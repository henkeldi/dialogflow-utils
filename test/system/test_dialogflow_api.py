from nose.tools import assert_equals, assert_false, nottest, assert_raises

import dialogflow
from ..context import dialogflow_utils as du


def test_that_we_can_create_and_delete_intents():
    df = du.Dialogflow()
    df.delete_all_intents()
    assert_equals(len(df.intents), 0)
    df.create_intent('Yes', ['yes', 'yeah'])
    assert_equals(len(df.intents), 1)
    intent = df.intents[0]
    assert_equals(intent.display_name, 'Yes')
    assert_equals(len(intent.input_context_names), 0)
    assert_equals(len(intent.parameters), 0)
    assert_equals(len(intent.output_contexts), 0)
    assert_equals(len(intent.events), 0)
    assert_equals(len(intent.training_phrases), 2)
    assert_equals(intent.webhook_state, dialogflow.enums.Intent.WebhookState.WEBHOOK_STATE_UNSPECIFIED)
    assert_false(intent.is_fallback)
    _client = du.ChatClient()
    _response = _client.detect_intent('yes')
    assert_equals(_response.query_result.intent.display_name, 'Yes')
    df.delete_all_intents()
    assert_equals(len(df.intents), 0)


def test_entity_type_detection():
    colors_map = [('red', ['red']), ('blue', ['blue']), ('green', ['green'])]
    t = du.Dialogflow.__get_entity_kind__(colors_map)
    assert_equals(t, dialogflow.enums.EntityType.Kind.KIND_MAP)
    colors_list = ['red', 'blue', 'green']
    t = du.Dialogflow.__get_entity_kind__(colors_list)
    assert_equals(t, dialogflow.enums.EntityType.Kind.KIND_LIST)
    colors_invalid = 'invalid_format'
    assert_raises(ValueError, du.Dialogflow.__get_entity_kind__, colors_invalid)


def test_that_we_can_create_and_delete_entities_of_kind_list():
    df = du.Dialogflow()
    df.delete_all_entities()
    assert_equals(len(df.entity_types), 0)
    colors = ['red', 'blue', 'green']
    df.create_entity('color', colors)
    assert_equals(len(df.entity_types), 1)
    entity = df.entity_types[0]
    assert_equals(entity.display_name, 'color')
    assert_equals(entity.kind, dialogflow.enums.EntityType.Kind.KIND_LIST)
    assert_equals(entity.auto_expansion_mode, dialogflow.enums.EntityType.AutoExpansionMode\
                  .AUTO_EXPANSION_MODE_UNSPECIFIED)
    assert_equals(len(entity.entities), len(colors))
    for e, color in zip(entity.entities, colors):
        assert_equals(e.value, color)
        assert_equals(len(e.synonyms), 1)
        assert_equals(e.synonyms[0], color)
    df.delete_all_entities()
    assert_equals(len(df.entity_types), 0)


def test_that_we_can_create_and_delete_entities_of_kind_map():
    df = du.Dialogflow()
    df.delete_all_entities()
    assert_equals(len(df.entity_types), 0)
    colors = [('red', ['red', 'rot']), ('blue', ['blue', 'blau']), ('green', ['green', 'gruen'])]
    df.create_entity('color', colors)
    assert_equals(len(df.entity_types), 1)
    entity = df.entity_types[0]
    assert_equals(entity.display_name, 'color')
    assert_equals(entity.kind, dialogflow.enums.EntityType.Kind.KIND_MAP)
    assert_equals(entity.auto_expansion_mode, dialogflow.enums.EntityType.AutoExpansionMode
                  .AUTO_EXPANSION_MODE_UNSPECIFIED)
    assert_equals(len(entity.entities), len(colors))
    for e, (color, color_synonyms) in zip(entity.entities, colors):
        assert_equals(e.value, color)
        assert_equals(len(e.synonyms), 2)
        assert_equals(e.synonyms[0], color_synonyms[0])
    df.delete_all_entities()
    assert_equals(len(df.entity_types), 0)


def test_that_we_can_use_entities_inside_of_intents():
    df = du.Dialogflow()
    df.delete_all_intents()
    assert_equals(len(df.intents), 0)
    df.delete_all_entities()
    assert_equals(len(df.entity_types), 0)
    colors = [('red', ['red', 'rot']), ('blue', ['blue', 'blau']), ('green', ['green', 'gruen'])]
    df.create_entity('colors', colors)
    df.create_intent('color_select', ['I want it in color@colors', 'Do you have it in color@colors'])

    # // Check that entity was created correctly
    assert_equals(len(df.entity_types), 1)
    entity = df.entity_types[0]
    assert_equals(entity.display_name, 'colors')
    assert_equals(entity.kind, dialogflow.enums.EntityType.Kind.KIND_MAP)
    assert_equals(entity.auto_expansion_mode, dialogflow.enums.EntityType.AutoExpansionMode
                  .AUTO_EXPANSION_MODE_UNSPECIFIED)
    assert_equals(len(entity.entities), len(colors))
    for e, (color, color_synonyms) in zip(entity.entities, colors):
        assert_equals(e.value, color)
        assert_equals(len(e.synonyms), 2)
        assert_equals(e.synonyms[0], color_synonyms[0])

    df.delete_all_intents()
    assert_equals(len(df.intents), 0)

    df.delete_all_entities()
    assert_equals(len(df.entity_types), 0)
