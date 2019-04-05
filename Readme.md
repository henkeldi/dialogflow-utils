
# Dialogflow Utils

Python Library to automate intent and entity creation in Dialogflow.

## Installation

```bash
make deps
make
```

## Initial steps

1. Create *Google Cloud Service Account* as described [here](https://cloud.google.com/docs/authentication/production#obtaining_and_providing_service_account_credentials_manually)

2. Export *Google Application Credentials*

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

3. Import *Dialogflow Utils* 

```python
import dialogflow_utils as du
```

### Usage example

* Create an instance of *Dialogflow*

```python
df = du.Dialogflow()
```

* Create Intent

```python
# df.create_intent('<intent-name>',
#     ['<training-phrase-1>', '<training-phrase-2>'])

df.create_intent('yes_intent',
    ['yes', 'sure', 'do it'])
```

* Create Entity

```python
# df.create_entity('<entity-name>', [('<entry-1>', ['<synonym-1>', '<synonym-2>'])])

df.create_entity('sizes', [('small', ['small', 'little', 'S'])])
```

* Use Entity

```python
# df.create_intent('t-shirt_intent',
#    ['I want a t-shirt in size <parameter-name>@<entity-type>'])

df.create_intent('t-shirt_intent',
    ['I want a t-shirt in size size@sizes'])
```

* Set Input Contexts
```python
with df.context('ask_for_more'):
    df.create_intent('yes_intent', ['yes', 'sure'])
    df.create_intent('no_intent', ['no', 'not really'])
```

### Test agent
```python
client = du.ChatClient()

client.detect_intent("Hello")
```

Example Respone:

```python
response_id: "cb95e7c6-179f-42ec-9ce9-5f5f37689a41"
query_result {
  query_text: "Hello"
  parameters {
  }
  all_required_params_present: true
  fulfillment_messages {
    text {
      text: ""
    }
  }
  intent {
    name: "projects/<project-id>/agent/intents/ec5vc707-0506-4144-87ad-46d2a8e1oda8"
    display_name: "greeting_intent"
  }
  intent_detection_confidence: 1.0
  language_code: "de"
}
```

### Run tests

```bash
make test
```