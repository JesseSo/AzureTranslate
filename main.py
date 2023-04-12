import requests, uuid, json
from jproperties import Properties

configs = Properties()

with open('properties', 'rb') as config_file:
    configs.load(config_file)

constructed_url = "https://api.cognitive.microsofttranslator.com/translate"

params = {
    'api-version': '3.0',
    'from': 'en',
    'to': ['fi']
}

headers = {
    'Ocp-Apim-Subscription-Key': configs.get("key").data,
    # location required if you're using a multi-service or regional (not global) resource.
    'Ocp-Apim-Subscription-Region': configs.get("location").data,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

textToTranslate = input("Give the text to translate: ")

# You can pass more than one object in body.
body = [{
    'text': textToTranslate
}]

request = requests.post(constructed_url, params=params, headers=headers, json=body)
response = request.json()

print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))