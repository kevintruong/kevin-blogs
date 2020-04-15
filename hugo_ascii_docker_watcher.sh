#!/usr/bin/env bash

PARAMETERS=$@
echo "run hugo with $PARAMETERS"
docker run \
--rm -it \
--name hugo-ascii-runner \
--net host \
-p 1313:8080  \
--user $(whoami) \
-u=$(id -u $(whoami)):$(id -g $(whoami)) \
--volume ${PASSWD_FILE}:/etc/passwd \
--volume ${GROUP_FILE}:/etc/group \
--volume $HOME:$HOME \
--volume $(pwd):/documents \
hugo-ascii hugo ${PARAMETERS}
