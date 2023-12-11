from __future__ import print_function
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleTable:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SAMPLE_SPREADSHEET_ID = '1G53ZTltTmTD43Z9RSRSY7DqsU9LldkOOQixmXhi7t3g'

    def __init__(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', GoogleTable.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', GoogleTable.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        self.service = build('sheets', 'v4', credentials=creds)

    def getData(self, work_sheet, range_name):
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GoogleTable.SAMPLE_SPREADSHEET_ID,
                                    range=f'{work_sheet}!{range_name}').execute()
        values = result.get('values', [])
        if not values:
            print('No data found.')
            return False
        return values[0]

    def UpdateData(self, work_sheet, range_name, values):
        data = [
            {
                'range': f'{work_sheet}!{range_name}',
                'values': [[values]]  # каждый маленький списак это строка со значениями
            }
        ]
        body = {
            'valueInputOption': 'USER_ENTERED',  # право на измеение таблицы
            'data': data
        }
        sheets = self.service.spreadsheets()
        result = sheets.values().batchUpdate(spreadsheetId=GoogleTable.SAMPLE_SPREADSHEET_ID,
                                             body=body).execute()
        print(f'{result.get("totalUpdatedCells")} ячеек было обновлено')

    def deleteData(self, worksheet, tel):
        import datetime
        from keyboards import days_months, months_list
        current_date = datetime.datetime(2023, 1, 7)
        # current_date = datetime.date.today()
        number_row = sum(days_months[:current_date.month]) + int(current_date.day) + current_date.month
        count_days = number_row + days_months[current_date.month] + days_months[current_date.month] - current_date.day
        sheet = self.service.spreadsheets()

        result = sheet.values().get(spreadsheetId=GoogleTable.SAMPLE_SPREADSHEET_ID,
                                    range=f'{worksheet}!B{number_row}:H{count_days}').execute()
        values = result.get('values', [])
        names_columns = 'BCDEFGH'
        for row in range(len(values)):
            if len(values[row]) > 0:
                for col in range(len(values[row])):
                    if tel in values[row][col]:
                        self.UpdateData(worksheet,
                                        names_columns[col] + str(number_row + row) + ':' + names_columns[col] + str(
                                            number_row + row), '')

