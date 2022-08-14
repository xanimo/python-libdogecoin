#!/bin/bash
export LC_ALL=C
set -e -o pipefail

if command -v docker &> /dev/null
then
    sudo apt-get remove docker docker-engine docker.io containerd runc
fi

sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
    
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo usermod -aG docker $(whoami)
newgrp docker

sudo chmod 666 /var/run/docker.sock

PLATFORMS=linux/amd64,linux/arm64,linux/arm/v7,linux/386
if ! command -v docker buildx &> /dev/null
then
    VERSION="v0.8.2"
    URL_BASE=https://github.com/docker/buildx/releases/download/$VERSION
    FILENAME=buildx-$VERSION.$OS-$ARCH
    CHECKSUM=$URL_BASE/checksums.txt
    curl -O -L $URL_BASE/$FILENAME -o $FILENAME
    if [ $OS == "darwin" ]; then
        echo "95303b8b017d6805d35768244e66b41739745f81cb3677c0aefea231e484e227  buildx-v0.8.2.darwin-amd64" | sha256sum -c
    else
        curl -O -L $CHECKSUM -o checksums.txt
        grep $FILENAME checksums.txt | sha256sum -c
    fi
    chmod +x $FILENAME
    if [ -d "/usr/local/lib/docker" ]; then
        if [ ! -d "/usr/local/lib/docker/cli-plugins" ]; then
            sudo mkdir -p /usr/local/lib/docker/cli-plugins
        fi
    fi
    sudo mv $FILENAME /usr/local/lib/docker/cli-plugins/docker-buildx
    rm -rf checksums.txt
fi

docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
if ! docker buildx ls | grep -q container-builder; then
    docker buildx create --platform ${PLATFORMS} --name container-builder --use;
else
    docker buildx create --platform ${PLATFORMS} --name container-builder --node container-builder --use;
fi
