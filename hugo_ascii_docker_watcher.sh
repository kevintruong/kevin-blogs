#!/usr/bin/env bash


ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function hugo_ascii_docker_run() {
    PARAMETERS=$@
    PASSWD_FILE=/etc/passwd
    GROUP_FILE=/etc/group
    echo "run hugo with $PARAMETERS"
    docker run \
    -d \
    --rm \
    --name hugo-ascii-runner \
    --net host \
    --user $(whoami) \
    -u=$(id -u $(whoami)):$(id -g $(whoami)) \
    --volume ${PASSWD_FILE}:/etc/passwd \
    --volume ${GROUP_FILE}:/etc/group \
    --volume $HOME:$HOME \
    --volume $(pwd):/documents \
    hugo-ascii hugo ${PARAMETERS}
}

watch() {
    echo watching folder $1/ every $2 secs.
    while [[ true ]]
    do
        files=`find $1 -type f -newermt '3 seconds ago'`
        if [[ ${files} != "" ]] ; then
            docker stop hugo-ascii-runner
            sleep 1
            hugo_ascii_docker_run -D
            sleep 2
            cp -rf ${ROOT_DIR}/assets ${ROOT_DIR}/static/
            sleep 2
            hugo_ascii_docker_run "server -D"
        fi
        sleep 3
    done
}

watch $ROOT_DIR/content 3
