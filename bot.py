import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_KEY

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ JackBot AI is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Simple reply with ChatGPT
    if message.content.startswith("!ask"):
        question = message.content[5:].strip()
        if not question:
            await message.reply("Ask me something!")
            return

        await message.channel.send("🤖 Thinking...")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}],
                max_tokens=500
            )
            reply = response.choices[0].message.content
            await message.reply(reply)
        except Exception as e:
            await message.reply("Sorry, something went wrong.")

bot.run(TOKEN)
