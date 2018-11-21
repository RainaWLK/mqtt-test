/*
Copyright (c) 2009-2014 Roger Light <roger@atchoo.org>

All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
and Eclipse Distribution License v1.0 which accompany this distribution.
 
The Eclipse Public License is available at
   http://www.eclipse.org/legal/epl-v10.html
and the Eclipse Distribution License is available at
  http://www.eclipse.org/org/documents/edl-v10.php.
 
Contributors:
   Roger Light - initial implementation and documentation.
*/
#include <json.h>

#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef WIN32
#include <unistd.h>
#else
#include <process.h>
#include <winsock2.h>
#define snprintf sprintf_s
#endif

#include <mosquitto.h>
#include "client_shared.h"

bool process_messages = true;
int msg_count = 0;

char resp[384];
char dev_name[24];
char dev_mac[24];
int dev_gps_lat, dev_gps_lng;

int qos = 1;
int retain = 1;
char pub_topic[64];
int pub_len;
char task_id[40];

/*
void token_backslash(char* orig, char* token)
{
	strncpy(token, orig, strlen(orig));

	memmove( token + 6 + 1, token + 6, 61 - (6+1) );
	token[6] = '\\';
	memmove( token + 3 + 1, token + 3, 62 - (3+1) );
	token[3] = '\\';
	memmove( token + 0 + 1, token + 0, 63 - (0+1) );
	token[0] = '\\';

	return 0;
}
*/

/* add backslash before $, used for shell environment */
void add_backslash(char* orig, char* token)
{
        char *location, *ptr;

	strncpy(token, orig, strlen(orig));
        ptr = token;
        while( (location=strstr(ptr, "$")) )
        {
                memmove( location + 1, location, strlen(location)+1 );
                location[0] = '\\';     
                ptr = location + 2;     // skip \$
        }
}


