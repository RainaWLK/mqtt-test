#include "config.h"

#include <json-c/json.h>

#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#ifndef WIN32
#include <unistd.h>
#else
#include <process.h>
#include <winsock2.h>
#define snprintf sprintf_s
#endif

#ifdef __APPLE__
#  include <sys/time.h>
#endif

#include <mosquitto.h>
#include "client_shared.h"

#define PAYLOAD_SIZE 384


void getProperties(char *resp, struct json_object *j_task_id, struct mosq_config *cfg) {
  //printf("\nget /system/properties (%d)\n", ++sp_count);

	//XXX device name and MAC
  char dev_name[24];
  char dev_mac[24];
  int dev_gps_lat=0, dev_gps_lng=0;
	snprintf(dev_name, 24, "%s-%s", "UC-8112-LX", cfg->psk+58);
	snprintf(dev_mac, 24, "%s:%c%c:%c%c", "00:90:E8",
			cfg->psk[60], cfg->psk[61], cfg->psk[62], cfg->psk[63]);

	dev_gps_lat = -80 + (int)strtol(cfg->psk+58, NULL, 16)/361;
	dev_gps_lng = -180 + (int)strtol(cfg->psk+58, NULL, 16)%361;


  snprintf(resp, PAYLOAD_SIZE, 
    "{ \"code\": 200, \"resource\": \"/system/properties\", \"task_id\": \"%s\", \"id\": 190760, \"sign\": [ \"status\" ], \"data\": { \"aliasName\": \"%s\", \"gps\": { \"lat\": %d, \"lng\": %d } }, \"method\": \"get\" }",
    json_object_get_string(j_task_id),
    dev_name,
    dev_gps_lat,
    dev_gps_lng);

  return;
}

void getImport(char *resp, struct json_object *j_task_id) {
	snprintf(resp, PAYLOAD_SIZE,
    "{ \"code\": 200, \"resource\": \"/system/import\", \"task_id\": \"%s\", \"method\": \"put\", \"sign\": [ \"import-export\" ], \"data\": {}, \"id\": 190760 }",
		json_object_get_string(j_task_id));

  return;
}

void getSerial(char *resp, struct json_object *j_task_id) {
	snprintf(resp, PAYLOAD_SIZE,
    "{ \"code\": 200, \"resource\": \"/system/serial\", \"task_id\": \"%s\", \"id\": 190760, \"sign\": [ \"serial\" ], \"data\": [ { \"devDisplayName\": \"PORT 1\", \"id\": 1, \"dev\": \"/dev/ttyM0\", \"mode\": \"rs232\" } ], \"method\": \"get\" }",
		json_object_get_string(j_task_id));
  return;
}

void getFirmware(char *resp, struct json_object *j_task_id) {

}


void sub_action(struct mosquitto *mosq, struct mosq_config *cfg, const struct mosquitto_message *message) {
  printf("sub_action\n");

	printf("\n%s ", message->topic);
	fwrite(message->payload, 1, message->payloadlen, stdout);
	printf("\n");
	fflush(stdout);

  char *resp = calloc(PAYLOAD_SIZE, sizeof(char));
  //char dev_name[24];
  //char dev_mac[24];
  //int dev_gps_lat, dev_gps_lng;

	int mid_sent = 0;
	struct json_object *j_root, *j_resource, *j_task_id;
	struct json_object *j_data, *j_file, *j_url, *j_headers, *j_token;
	//static int sp_count = 0;	// counter of /system/properties

  j_root = json_tokener_parse(message->payload);
	json_object_object_get_ex(j_root, "task_id", &j_task_id);
	json_object_object_get_ex(j_root, "resource", &j_resource);

  const char *resource = json_object_get_string(j_resource);

	if( strcmp(resource, "/system/properties") == 0 )
	{
    getProperties(resp, j_task_id, cfg);
	}
	else if( strcmp(resource, "/system/import") == 0 )
	{
    getImport(resp, j_task_id);
	}
	else if( strcmp(resource, "/system/firmware") == 0 )
	{
		//char token[64] = {0};
		//char url[80] = {0};

		json_object_object_get_ex(j_root, "data", &j_data);
		json_object_object_get_ex(j_data, "file", &j_file);
		json_object_object_get_ex(j_file, "url", &j_url);
		json_object_object_get_ex(j_file, "headers", &j_headers);
		json_object_object_get_ex(j_headers, "MX-API-TOKEN", &j_token);

		/*add_backslash(json_object_get_string(j_token), token);

		// execute wget to download firmware
		snprintf(resp, 384, "wget --header \"mx-api-token:%s\" \"%s\" -P /tmp/%s", token, json_object_get_string(j_url), cfg->psk+58);
		//snprintf(resp, 384, "wget --header \"mx-api-token:%s\" \"%s\" -O /dev/null", token, url);
		system(resp);
		snprintf(resp, 384, "{ \"code\": 200, \"resource\": \"/system/firmware\", \"task_id\": \"%s\", \"id\": 190760, \"sign\": [ \"firmware\" ], \"data\": {}, \"method\": \"post\" }",
			json_object_get_string(j_task_id));*/
	}
	else if( strcmp(resource, "/system/serial") == 0 )
	{
    getSerial(resp, j_task_id);
	}
	else
	{
		printf("Undefined request: %s\n", (char*)message->payload);
	}

	printf("PUB: %s\n", resp);
  char pub_topic[64];
	snprintf(pub_topic, sizeof(pub_topic), "$ThingsPro/devices/%s/client", cfg->id);
	int rc = mosquitto_publish(mosq, &mid_sent, pub_topic, strlen(resp), resp, cfg->qos, cfg->retain);
	if(rc) {
		fprintf(stderr, "Error: Publish response(1) failed.\n");
	}

  free(resp);
}

void send_online_event(struct mosquitto *mosq, struct mosq_config *cfg) {
  char pub_topic[64];
	int mid_sent = 0;
	int buf_len = 4;
	char *buf;

  //payload
	buf = malloc(buf_len);
	bzero(buf, buf_len);
	strcpy(buf, "1");

  //topic
	snprintf(pub_topic, 64, "$ThingsPro/devices/%s/status", cfg->id);
	printf("send online event:%s\n", pub_topic);
	
  //publish
  int rc = mosquitto_publish(mosq, &mid_sent, pub_topic, strlen(buf), buf, cfg->qos, cfg->retain);
	if(rc) {
		if(!cfg->quiet) fprintf(stderr, "Error: Publish notification failed.\n");
	}

  return;
}

int connected = 0;

void sub_connect_action(struct mosquitto *mosq, struct mosq_config *cfg) {
	if(connected == 0) {
		connected = 1;
  	send_online_event(mosq, cfg);
	}
  return;
}

void sub_disconnect_action() {
	connected = 0;
  return;
}