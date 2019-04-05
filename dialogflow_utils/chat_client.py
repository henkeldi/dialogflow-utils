#!/usr/bin/python2
# -*- coding: utf-8 -*-
import random
import string
import sys

import dialogflow

import utils


class ChatClient(object):

    def __init__(self, session_id=None):
        if not utils.has_credentials():
            utils.print_missing_credential_notification()
            sys.exit(-1)
        project_id = utils.get_project_id_from_credentials()
        session_id = session_id if session_id else ChatClient.__generate_random_session_id__()
        self._session_client = dialogflow.SessionsClient()
        self._session = self._session_client.session_path(project_id,
                                                          session_id)

    @staticmethod
    def __generate_random_session_id__():
        return ''.join(
            [
                random.choice(string.ascii_uppercase + string.digits)
                for x
                in xrange(254)
            ])

    def detect_intent(self, query, language_code='de'):
        text_input = dialogflow.types.TextInput(text=query,
                                                language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        return self._session_client.detect_intent(session=self._session,
                                                  query_input=query_input)
