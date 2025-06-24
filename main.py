import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram.ext import Updater, MessageHandler, Filters

# ===== CONFIG =====
BOT_TOKEN = "your-telegram-bot-token"
OPENAI_API_KEY = "your-openai-api-key"
GOOGLE_SHEET_NAME = "Student Database"

openai.api_key = OPENAI_API_KEY

# ===== GOOGLE SHEETS SETUP =====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("studentbot-463913-2b13759b4fa7.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

# ===== GPT FUNCTION =====
def ask_gpt(question, data):
    prompt = f"""You are a helpful assistant using this student database:

{data}

Answer the question below clearly and directly.

Question: {question}
Answer:"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300
    )

    return response['choices'][0]['message']['content']

# ===== TELEGRAM BOT LOGIC =====
def handle_message(update, context):
    question = update.message.text
    records = sheet.get_all_records()
    data_text = "\n".join([str(r) for r in records])

    answer = ask_gpt(question, data_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=answer)

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

print("🤖 Bot is running...")
updater.start_polling()
