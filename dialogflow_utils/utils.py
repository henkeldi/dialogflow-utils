#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import json
import os


GOOGLE_APPLICATION_CREDENTIALS_ENVIRONMENT_NAME = "GOOGLE_APPLICATION_CREDENTIALS"


def has_credentials():
    return GOOGLE_APPLICATION_CREDENTIALS_ENVIRONMENT_NAME in os.environ


def print_missing_credential_notification():
    print 'Please set up your google application credentials:'
    print
    print 'export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"'
    print
    print 'More info: https://cloud.google.com/text-to-speech/docs/reference/libraries#setting_up_authentication'


def get_project_id_from_credentials():
    credentials = os.environ[GOOGLE_APPLICATION_CREDENTIALS_ENVIRONMENT_NAME]
    with open(credentials, 'r') as f:
        data = json.load(f)
    return data['project_id']