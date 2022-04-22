'''
Hugging Face API calls
'''

import json
import requests

import config

API_URL = 'https://api-inference.huggingface.co/models/'
headers = {"Authorization": f"Bearer {config.WRITE_TOKEN}"}

# Hugging Face Models
T0PP = 'bigscience/T0pp'
T5_11B_SSM_TQA = 'google/t5-11b-ssm-tqa'


def query(payload, model_tag):
    data = json.dumps(payload)
    target_url = API_URL + model_tag
    response = requests.request("POST", target_url, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))
