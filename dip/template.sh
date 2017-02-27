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
  git ls-remote $1 | grep "refs/heads/$(gitbranch)" > /dev/null 2>&1
}

gitdiff() {
  git diff $1/$2:$(remotepath)/docker-compose.yml ${PWD}/docker-compose.yml
}

check_remote() {
  if isgit; then
    if [ -n "$1" ]; then
      if remote_exists $1; then
        if ! branch_exists $1; then
          echo -e "${AMBER}The remote branch $1/$2 does not exist${NC}"
          return 1
        fi
      else
        echo -e "${AMBER}The configured remote $1 does not exist${NC}"
        return 1
      fi
    fi
  fi
}

set -e
cd $(dip config %%name%% home)
remote=$(dip config %%name%% remote)
branch=$(gitbranch)

# Check for divergence if git is configured
if check_remote ${remote} ${branch}; then
  if [ -n "$(gitdiff ${remote} ${branch})" ]; then
    echo -e "${AMBER}The local docker-compose.yml has diverged from remote $(dip config %%name%% remote)/$(gitbranch)\\n${NC}"
    gitdiff ${remote} ${branch}
    echo
    echo 'Sleeping for 10s'
    sleep 10
  fi
fi

# Run command
docker-compose run --rm %%name%% $*
