
# Telegram GPT bot

My first Telegram bot, created in Python using ChatGPT.

The bot can communicate with the user, show random facts and perform other interesting actions.

The project is made as an educational one — for practice working with Aiogram and OpenAI API.

________________________________________

### ✨ Bot capabilities

• User selects a command after a command (/start)

• Shows a random image and an interesting fact (/random)

• Has a dialogue with a famous person (/talk)

• Conducts a quiz (/quiz)

• Performs translation (/translate)

• Conducts a game with a dice (/roll)
________________________________________

### 🛠 Technologies used

• Python 3.10+

• Aiogram — working with Telegram API

• OpenAI API (ChatGPT) — text generation

• python-dotenv — secure token storage

• Git + GitHub — for project management
________________________________________________

### 🚀 How to run the bot locally

1. Clone the repository:
git clone https://github.com/OksanaMykich/telegram-gpt-bot.git
2. Go to the project folder:
cd telegram-gpt-bot
3. Install libraries:
pip install -r requirements.txt
4. Create a .env file:
BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_API_key
5. Run the bot:
python main.py
______________________________________

### 🔒 Security

• The .env file is not uploaded to GitHub — it is protected in .gitignore

• The .env.example is used for the example, which shows the file structure
_______________________________________

Author: Oksana Mykich

A training project for practicing creating Telegram bots with ChatGPT 💬