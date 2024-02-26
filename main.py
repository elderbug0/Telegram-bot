from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
)
import openai
from openai.error import OpenAIError
import json

# Assuming you've set your tokens as environment variables for security reasons
TOKEN = ''
BOT_USERNAME = ''
openai.api_key = ""

# Define states for the conversation
WAITING_FOR_QUESTION,ASKING, BACK, BOOKS, GRADE_SELECTION = range(5)


def ai(text: str) -> str:
    processed: str=text.lower()
    messages = [
        {"role": "system", "content": f"Физика туралы көп білесін. Осы сураққа жауап бер: {processed}; физикалык формулаларды текстпен жаз себеби телеграм оны окымайды. Жане тез жаз"}
    ]
    try:
        # Generate a response using the GPT-3.5 Turbo model
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=messages

        )

        decoded_response = response.choices[0].message['content']
        return decoded_response

    except OpenAIError as e:
        response = "The server is experiencing a high volume of requests. Please try again later."
        return response

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        ["Сұрақ қою 🤖", "Кітап Алу 📚"],
        ["Артқа 🔙"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Таңда:', reply_markup=reply_markup)
    return ASKING

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_message = update.message.text

    keyboard = [["Сұрақ қою 🤖", "Кітап Алу 📚"], ["Артқа 🔙"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    if user_message.lower() == "артқа 🔙":
        await update.message.reply_text('Таңда:', reply_markup=reply_markup)
        return ASKING
    elif user_message.lower() == "сұрақ қою 🤖":
        # Prompt the user to type their question
        await update.message.reply_text("Сұрағыңызды жазыңыз:", reply_markup=ReplyKeyboardMarkup([["Артқа 🔙"]], one_time_keyboard=True, resize_keyboard=True))

        return WAITING_FOR_QUESTION  # Move to waiting state for the user's question
    elif user_message.lower() == "кітап алу 📚":
        # Move to the BOOKS state and present new options
        return await books(update, context)


async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_message = update.message.text
    if user_message.lower() == "артқа 🔙":
        # If the user wants to go back, show the initial options again
        return await ask_ai(update, context)
    else:
        await update.message.reply_text("Күте тұрыңыз")
        # Process the question through your AI function
        response = ai(user_message)  # Process the user's question here

        print(user_message)
        await update.message.reply_text(response)
        print(response)
        return WAITING_FOR_QUESTION  # Allow the user to ask another question or press "артка"


async def books(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        ["9 сынып 📙", "10 сынып 📘","11 сынып 📕"],
        ["Артқа 🔙"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Сыныпты Таңда:', reply_markup=reply_markup)
    return GRADE_SELECTION

async def grade_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_message = update.message.text# Constructing the file path

    if user_message.lower() == "9 сынып 📙":
        await update.message.reply_text("https://forms.gle/e4ZjbLqb2DVKdjrx7")
        return await books(update,context)
    if user_message.lower() == "10 сынып 📘":
        await update.message.reply_text('https://forms.gle/9UCw7uMauA8asJqCA')
        return await books(update,context)
    if user_message.lower() == "11 сынып 📕":
        await update.message.reply_text('https://forms.gle/jRgApX9PR2hy3Doi9')
        return await books(update,context)
    elif user_message.lower() == "артқа 🔙":
        return await start_command(update, context)  # Go back to the start options



def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    print(f"User {user.first_name} canceled the conversation.")
    update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END

if _name_ == '_main_':
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            ASKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai)],
            BOOKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, books)],
            GRADE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, grade_selection)],
            WAITING_FOR_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )


    application.add_handler(conv_handler)

    print('Bot is polling...')
    application.run_polling()
