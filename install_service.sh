#!/bin/sh
cp complete-discography.service /etc/systemd/system
systemctl daemon-reload
systemctl start complete-discography.service
systemctl enable complete-discography.service
