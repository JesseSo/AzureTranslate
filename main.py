import requests, json, uuid, os
from jproperties import Properties
import azure.cognitiveservices.speech as speechsdk

configs = Properties()

with open('properties', 'rb') as config_file:
    configs.load(config_file)

constructed_url = "https://api.cognitive.microsofttranslator.com/translate"

language = 'fr'

params = {
    'api-version': '3.0',
    'from': 'en',
    'to': [language]
}

location = configs.get("location").data

headers = {
    'Ocp-Apim-Subscription-Key': configs.get("translation_key").data,
    'Ocp-Apim-Subscription-Region': location,
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
translations = response[0]['translations']
text = translations[0]['text']

#Speech configs
speech_config = speechsdk.SpeechConfig(subscription=configs.get("speech_key").data, region=location)
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name='fr-FR-BrigitteNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")