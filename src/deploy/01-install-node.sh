#!/bin/bash
set -e
cd /opt
if [ ! -d node22 ]; then
  curl -fsSLO https://mirrors.cloud.tencent.com/nodejs-release/v22.14.0/node-v22.14.0-linux-x64.tar.xz
  tar xf node-v22.14.0-linux-x64.tar.xz
  mv node-v22.14.0-linux-x64 node22
  rm -f node-v22.14.0-linux-x64.tar.xz
fi
/opt/node22/bin/node -v
/opt/node22/bin/node -e 'const {DatabaseSync}=require("node:sqlite"); const d=new DatabaseSync(":memory:"); d.exec("create table t(a)"); console.log("node:sqlite OK");'
mkdir -p /opt/egoops/relay