void my_message_callback(struct mosquitto *mosq, void *obj, const struct mosquitto_message *message)
{
	struct mosq_config *cfg;
	int i;
	bool res;

	int rc;
	int mid_sent = 0;
	struct json_object *j_root, *j_resource, *j_task_id;
	struct json_object *j_data, *j_file, *j_url, *j_headers, *j_token;
	static int sp_count = 0;	// counter of /system/properties

	if(process_messages == false) return;

	assert(obj);
	cfg = (struct mosq_config *)obj;

	if(message->retain && cfg->no_retain) return;
	if(cfg->filter_outs){
		for(i=0; i<cfg->filter_out_count; i++){
			mosquitto_topic_matches_sub(cfg->filter_outs[i], message->topic, &res);
			if(res) return;
		}
	}

	if(!message->payloadlen && cfg->eol){
		printf("%s (null)\n", message->topic);
		fflush(stdout);
	}


	printf("\n%s ", message->topic);
	fwrite(message->payload, 1, message->payloadlen, stdout);
	printf("\n");
	fflush(stdout);

	j_root = json_tokener_parse(message->payload);
	j_task_id = json_object_object_get(j_root, "task_id");
	j_resource = json_object_object_get(j_root, "resource");

	if( strcmp(json_object_get_string(j_resource), "/system/properties") == 0 )
	{
		printf("\nget /system/properties (%d)\n", ++sp_count);
		snprintf(resp, 384, "{ \"code\": 200, \"resource\": \"/system/properties\", \"task_id\": \"%s\", \"id\": 190760, \"sign\": [ \"status\" ], \"data\": { \"aliasName\": \"%s\", \"gps\": { \"lat\": %d, \"lng\": %d } }, \"method\": \"get\" }",
			json_object_get_string(j_task_id),
			dev_name,
			dev_gps_lat, dev_gps_lng);
	}
	else if( strcmp(json_object_get_string(j_resource), "/system/import") == 0 )
	{
		snprintf(resp, 384, "{ \"code\": 200, \"resource\": \"/system/import\", \"task_id\": \"%s\", \"method\": \"put\", \"sign\": [ \"import-export\" ], \"data\": {}, \"id\": 190760 }",
			json_object_get_string(j_task_id));
	}
	else if( strcmp(json_object_get_string(j_resource), "/system/firmware") == 0 )
	{
		char token[64] = {0};
		char url[80] = {0};

		j_data = json_object_object_get(j_root, "data");
		j_file = json_object_object_get(j_data, "file");
		j_url = json_object_object_get(j_file, "url");
		j_headers = json_object_object_get(j_file, "headers");
		j_token = json_object_object_get(j_headers, "MX-API-TOKEN");

		add_backslash(json_object_get_string(j_token), token);

		// execute wget to download firmware
		snprintf(resp, 384, "wget --header \"mx-api-token:%s\" \"%s\" -P /tmp/%s", token, json_object_get_string(j_url), cfg->psk+58);
		//snprintf(resp, 384, "wget --header \"mx-api-token:%s\" \"%s\" -O /dev/null", token, url);
		system(resp);
		snprintf(resp, 384, "{ \"code\": 200, \"resource\": \"/system/firmware\", \"task_id\": \"%s\", \"id\": 190760, \"sign\": [ \"firmware\" ], \"data\": {}, \"method\": \"post\" }",
			json_object_get_string(j_task_id));
	}
	else if( strcmp(json_object_get_string(j_resource), "/system/serial") == 0 )
	{
		snprintf(resp, 384, "{ \"code\": 200, \"resource\": \"/system/serial\", \"task_id\": \"%s\", \"id\": 190760, \"sign\": [ \"serial\" ], \"data\": [ { \"devDisplayName\": \"PORT 1\", \"id\": 1, \"dev\": \"/dev/ttyM0\", \"mode\": \"rs232\" } ], \"method\": \"get\" }",
			json_object_get_string(j_task_id));
	}
	else
	{
		printf("Undefined request: %s\n", (char*)message->payload);
	}

	//printf("PUB: %s\n", resp);
	retain = 0;
	pub_len = strlen(resp);
	snprintf(pub_topic, 64, "$ThingsPro/devices/%s/client", cfg->id);
	rc = mosquitto_publish(mosq, &mid_sent, pub_topic, pub_len, resp, qos, retain);
	if(rc) {
		fprintf(stderr, "Error: Publish response(1) failed.\n");
	}

	if(cfg->msg_count>0){
		msg_count++;
		if(cfg->msg_count == msg_count){
			process_messages = false;
			mosquitto_disconnect(mosq);
		}
	}
}

void my_connect_callback(struct mosquitto *mosq, void *obj, int result)
{
	int i;
	struct mosq_config *cfg;

	int rc2;
	int mid_sent = 0;
	int buf_len = 4;
	char *buf;

	assert(obj);
	cfg = (struct mosq_config *)obj;

	buf = malloc(buf_len);
	bzero(buf, buf_len);
	strcpy(buf, "1");
	pub_len = strlen(buf);
	snprintf(pub_topic, 64, "$ThingsPro/devices/%s/status", cfg->id);
	rc2 = mosquitto_publish(mosq, &mid_sent, pub_topic, pub_len, buf, qos, retain);
	if(rc2) {
		if(!cfg->quiet) fprintf(stderr, "Error: Publish notification failed.\n");
	}

	if(!result){
		for(i=0; i<cfg->topic_count; i++){
			mosquitto_subscribe(mosq, NULL, cfg->topics[i], cfg->qos);
		}
	}else{
		if(result && !cfg->quiet){
			fprintf(stderr, "%s\n", mosquitto_connack_string(result));
		}
	}
	free(buf);
}

void my_subscribe_callback(struct mosquitto *mosq, void *obj, int mid, int qos_count, const int *granted_qos)
{
	int i;
	struct mosq_config *cfg;

	assert(obj);
	cfg = (struct mosq_config *)obj;

	if(!cfg->quiet) printf("Subscribed (mid: %d): %d", mid, granted_qos[0]);
	for(i=1; i<qos_count; i++){
		if(!cfg->quiet) printf(", %d", granted_qos[i]);
	}
	if(!cfg->quiet) printf("\n");
}

