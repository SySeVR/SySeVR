#!/bin/bash
source /etc/profile
cd /home/SySeVR/joern-0.3.1
ant
echo "alias joern='java -jar $JOERN/bin/joern.jar'" >> ~/.bashrc
source ~/.bashrc
