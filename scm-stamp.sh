#!/usr/bin/env sh
echo "{\"url\": \"git:$GITURL\", \"revision\": \"$GITHEAD\", \"author\": \"$USER\", \"status\": \"$GITSTATUS\"}"  > scm-source.json
