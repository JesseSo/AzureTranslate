import requests, os, base64, logging
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)
region = os.environ.get('REGION')

@app.route('/', methods=['GET', 'POST'])
def translate():
    translated_text = ""
    audio_url = session.get('audio_url', '')
    if request.method == 'POST':
        input_text = request.form['input_text']
        source_lang = request.form['source_lang']
        target_lang = request.form['target_lang']

        # Make the API call to Azure Translation Service
        endpoint = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
        headers = {
            "Ocp-Apim-Subscription-Key": os.environ.get('TRANSLATION_KEY'),
            "Ocp-Apim-Subscription-Region": region,
            "Content-type": "application/json"
        }

        params = {
            "api-version": "3.0",
            "from": source_lang,
            "to": target_lang
        }
        body = [
            {
                "text": input_text
            }
        ]
        response = requests.post(endpoint, headers=headers, params=params, json=body)

        if response.status_code == 200:
            response_json = response.json()
            translated_text = response_json[0]["translations"][0]["text"]

            # Store the translated text in the session
            session['translated_text'] = translated_text

            # Store the target language in the session
            session['target_lang'] = target_lang

        else:
            translated_text = "Error: " + response.text

    else:
        # If there's no POST request, try to retrieve the translated text from the session
        translated_text = session.get('translated_text', '')

        # Use the previously selected target language as the default, if available
        target_lang = session.get('target_lang', 'en')

    return render_template('form.html', translated_text=translated_text, audio_url=audio_url, target_lang=target_lang)

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    logging.info("Generating audio...")
    
    translated_text = session.get('translated_text', '')
    logging.info("Translated text: %s", translated_text)
    
    if not translated_text:
        return redirect(url_for('translate'))

    target_lang = session.get('target_lang', 'en') # Default to English if target language not set
    session['target_lang'] = target_lang

    # Set the voice based on the target language, or use the previously selected voice if available
    if 'voice' in session:
        voice = session['voice']
    elif target_lang.startswith('en'):
        voice = 'en-US-JessaNeural'
    elif target_lang.startswith('fi'):
        voice = 'fi-FI-SelmaNeural'
    elif target_lang.startswith('es'):
        voice = 'es-ES-ElviraNeural' 
    elif target_lang.startswith('de'):
        voice = 'de-DE-AmalaNeural' 
    elif target_lang.startswith('fr'):
        voice = 'fr-FR-BrigitteNeural'
    else:
        voice = 'en-US-JessaNeural' # Default to English (US)

    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=region)
    speech_config.speech_synthesis_voice_name = voice
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_text_async(translated_text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        audio_data = base64.b64encode(result.audio_data).decode()
        audio_url = "data:audio/mp3;base64," + audio_data
        session['audio_url'] = audio_url  # Store the audio URL in the session
        session['voice'] = voice  # Store the selected voice in the session
        logging.info("Audio generated successfully.")
    else:
        logging.error("Error synthesizing audio: %s", result)
        print("Error synthesizing audio: {}".format(result))

    return redirect(url_for('translate'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)