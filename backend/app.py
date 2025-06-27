# Importando as bibliotecas necessárias
import os
import requests
import uuid
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()

app = Flask(__name__) 

CORS(app) 

# Continuação do app.py...

# Pega as credenciais carregadas do .env de forma segura
AZURE_SUBSCRIPTION_KEY = os.getenv('AZURE_SUBSCRIPTION_KEY')
AZURE_LOCATION = os.getenv('AZURE_LOCATION')
AZURE_ENDPOINT = 'https://api.cognitive.microsofttranslator.com/' 

# Define a rota da nossa API.
# Ela será acessível em http://127.0.0.1:5000/api/translate
# e aceitará apenas requisições do tipo POST.

    # Substitua a função translate_text() anterior por esta

@app.route('/api/translate', methods=['POST'])
def translate_text():
    # 1. Validação interna: Verifica se as chaves foram carregadas no servidor
    if not AZURE_SUBSCRIPTION_KEY or not AZURE_LOCATION:
        return jsonify({'error': 'Credenciais da Azure não configuradas no servidor.'}), 500

    # 2. Extração de dados: Pega os dados enviados pelo frontend
    try:
        data = request.get_json()
        text_to_translate = data['text']
        target_language = data['to']
        source_language = data.get('from') # .get() é seguro para campos opcionais
    except:
        return jsonify({'error': 'Dados inválidos. "text" e "to" são obrigatórios.'}), 400

    # 3. Preparação da chamada para a Azure: Monta a URL e os cabeçalhos
    constructed_url = f"{AZURE_ENDPOINT}/translate?api-version=3.0&to={target_language}"
    if source_language:
        constructed_url += f"&from={source_language}"

    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_SUBSCRIPTION_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_LOCATION,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{'text': text_to_translate}]

    # 4. Execução: Chama a API da Azure e retorna a resposta para o frontend
    try:
        azure_response = requests.post(constructed_url, headers=headers, json=body)
        azure_response.raise_for_status()  # Lança erro se a resposta não for 2xx (sucesso)
        
        response_data = azure_response.json()
        translated_text = response_data[0]['translations'][0]['text']
        
        # 5. Sucesso: Retorna a tradução em um JSON para o frontend
        return jsonify({'translation': translated_text})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Falha na comunicação com a API da Azure: {e}'}), 502
    except Exception as e:
        return jsonify({'error': f'Erro inesperado: {str(e)}'}), 500
    
if __name__== '__main__': 
    app.run(debug=True, port=5000) 
