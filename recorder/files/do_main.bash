#!/bin/bash

export PATH=/home/recusr/.local/python/bin:${PATH}

cd /home/recusr
python3.8 main.py

tail -f /dev/null

