#!/bin/bash

if [[ -z "${CI_COMMIT_MESSAGE}" ]]; then
    echo "$(git log -1 --pretty=%B)" > /tmp/.gitmessage
else
    echo "$CI_COMMIT_MESSAGE" > /tmp/.gitmessage
fi

conventional-pre-commit /tmp/.gitmessage
