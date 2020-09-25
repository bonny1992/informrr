#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y python3.8-pip python3.8-dev

if ! [ -L /app ]; then
  sudo rm -rf /app
  ln -fs /vagrant/app /app
fi

if ! [ -L /data ]; then
  sudo chown -R 1000:1000 /data
else
  sudo mkdir /data
  sudo chown -R 1000:1000 /data
fi


cd /app
sudo pip3 install -r requirements.txt
sudo pip3 install pyngrok






echo "Run these in tmux sessions:"
echo "** tmux new -d -s ngrok ngrok http 5445 **"
echo "** tmux new -d -s webhook python3.8 /app/main.py **"
echo "** tmux new -d -s notify python3.8 /app/notificator.py **"