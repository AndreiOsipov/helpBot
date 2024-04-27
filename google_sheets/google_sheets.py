from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import re
import datetime
import json
from dataclasses import dataclass
from bot_paths.paths import GOOGLE_API_CREDS_PATH, SPREADSHEET_ID_PATH


@dataclass
class ShortClient:
    name: str
    payment_date: str
    responsible_user: str


class ClientsGoogleSheetsGetter:
    _instance = None


    def __init__(self) -> None:
        self.spreadsheet_id = self.get_spreadsheet_id()
        # self.responsible_user = responsible_user
        self.service = self.get_service()
        self.clients_range = "A1:V"

    def get_spreadsheet_id(self) -> str:
        with open(SPREADSHEET_ID_PATH) as spreadsheet_id_file:
            spreadsheet = json.load(spreadsheet_id_file)
            return  spreadsheet["spreadsheet_id"]

    def get_service(self):
        credentials = Credentials.from_service_account_file(GOOGLE_API_CREDS_PATH)
        return build('sheets', 'v4', credentials=credentials)
 

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls)
        return cls._instance

 
    def get_row_date_template(self, row_date: str):
        row_date_template = None
        pattern = r'\b\d{1,2}\.\d{1,2}\.\d{4}\b|\b\d{1,2}\.\d{1,2}\.\d{2}\b'
        str_date_lst = re.findall(pattern, row_date)
        if len(str_date_lst) > 0:
            if len(row_date.split(".")[-1]) > 2:
                row_date_template = "%d.%m.%Y"
            elif len(row_date.split(".")[-1]) == 2:
                row_date_template = "%d.%m.%y"
        return row_date_template

    def check_row_by_responsible_user(self, responsible_user: str, requeired_responsible_user: str):
        return (responsible_user == requeired_responsible_user) or (requeired_responsible_user == "Все") or (requeired_responsible_user is None)
 
    def get_clients_by_responsible_user(self, requeired_responsible_user: str):
        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=self.clients_range).execute()
        values:list[list] = result.get("values", [])
        cols_names:list[str] = values[0]
        
        name_index = cols_names.index("Name")
        payment_date_index = cols_names.index("До какого оплачено?")
        responsible_user_index = cols_names.index(" От кого?")
        
        clients_data:list[list[str]] = values[1:]
        users_clients: list[ShortClient] = []
        clients_without_responsible_user: list[ShortClient] = []
        
        
        for row in clients_data:
            if responsible_user_index < len(row):
                if self.check_row_by_responsible_user(row[responsible_user_index], requeired_responsible_user):
                    row_date_template = self.get_row_date_template(row[payment_date_index])
                    if row_date_template:
                        date = datetime.datetime.strptime(row[payment_date_index], row_date_template)
                        if date <= datetime.datetime.today():
                            users_clients.append(ShortClient(row[name_index], date.strftime("%d.%m.%Y"), row[responsible_user_index]))
                    elif row[payment_date_index] == "":
                        users_clients.append(ShortClient(row[name_index], "", row[responsible_user_index]))
            else:
                clients_without_responsible_user.append(ShortClient(row[name_index], "", ""))
        return users_clients, clients_without_responsible_user

# client_cls = ClientsGoogleSheetsGetter()
# print(client_cls.get_clients_by_responsible_user("Все"))