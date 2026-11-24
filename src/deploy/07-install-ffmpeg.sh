#!/bin/bash
set -e
cd /opt
if [ ! -x /opt/ffmpeg/ffmpeg ]; then
  echo "下载静态 ffmpeg ..."
  curl -fsSL -o /tmp/ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
  mkdir -p /tmp/ffx && tar -xJf /tmp/ffmpeg.tar.xz -C /tmp/ffx
  rm -rf /opt/ffmpeg && mv /tmp/ffx/ffmpeg-*-static /opt/ffmpeg
  rm -f /tmp/ffmpeg.tar.xz
fi
/opt/ffmpeg/ffmpeg -version | head -2
ls -la /opt/ffmpeg/ffmpeg
