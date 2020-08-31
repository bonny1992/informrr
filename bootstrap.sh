#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y python3-pip python3-dev

if ! [ -L /app ]; then
  sudo rm -rf /app
  ln -fs /vagrant/app /app
fi

cd /app
sudo pip3 install -r requirements.txt
sudo pip3 install pyngrok