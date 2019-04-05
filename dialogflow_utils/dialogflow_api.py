#!/usr/bin/python2
# -*- coding: utf-8 -*-
import sys
import logging as log
import re
from contextlib import contextmanager

import dialogflow

import utils

'''
References:

** http://dialogflow-python-client-v2.readthedocs.io
/en/latest/?#using-dialogflow

# Google Apis python github
** https://github.com/googleapis/dialogflow-python-client-v2
/blob/master/samples/intent_management.py


# Dialogflow Reference Manual
** https://cloud.google.com/dialogflow-enterprise
/docs/reference/rpc/google.cloud.dialogflow.v2
'''

log.basicConfig(stream=sys.stdout,
                format='[%(levelname)s] %(message)s',
                level=log.DEBUG)

log.addLevelName(log.DEBUG, "\033[1;34mD\033[1;0m")
log.addLevelName(log.INFO, "\033[1;32mI\033[1;0m")
log.addLevelName(log.WARNING, "\033[1;33mW\033[1;0m")
log.addLevelName(log.ERROR, "\033[1;31mE\033[1;0m")
log.addLevelName(log.CRITICAL, "\033[1;31mC\033[1;0m")


class Dialogflow(object):

    valid_variable_name = '[a-zA-Z][a-zA-Z0-9_-]*'
    valid_user_defined_entitiy = '[a-zA-Z][a-zA-Z0-9_-]*'
    valid_buildin_entity = 'sys.(email|language|date-period|' + \
                           'duration|street-address|date|time-period|' + \
                           'unit-weight|music-artist|percentage|' + \
                           'number|location|date-time|unit-volume|' + \
                           'geo-city|color|last-name|address|' + \
                           'flight-number|given-name|phone-number|' +\
                           'any|currency-name|url|zip-code|time|' + \
                           'geo-country|geo-state-de|unit-currency)'

    def __init__(self):
        if not utils.has_credentials():
            utils.print_missing_credential_notification()
            sys.exit(-1)

        self._project_id = utils.get_project_id_from_credentials()
        self._intents_client = dialogflow.IntentsClient()
        self._entity_types_client = dialogflow.EntityTypesClient()
        self._project_parent = self._intents_client.project_agent_path(
            self._project_id)
        log.info('Project Name: {}'.format(self._project_id))

        self.__load_intents__()
        self.__load_entities__()

        self._input_contexts = []

    def __load_intents__(self):
        log.info('Getting intents ..')
        self._intents = list(
            self._intents_client.list_intents(self._project_parent,
                                              intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL))
        log.info('Got {} intents'.format(len(self._intents)))

    def __load_entities__(self):
        log.info('Getting entity types ..')
        self._entity_types = list(
            self._entity_types_client.list_entity_types(self._project_parent))
        log.info('Got {} entitcreate_entity types'.format(len(self._entity_types)))

        self._entity_name_type_pattern = re.compile('{}@({}|{})'.format(
            Dialogflow.valid_variable_name,
            Dialogflow.valid_buildin_entity,
            Dialogflow.valid_user_defined_entitiy))

    @property
    def intents(self):
        return self._intents

    @property
    def entity_types(self):
        return self._entity_types

    def __create_input_contexts__(self, input_contexts):
        template = 'projects/{project_id}/agent/' +\
                   'sessions/-/contexts/{context_id}'
        return [template.format(
            project_id=self._project_id, context_id=c) for c in input_contexts
        ]

    def __create_output_contexts__(self, output_contexts):
        res = []
        for c, l in output_contexts:
            res.append({
                'name': 'projects/{project_id}/agent' +
                        '/sessions/-/contexts/{context_id}'
                        .format(project_id=self._project_id, context_id=c),
                'lifespan_count': l
            })
        return res

    def __create_training_phrases__(self, training_phrases):
        res = []
        for t in training_phrases:
            if '@' not in t:
                parts = [{'text': t}]
            else:
                log.debug('Got training phrase with enities')

                matches = self._entity_name_type_pattern.finditer(t)

                current_index = 0
                parts = []
                for match in matches:
                    start, end = match.span()
                    text = t[current_index:start]
                    entity = t[start:end].strip()

                    entity_name, entity_type = entity.split('@')

                    if text != '':
                        log.debug('Got text: ' + text)
                        parts.append({
                            'text': text
                        })
                    log.debug('Got entity: ' + entity)

                    _entity_type = self.find_entity_type(entity_type)
                    if not _entity_type:
                        raise RuntimeError("""Entity with type {} used but it doen\'t exist.
                            Please create it with df.create_entity(..) before using inside an intent."""
                                           .format(entity_type))
                    lookup = Dialogflow.entity_type_to_dict(_entity_type)
                    parts.append({
                        'text': lookup.items()[0][0],
                        'entity_type': '@' + entity_type,
                        'alias': entity_name
                    })
                    current_index = end
                if current_index != len(t)-1:
                    text = t[current_index:]
                    log.debug('Got text: ' + text)
                    parts.append({'text': text})

            res.append({
                'type': 'EXAMPLE',
                'parts': parts,
            })
        return res

    @contextmanager
    def context(self, contexts):
        if isinstance(contexts, str):
            contexts = [contexts]
        self._input_contexts.append(contexts)
        yield
        self._input_contexts = self._input_contexts[:-1]

    @staticmethod
    def __create_message__(messages):
        res = []
        text = dialogflow.types.Intent.Message.Text(text=messages)
        message = dialogflow.types.Intent.Message(text=text)
        res.append(message)
        return res

    @staticmethod
    def __get_entity_kind__(value_synonyms_list):
        if isinstance(value_synonyms_list, list) and\
                len(value_synonyms_list) > 0 and\
                isinstance(value_synonyms_list[0], str):
            return dialogflow.enums.EntityType.Kind.KIND_LIST
        elif isinstance(value_synonyms_list, list) and \
                len(value_synonyms_list) > 0 and \
                isinstance(value_synonyms_list[0], tuple):
            return dialogflow.enums.EntityType.Kind.KIND_MAP
        else:
            raise ValueError("value_synonyms_list has the wrong format.")

    def create_entity(self, display_name, value_synonyms_list, auto_expansion_mode=None, language_code='de'):
        if not auto_expansion_mode:
            auto_expansion_mode = dialogflow.enums.EntityType.AutoExpansionMode.AUTO_EXPANSION_MODE_UNSPECIFIED
        kind = Dialogflow.__get_entity_kind__(value_synonyms_list)
        if kind == dialogflow.enums.EntityType.Kind.KIND_LIST:
            entities = [{'value': l, 'synonyms': [l]} for l in value_synonyms_list]
        else:
            entities = [{'value': v, 'synonyms': s} for v, s in value_synonyms_list]

        entity_type = dialogflow.types.EntityType(
            display_name=display_name,
            kind=kind,
            auto_expansion_mode=auto_expansion_mode,
            entities=entities)

        entry = self.find_entity_type(display_name)
        if entry:
            entity_type.name = entry.name
            self._entity_types_client.update_entity_type(
                entity_type, language_code)
        else:
            self._entity_types_client.create_entity_type(
                self._project_parent, entity_type, language_code)

        self.__load_entities__()

    def find_entity_type(self, display_name):
        entry = [e for e in self._entity_types if e.display_name == display_name]
        if len(entry) == 0:
            return None
        elif len(entry) == 1:
            return entry[0]
        else:
            # Should never happen
            raise RuntimeError("Multiple instances of entity found")

    @staticmethod
    def entity_type_to_dict(entity_type):
        return {a.value: a.synonyms for a in entity_type.entities}

    def delete_all_entities(self):
        for entity in self._entity_types:
            entity_type_id = Dialogflow.__get_entity_id__(entity)
            entity_type_path = self._entity_types_client.entity_type_path(
                self._project_id, entity_type_id)
            self._entity_types_client.delete_entity_type(entity_type_path)
        self.__load_entities__()

    @staticmethod
    def __get_entity_id__(entity):
        return entity.name.split('/')[-1]

    def create_intent(self,
                      display_name,
                      training_phrases=None,
                      messages=None,
                      input_contexts=None,
                      output_contexts=None,
                      is_fallback=False,
                      webhook_state='WEBHOOK_STATE_UNSPECIFIED',
                      language_code='de'):
        if training_phrases is None:
            training_phrases = []
        if messages is None:
            messages = []
        if input_contexts is None:
            input_contexts = []
        if output_contexts is None:
            output_contexts = []

        if isinstance(training_phrases, str):
            training_phrases = [training_phrases]
        if isinstance(messages, str):
            messages = [messages]
        if isinstance(input_contexts, str):
            input_contexts = [input_contexts]

        for c in self._input_contexts:
            for ic in c:
                input_contexts += c
        intent = {
            'display_name': display_name,
            'is_fallback': is_fallback,
            'training_phrases': self.__create_training_phrases__(
                training_phrases),
            'webhook_state': webhook_state,
            'input_context_names': self.__create_input_contexts__(
                input_contexts),
            'output_contexts': self.__create_output_contexts__(
                output_contexts),
            'messages': Dialogflow.__create_message__(messages)
        }
        entry = [i for i in self._intents if i.display_name == display_name]
        if len(entry) == 0:
            # CREATE NEW INTENT
            log.info('Intent \'{display_name}\' doesn\'t exist yet.' +
                     'Creating one ..'.format(display_name=display_name))

            self._intents_client.create_intent(
                self._project_parent, intent, language_code=language_code)
            log.info('Created Intent ' +
                     '\'{display_name}\''.format(display_name=display_name))
        elif len(entry) == 1:
            # UPDATE EXISTING INTENT
            log.info('Intent \'{display_name}\' exists. Updating ..'.format(
                display_name=display_name))
            intent['name'] = entry[0].name
            self._intents_client.update_intent(intent, language_code)
            log.info('Updated Intent ' +
                     ' \'{display_name}\''.format(display_name=display_name))
        else:
            log.error('List contained intent ' +
                      '{display_name} {} times.'.format(
                          display_name, len(entry)))
        self.__load_intents__()

    def delete_all_intents(self):
        for intent in self._intents:
            intent_id = Dialogflow.__get_intent_id__(intent)
            intent_path = self._intents_client.intent_path(self._project_id, intent_id)
            self._intents_client.delete_intent(intent_path)
        self.__load_intents__()

    @staticmethod
    def __get_intent_id__(intent):
        return intent.name.split('/')[-1]
