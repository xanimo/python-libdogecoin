#!/bin/bash

config_wslu() {
    if [ "$OS" == "windows" ]; then
        $USE_SUDO apt install gnupg2 apt-transport-https
        wget -O - https://pkg.wslutiliti.es/public.key | $USE_SUDO tee -a /etc/apt/trusted.gpg.d/wslu.asc

        # Debian 11
        echo "deb https://pkg.wslutiliti.es/debian bullseye main" | $USE_SUDO sudo tee -a /etc/apt/sources.list
    fi
}
