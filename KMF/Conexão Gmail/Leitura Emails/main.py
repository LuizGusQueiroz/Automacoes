from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import base64
import email

# Defina as credenciais do OAuth 2.0 (baixadas do Console do Google Cloud)
credenciais_json = 'credentials.json'

# Escopo da API do Conexão Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def autenticar():
    creds = None

    # Verifica se já existe um arquivo de token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    # Se não há credenciais válidas, solicita a autenticação do usuário
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credenciais_json, SCOPES)
            creds = flow.run_local_server(port=0)

        # Salva as credenciais para futuros usos
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def main():
    # Autenticar e criar um objeto de serviço do Conexão Gmail
    creds = autenticar()
    service = build('gmail', 'v1', credentials=creds)

    # Exemplo: Listar os 10 primeiros emails da caixa de entrada
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print('Nenhum email encontrado.')
    else:
        print('Mensagens:')


        for message in messages:
            message = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = message['payload']

            # Processar a parte do payload que contém o corpo da mensagem
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        raw_data = part['body']['data']
                        msg_str = base64.urlsafe_b64decode(raw_data.encode('ASCII')).decode('utf-8')
                        mime_msg = email.message_from_string(msg_str)

                        assunto = mime_msg['Subject']
                        print(f"Assunto: {assunto}")

                        body = part['body']['data']
                        body_decoded = base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8')
                        print("Conteúdo da mensagem:")
                        print(body_decoded)
            else:
                raw_data = payload['body']['data']
                msg_str = base64.urlsafe_b64decode(raw_data.encode('ASCII')).decode('utf-8')
                mime_msg = email.message_from_string(msg_str)

                assunto = mime_msg['Subject']
                print(f"Assunto: {assunto}")

                body = payload['body']['data']
                body_decoded = base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8')
                print("Conteúdo da mensagem:")
                print(body_decoded)



if __name__ == '__main__':
    main()
