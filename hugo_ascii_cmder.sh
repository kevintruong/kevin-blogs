#!/usr/bin/env bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function hugo_ascii_docker_run() {
    PARAMETERS=$@
    PASSWD_FILE=/etc/passwd
    GROUP_FILE=/etc/group
    echo "run hugo with $PARAMETERS"
    docker run \
    -d \
    -it \
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
    hugo_ascii_docker_run "server -D"
    while [[ true ]]
    do
        files=`find $1 -type f -newermt "$2 seconds ago"`
        if [[ ${files} != "" ]] ; then
            echo "${files} file changed, let update"
            docker stop hugo-ascii-runner
            sleep 1
            hugo_ascii_docker_run -D
            sleep 1
            cp -rf ${ROOT_DIR}/assets ${ROOT_DIR}/static/
            sleep 1
            hugo_ascii_docker_run "server -D"
        fi
        sleep 3
    done
}

function usage
{
    echo "usage: hugo_ascii_cmder -w your_dir_path -d diff_time : for monitoring your directory and re-update local hugo web"
    echo "usage: hugo_ascii_cmder -r 'hugo command here' : for monitoring your directory and re-update local hugo web"

    echo "   ";
    echo "  -w | --watch            : your dir to monitor";
    echo "  -dt| --difftime         : difftime";
    echo "  -r | --run              : run command";
    echo "  -h | --help             : Help";
}

function parse_args
{
  # positional args
  args=()

  # named args
  while [[ "$1" != "" ]]; do
      case "$1" in
          -w | --watch )                watch_dir="$2";             shift;;
          -dt | --difftime )            diff_time="$2";     shift;;
          -r | --runcmd )               run_cmd="$2";      shift;;
          -h | --help )                 usage;                   exit;; # quit and show usage
          * )                           args+=("$1")             # if no match, add it to the positional args
      esac
      shift # move to next kv pair
  done

  # restore positional args
  set -- "${args[@]}"

}


function run
{
  parse_args "$@"
   # validate required args

  echo "you passed in...\n"
  echo "named arg: watchdir: $watch_dir"
  echo "named arg: difftime : $diff_time"
  echo "named arg: runcmd: $run_cmd"

  if [[ ! -z "${watch_dir}"  &&  ! -z "${run_cmd}" ]]; then
    echo " -r and -w can not be combined"
    usage
    exit 1
  fi

  if [[ ! -z "${watch_dir}" ]]; then
    echo "run hugo watch content dir"
    if [[ -z "${diff_time}" ]]; then
        diff_time=3
    fi
    watch ${watch_dir} ${diff_time}
    return
  fi

  if [[ ! -z "${run_cmd}" ]]; then
    echo "run hugo command "
    hugo_ascii_docker_run ${run_cmd}
  fi
}

run "$@";
