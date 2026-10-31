import logging
import os
from flask import Flask, request, jsonify
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

@app.get('/ping')
def ping():
    return jsonify(ack='pong')

@app.post('/chat')
def chat():
    key = os.getenv('OPENROUTER_API_KEY', '').strip()
    if not key:
        return jsonify(error='OPENROUTER_API_KEY missing on Flask server'), 500
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error='Expected JSON object'), 400
    prompt = payload.get('input', '')
    model = payload.get('model_id') or DEFAULT_MODEL
    if not isinstance(prompt, str) or not prompt.strip():
        return jsonify(error='Question required'), 400
    if not isinstance(model, str):
        return jsonify(error='Invalid model_id'), 400
    try:
        client = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=key, timeout=90.0)
        result = client.chat.completions.create(model=model, messages=[{'role':'user','content':prompt.strip()}])
        answer = result.choices[0].message.content
        return jsonify(ack=answer or '(Empty model response)')
    except OpenAIError as exc:
        # Log status/type without displaying secrets or API key.
        logging.exception('OpenRouter API call failed')
        return jsonify(error='OpenRouter API call failed', detail=str(exc)[:350]), 502
    except Exception:
        logging.exception('Unexpected server failure')
        return jsonify(error='Unexpected server failure'), 500

if __name__ == '__main__':
    app.run(host=os.getenv('FLASK_HOST','127.0.0.1'), port=int(os.getenv('PORT','5001')), debug=False)
