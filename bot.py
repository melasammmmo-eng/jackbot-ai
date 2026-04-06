# JackBot AI - Simple Ticket System with ChatGPT
# Run: python bot.py

import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import openai
import asyncio
from datetime import datetime

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

active_tickets = {}

BAD_WORDS = ["kill", "rape", "suicide", "nigger", "faggot", "retard", "cunt", "bitch"]

def is_bad_message(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in BAD_WORDS)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green, emoji="📩")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        thread = await interaction.channel.create_thread(
            name=f"Ticket-{interaction.user.name}",
            type=discord.ChannelType.private_thread
        )

        active_tickets[thread.id] = interaction.user.id

        await thread.add_user(interaction.user)
        await thread.send(
            f"**Hello {interaction.user.mention}!**\n"
            "You are now chatting with **JackBot AI**.\n"
            "Ask me anything!\n\n"
            "**Type `close` to close this ticket.**"
        )

        await interaction.response.send_message("✅ Ticket created! Go to the thread.", ephemeral=True)

@tree.command(name="setup_tickets", description="Create ticket button")
@app_commands.default_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Need Help?",
        description="Click below to talk to JackBot AI",
        color=0x00ff88
    )
    view = TicketView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Done!", ephemeral=True)

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not isinstance(message.channel, discord.Thread):
        return
    if message.channel.id not in active_tickets:
        return

    if message.content.lower().strip() == "close":
        await message.channel.send("Closing ticket...")
        await message.channel.delete()
        active_tickets.pop(message.channel.id, None)
        return

    if is_bad_message(message.content):
        owner = await bot.fetch_user(OWNER_ID)
        if owner:
            await owner.send(f"⚠️ Bad message in ticket {message.channel.mention}\nUser: {message.author}\nMessage: {message.content}")
        await message.channel.send("⚠️ Please be respectful.")
        return

    # ChatGPT Response
    await message.channel.send("🤖 Thinking...", delete_after=1.5)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",   # You can change to "gpt-4o" if you want better answers
            messages=[
                {"role": "system", "content": "You are JackBot AI, a helpful and friendly assistant."},
                {"role": "user", "content": message.content}
            ],
            temperature=0.7,
            max_tokens=700
        )
        reply = response.choices[0].message.content
        await message.channel.send(reply)

    except Exception as e:
        await message.channel.send("Sorry, I'm having trouble right now.")

@bot.event
async def on_ready():
    print(f"✅ JackBot AI is online as {bot.user}")

bot.run(DISCORD_TOKEN)
