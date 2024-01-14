from oauth2client.service_account import ServiceAccountCredentials
import os
import httplib2
from googleapiclient.discovery import build
from config import ID_SPREADSHEET


class GoogleTable:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SAMPLE_SPREADSHEET_ID = ID_SPREADSHEET

    def __init__(self):
        self.service = self.get_service_sacc()

    def get_service_sacc(self):
        creds_json = os.path.dirname(__file__) + "/creds/sacc1.json"
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
        return build('sheets', 'v4', http=creds_service)

    def getData(self, work_sheet, range_name):
        '''
        Функция получения данных из таблицы
        '''
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GoogleTable.SAMPLE_SPREADSHEET_ID,
                                    range=f'{work_sheet}!{range_name}').execute()  # result это словарь {'majorDimension': 'ROWS', 'range': "'Алина Репина'!B1:K1", 'values': [['9.00', '11.00', '13.00', '15.00', '17.00', '19.00', '21.00']]}
        values = result.get('values', [])  # [] - значение по умолчанию, если по ключу ничего не найдется
        if not values:
            print('No data found.')
            return False
        return values[0]

    def updateData(self, work_sheet, range_name, values):
        '''
        Функция обновления/изменения ячеек таблицы
        '''
        data = [
            {
                'range': f'{work_sheet}!{range_name}',
                'values': [[values]]  # каждый маленький список это строка со значениями
            }
        ]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        sheets = self.service.spreadsheets()
        result = sheets.values().batchUpdate(spreadsheetId=GoogleTable.SAMPLE_SPREADSHEET_ID,
                                             body=body).execute()
        print(f'{result.get("totalUpdatedCells")} ячеек было обновлено')

    def deleteData(self, worksheet, tel):
        '''
        Функция удаления данных из таблицы по номеру телефона клиента
        '''
        import datetime
        from keyboards import days_months, months_list
        # current_date = datetime.datetime(2023, 1, 7)
        current_date = datetime.date.today()
        number_row = sum(days_months[:current_date.month]) + int(current_date.day) + current_date.month
        count_days = number_row + days_months[current_date.month] * (current_date.month + 1 < 12) \
                     + days_months[current_date.month] - current_date.day  # хранит количество дней наперед
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GoogleTable.SAMPLE_SPREADSHEET_ID,
                                    range=f'{worksheet}!B{number_row}:H{count_days}').execute()
        values = result.get('values', [])
        names_columns = 'BCDEFGH'
        is_found = False
        for row in range(len(values)):
            if len(values[row]) > 0:
                for col in range(len(values[row])):
                    if tel in values[row][col]:
                        self.updateData(worksheet,
                                        names_columns[col] + str(number_row + row) + ':' + names_columns[col] + str(
                                            number_row + row), '')
                        is_found = True
        return is_found