void my_log_callback(struct mosquitto *mosq, void *obj, int level, const char *str)
{
	printf("%s\n", str);
}

void print_usage(void)
{
	int major, minor, revision;

	mosquitto_lib_version(&major, &minor, &revision);
	printf("mosquitto_sub is a simple mqtt client that will subscribe to a single topic and print all messages it receives.\n");
	printf("mosquitto_sub version %s running on libmosquitto %d.%d.%d.\n\n", VERSION, major, minor, revision);
	printf("Usage: mosquitto_sub [-c] [-h host] [-k keepalive] [-p port] [-q qos] [-R] -t topic ...\n");
	printf("                     [-C msg_count] [-T filter_out]\n");
#ifdef WITH_SRV
	printf("                     [-A bind_address] [-S]\n");
#else
	printf("                     [-A bind_address]\n");
#endif
	printf("                     [-i id] [-I id_prefix]\n");
	printf("                     [-d] [-N] [--quiet] [-v]\n");
	printf("                     [-u username [-P password]]\n");
	printf("                     [--will-topic [--will-payload payload] [--will-qos qos] [--will-retain]]\n");
#ifdef WITH_TLS
	printf("                     [{--cafile file | --capath dir} [--cert file] [--key file]\n");
	printf("                      [--ciphers ciphers] [--insecure]]\n");
#ifdef WITH_TLS_PSK
	printf("                     [--psk hex-key --psk-identity identity [--ciphers ciphers]]\n");
#endif
#endif
#ifdef WITH_SOCKS
	printf("                     [--proxy socks-url]\n");
#endif
	printf("       mosquitto_sub --help\n\n");
	printf(" -A : bind the outgoing socket to this host/ip address. Use to control which interface\n");
	printf("      the client communicates over.\n");
	printf(" -c : disable 'clean session' (store subscription and pending messages when client disconnects).\n");
	printf(" -C : disconnect and exit after receiving the 'msg_count' messages.\n");
	printf(" -d : enable debug messages.\n");
	printf(" -h : mqtt host to connect to. Defaults to localhost.\n");
	printf(" -i : id to use for this client. Defaults to mosquitto_sub_ appended with the process id.\n");
	printf(" -I : define the client id as id_prefix appended with the process id. Useful for when the\n");
	printf("      broker is using the clientid_prefixes option.\n");
	printf(" -k : keep alive in seconds for this client. Defaults to 60.\n");
	printf(" -N : do not add an end of line character when printing the payload.\n");
	printf(" -p : network port to connect to. Defaults to 1883.\n");
	printf(" -P : provide a password (requires MQTT 3.1 broker)\n");
	printf(" -q : quality of service level to use for the subscription. Defaults to 0.\n");
	printf(" -R : do not print stale messages (those with retain set).\n");
#ifdef WITH_SRV
	printf(" -S : use SRV lookups to determine which host to connect to.\n");
#endif
	printf(" -t : mqtt topic to subscribe to. May be repeated multiple times.\n");
	printf(" -T : topic string to filter out of results. May be repeated.\n");
	printf(" -u : provide a username (requires MQTT 3.1 broker)\n");
	printf(" -v : print published messages verbosely.\n");
	printf(" -V : specify the version of the MQTT protocol to use when connecting.\n");
	printf("      Can be mqttv31 or mqttv311. Defaults to mqttv31.\n");
	printf(" --help : display this message.\n");
	printf(" --quiet : don't print error messages.\n");
	printf(" --will-payload : payload for the client Will, which is sent by the broker in case of\n");
	printf("                  unexpected disconnection. If not given and will-topic is set, a zero\n");
	printf("                  length message will be sent.\n");
	printf(" --will-qos : QoS level for the client Will.\n");
	printf(" --will-retain : if given, make the client Will retained.\n");
	printf(" --will-topic : the topic on which to publish the client Will.\n");
#ifdef WITH_TLS
	printf(" --cafile : path to a file containing trusted CA certificates to enable encrypted\n");
	printf("            certificate based communication.\n");
	printf(" --capath : path to a directory containing trusted CA certificates to enable encrypted\n");
	printf("            communication.\n");
	printf(" --cert : client certificate for authentication, if required by server.\n");
	printf(" --key : client private key for authentication, if required by server.\n");
	printf(" --ciphers : openssl compatible list of TLS ciphers to support.\n");
	printf(" --tls-version : TLS protocol version, can be one of tlsv1.2 tlsv1.1 or tlsv1.\n");
	printf("                 Defaults to tlsv1.2 if available.\n");
	printf(" --insecure : do not check that the server certificate hostname matches the remote\n");
	printf("              hostname. Using this option means that you cannot be sure that the\n");
	printf("              remote host is the server you wish to connect to and so is insecure.\n");
	printf("              Do not use this option in a production environment.\n");
#ifdef WITH_TLS_PSK
	printf(" --psk : pre-shared-key in hexadecimal (no leading 0x) to enable TLS-PSK mode.\n");
	printf(" --psk-identity : client identity string for TLS-PSK mode.\n");
#endif
#endif
#ifdef WITH_SOCKS
	printf(" --proxy : SOCKS5 proxy URL of the form:\n");
	printf("           socks5h://[username[:password]@]hostname[:port]\n");
	printf("           Only \"none\" and \"username\" authentication is supported.\n");
#endif
	printf("\nSee http://mosquitto.org/ for more information.\n\n");
}

