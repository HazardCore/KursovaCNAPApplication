#!/bin/bash

# curl http://10.0.43.6:82/management-cli/iac_run.sh -o /usr/local/bin/iac_run && chmod +x /usr/local/bin/iac_run && iac_run -i -t

INSTALLATION_DIRECTORY=/app
GIT_BRANCH=master

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -i|--install)
      INSTALL=1
      shift # past argument
      ;;
    -g|--git-branch)
      GIT_BRANCH="$2"
      shift # past argument
      shift # past argument
      ;;
    -t|--test)
      PRODUCTION=0
      TEST=1
      shift # past argument
      ;;
    -p|--production)
      TEST=0
      PRODUCTION=1
      shift # past argument
      ;;
    -d|--daemon)
      DAEMON=1
      shift # past argument
      ;;
    -c|--catalog)
      INSTALLATION_DIRECTORY="$2"
      shift # past argument
      shift # past value
      ;;
    -b|--rebuild)
      BUILD=1
      shift # past argument
      shift # past value
      ;;
    -u|--update)
      curl http://10.0.43.6:82/management-cli/iac_run.sh -o /usr/local/bin/iac_run && chmod +x /usr/local/bin/iac_run
      shift # pt argument
      ;;
    --clear)
      rm -rf $INSTALLATION_DIRECTORY/data/app-media/*
      rm -rf $INSTALLATION_DIRECTORY/data/app-static/*
      rm -rf $INSTALLATION_DIRECTORY/data/app-socket/*
      rm -rf $INSTALLATION_DIRECTORY/data/db-data/*
      rm -rf $INSTALLATION_DIRECTORY/data/redis-data/*
      rm -rf $INSTALLATION_DIRECTORY/data/influx-data/*
      rm -rf $INSTALLATION_DIRECTORY/data/influx-config/*
      rm -rf $INSTALLATION_DIRECTORY/data/elasticsearch-data/*
      shift # past argument
      ;;
    --publish)
      docker-compose -f $INSTALLATION_DIRECTORY/docker-compose.yaml build

      docker tag app_app dir-repo-p-01.trembita.gov.ua:443/iac_application:latest
      docker tag app_celery dir-repo-p-01.trembita.gov.ua:443/iac_celery:latest
      docker tag app_celery_beat dir-repo-p-01.trembita.gov.ua:443/iac_celerybeat:latest
      docker tag app_db dir-repo-p-01.trembita.gov.ua:443/iac_database:latest

      docker push dir-repo-p-01.trembita.gov.ua:443/iac_application:latest
      docker push dir-repo-p-01.trembita.gov.ua:443/iac_celery:latest
      docker push dir-repo-p-01.trembita.gov.ua:443/iac_celerybeat:latest
      docker push dir-repo-p-01.trembita.gov.ua:443/iac_database:latest
      shift
      ;;
    -h|--help)
      echo "IAC RUNNING SCRIPT. Use following parameters to perform a command."
      echo "    -i|--install      INSTALL INFRASTRUCTURE"
      echo "    -t|--test         RUN AS TEST"
      echo "    -p|--production   RUN AS PRODUCTION"
      echo "    -b|--rebuild      REBUILD CONTAINERS FOR TEST/PRODUCTION"
      echo "    -d|--daemon       RUN DOCKER-COMPOSE IN DAEMON MODE"
.      echo "    -c|--catalog      INSTALLATION FOLDER PATH"
      echo "    -g|--git-branch   SELECT GIT BRANCH TO INSTALL FROM"
      echo "    --clear           REMOVE ALL CONTENTS IN STATIC DIRECTORY"
      echo "    --update          UPDATE CURRENT SCRIPT LIBRARY"
      exit 0
      shift # past argument
      ;;
    *)    # unknown option
      shift # past argument
      ;;
  esac
done

if [[ "$INSTALL" -eq "1" ]]; then
    apt update
    apt install -y ansible

    mkdir -p $INSTALLATION_DIRECTORY
    cd $INSTALLATION_DIRECTORY
    # git -C $INSTALLATION_DIRECTORY init
    # git -C $INSTALLATION_DIRECTORY remote add iac https://gitlab.dir.gov.ua/developer-team/iac-docker.git
    git -C $INSTALLATION_DIRECTORY config --global user.email "devops@dir.gov.ua"
    git -C $INSTALLATION_DIRECTORY config --global user.name "DevOps"
    # git -C $INSTALLATION_DIRECTORY pull iac $GIT_BRANCH
    git clone https://gitlab.diia.org.ua/developer-team/iac-docker.git -c http.sslVerify=false -o iac -b $GIT_BRANCH $INSTALLATION_DIRECTORY
    git -C $INSTALLATION_DIRECTORY config credential.helper store
    git config core.fileMode false

    if [[ "$INSTALLATION_DIRECTORY" = "/app" ]]; then
      ansible-playbook ansible/install.yaml
    else
      ansible-playbook ansible/install.yaml --extra-vars "APPLICATION_DIRECTORY_PATH=$INSTALLATION_DIRECTORY"
    fi

    # chmod -R 0644 $INSTALLATION_DIRECTORY
fi

if [[ "$BUILD" -eq "1" ]]; then
    if [[ "$TEST" -eq "1" ]]; then
        docker-compose -f $INSTALLATION_DIRECTORY/docker-compose.yaml build
    else 
      if [[ "$PRODUCTION" -eq "1" ]]; then
          docker-compose -f $INSTALLATION_DIRECTORY/production.yaml build
      else
          docker-compose -f $INSTALLATION_DIRECTORY/production.yaml build
      fi
    fi
fi

if [ ! -f "$INSTALLATION_DIRECTORY/django/.env" ]; then
  echo "Create .env file in ./django directory before running a project!"
  echo "Ask .env developer for example file"
  exit 1
fi

if [[ "$TEST" -eq "1" ]]; then
    if [[ "$DAEMON" -eq "1" ]]; then
        docker-compose -f $INSTALLATION_DIRECTORY/docker-compose.yaml up -d
    else
        docker-compose -f $INSTALLATION_DIRECTORY/docker-compose.yaml up
    fi
fi

if [[ "$PRODUCTION" -eq "1" ]]; then
    if [[ "$DAEMON" -eq "1" ]]; then
        docker-compose -f $INSTALLATION_DIRECTORY/production.yaml up -d
    else
        docker-compose -f $INSTALLATION_DIRECTORY/production.yaml up
    fi
fi
