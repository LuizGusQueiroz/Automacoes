from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from typing import List
import os


def salva_relatorio(row: List[List]):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SAMPLE_SPREADSHEET_ID = "15gGHm67_W5maIas-4_YPSzE6R5f_CNJGcza_BJFlNBk"  # Código da planilha
    SAMPLE_RANGE_NAME = "Página1!A{}:D1000"  # Intervalo que será lido
    creds = None
    if os.path.exists("configs/creds/token.json"):
        creds = Credentials.from_authorized_user_file("configs/creds/token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "configs/creds/client.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("configs/creds/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME.format(2))
            .execute()
        )
        values = result.get("values", [])

        idx = 2 + len(values)

        result = (
            sheet.values()
            .update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME.format(idx),
                    valueInputOption='USER_ENTERED', body={"values": row})
            .execute()
        )

    except HttpError as err:
        print(err)
