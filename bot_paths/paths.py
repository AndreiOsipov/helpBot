import os

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TOKENS_PATH = os.path.join(ROOT, "tokens")
BOT_TOKEN = os.path.join(TOKENS_PATH, "bot_token.json")
GOOGLE_API_CREDS_PATH = os.path.join(TOKENS_PATH, "service_key.json")
SPREADSHEET_ID_PATH = os.path.join(TOKENS_PATH, "spreadsheet.json")