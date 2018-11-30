#!/bin/bash
$(aws ecr get-login --no-include-email --region us-west-1 --profile moxasys)
docker build -t cg_emu .
docker tag cg_emu:latest 656337455073.dkr.ecr.us-west-1.amazonaws.com/cg_emu:latest
docker push 656337455073.dkr.ecr.us-west-1.amazonaws.com/cg_emu:latest

#deploy
#echo 'update task definition...'
#aws ecs register-task-definition --cli-input-json file://$taskDefinitionFile --region us-west-2

#echo 'update our service with that last task..'
#aws ecs update-service --cluster CGEmu --service cgemu --task-definition cgemu --force-new-deployment --region us-west-1

#echo '(for development only) Replace to new Task..'
#TASK_ID=$(aws ecs list-tasks --cluster CGEmu | grep 'arn:' | sed 's/\"//g' | sed 's/^.*arn/arn/')
#if [ "$TASK_ID" != "" ]; then
#  aws ecs stop-task --cluster CGEmu --task $TASK_ID --reason 'auto deploy'
#else
#  echo 'no task to stop'
#fi