#!/bin/bash

AMBER='\033[0;33m'
NC='\033[0m'

gitbranch() {
  git branch | grep \* | cut -d ' ' -f2
}

gitremotes() {
  git remote --verbose | cut -f1 | uniq
}

gitroot() {
  realpath "${PWD}/$(git rev-parse --show-cdup)"
}

remotepath() {
  realpath --relative-to "$(gitroot)" ${PWD}
}

isgit() {
  git rev-parse --is-inside-work-tree > /dev/null 2>&1
}

remote_exists() {
  gitremotes | grep $1 > /dev/null 2>&1
}

branch_exists() {
  git ls-remote $1 | grep "refs/heads/$2" > /dev/null 2>&1
}

compose_exists() {
  git cat-file -e $1/$2:$(remotepath)/docker-compose.yml > /dev/null 2>&1
}

gitdiff() {
  git --no-pager diff $1/$2:$(remotepath)/docker-compose.yml ${PWD}/docker-compose.yml
}

check_remote() {
  if isgit; then
    if remote_exists $1; then
      if ! branch_exists $1 $2; then
        echo -e "${AMBER}The remote branch $1/$2 does not exist${NC}"
        return 1
      elif ! compose_exists $1 $2; then
        echo -e "${AMBER}The remote branch $1/$2 does not contain a docker-compose.yml${NC}"
        return 1
      fi
    else
      echo -e "${AMBER}The configured remote $1 does not exist${NC}"
      return 1
    fi
  fi
}

# Ensure `realpath` is installed
if [ -z "$(which realpath)" ]; then
  echo 'Please install realpath (`brew install coreutils` on macOS)'
  exit 1
fi

# Ensure `dip` is installed
if [ -z "$(which dip)" ]; then
  echo 'dip is not installed, please reinstall'
  exit 1
elif [ -z "$(dip config %%name%%)" ]; then
  echo '%%name%% is not configured in dip, please reinstall'
  exit 1
fi

cd $(dip config %%name%% home)
remote=$(dip config %%name%% remote)
branch=$(dip config %%name%% branch || gitbranch)

# Check for divergence if git is configured
if [ -n "${remote}" ]; then
  if check_remote ${remote} ${branch}; then
    if [ -n "$(gitdiff ${remote} ${branch})" ]; then
      echo -e "${AMBER}The local docker-compose.yml has diverged from remote ${remote}/${branch}\\n${NC}"
      gitdiff ${remote} ${branch}
      echo
      echo 'Sleeping for 10s'
      sleep 10
    fi
  fi
fi

# Run command
env=$(dip env %%name%%)
docker-compose run --rm ${env} %%name%% $*
