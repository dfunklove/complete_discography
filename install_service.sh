#!/bin/sh
cp complete-discography.service /etc/systemd/system
systemctl daemon-reload
systemctl start tikka.service
systemctl enable tikka.service
