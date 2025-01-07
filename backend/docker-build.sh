#!/bin/zsh

version=$1
echo $version
docker build -t registry-docker.rightknights.com/devops/cmdb-back:$version .
docker push registry-docker.rightknights.com/devops/cmdb-back:$version
