#!/bin/zsh
npm run build
mv dist docker-build
version=$1
echo $version
docker build -t registry-docker.rightknights.com/devops/cmdb-front:$version ./docker-build/
docker push registry-docker.rightknights.com/devops/cmdb-front:$version
rm -rf docker-build/dist