int main(int argc, char *argv[])
{
	struct mosq_config cfg;
	struct mosquitto *mosq = NULL;
	int rc;
	
	rc = client_config_load(&cfg, CLIENT_SUB, argc, argv);
	if(rc){
		client_config_cleanup(&cfg);
		if(rc == 2){
			/* --help */
			print_usage();
		}else{
			fprintf(stderr, "\nUse 'mosquitto_sub --help' to see usage.\n");
		}
		return 1;
	}

	mosquitto_lib_init();

	if(client_id_generate(&cfg, "mosqsub")){
		return 1;
	}

	mosq = mosquitto_new(cfg.id, cfg.clean_session, &cfg);
	if(!mosq){
		switch(errno){
			case ENOMEM:
				if(!cfg.quiet) fprintf(stderr, "Error: Out of memory.\n");
				break;
			case EINVAL:
				if(!cfg.quiet) fprintf(stderr, "Error: Invalid id and/or clean_session.\n");
				break;
		}
		mosquitto_lib_cleanup();
		return 1;
	}
	if(client_opts_set(mosq, &cfg)){
		return 1;
	}
	if(cfg.debug){
		mosquitto_log_callback_set(mosq, my_log_callback);
		mosquitto_subscribe_callback_set(mosq, my_subscribe_callback);
	}
	mosquitto_connect_callback_set(mosq, my_connect_callback);
	mosquitto_message_callback_set(mosq, my_message_callback);


	rc = client_connect(mosq, &cfg);
	if(rc) {
		printf("# %s: client_connect fail\n", dev_name);
		return rc;
	}


	//XXX device name and MAC
	snprintf(dev_name, 24, "%s-%s", "UC-8112-LX", cfg.psk+58);
	snprintf(dev_mac, 24, "%s:%c%c:%c%c", "00:90:E8",
			cfg.psk[60], cfg.psk[61], cfg.psk[62], cfg.psk[63]);

	dev_gps_lat = -80 + (int)strtol(cfg.psk+58, NULL, 16)/361;
	dev_gps_lng = -180 + (int)strtol(cfg.psk+58, NULL, 16)%361;


	rc = mosquitto_loop_forever(mosq, -1, 1);
	/*do {
		rc = mosquitto_loop_forever(mosq, -1, 1);
		sleep(5);
	} while( rc );
	*/

	mosquitto_destroy(mosq);
	mosquitto_lib_cleanup();

	if(cfg.msg_count>0 && rc == MOSQ_ERR_NO_CONN){
		rc = 0;
	}
	if(rc){
		fprintf(stderr, "Error: %s\n", mosquitto_strerror(rc));
	}
	return rc;
}

