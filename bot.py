# JackBot AI - FULL WORKING VERSION
# Run: python bot.py

import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# Load env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

client = OpenAI(api_key=OPENAI_API_KEY)

# Intents (FIXED)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Store active tickets
active_tickets = {}

BAD_WORDS = ["kill", "rape", "suicide", "fuck you", "nigger", "faggot", "retard", "cunt", "bitch", "whore"]

def is_bad_message(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in BAD_WORDS)

# --------------------------
# TICKET BUTTON VIEW
# --------------------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green, emoji="📩")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        thread = await interaction.channel.create_thread(
            name=f"ticket-{interaction.user.name}",
            type=discord.ChannelType.private_thread
        )

        active_tickets[thread.id] = interaction.user.id

        await thread.add_user(interaction.user)

        await thread.send(
            f"👋 Hello {interaction.user.mention}!\n"
            "You're now chatting with **JackBot AI**.\n"
            "Type `close` to close this ticket."
        )

        await interaction.response.send_message("✅ Ticket created!", ephemeral=True)

# --------------------------
# SLASH COMMAND: SETUP PANEL
# --------------------------
@tree.command(name="setup_tickets", description="Create the ticket panel")
@app_commands.default_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 Support Tickets",
        description="Click the button below to open a ticket and talk to AI.",
        color=0x00ff88
    )

    view = TicketView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Panel created!", ephemeral=True)

# --------------------------
# AI MESSAGE HANDLER
# --------------------------
@bot.event
async def on_message(message: discord.Message):

    if message.author.bot:
        return

    # ONLY respond in ticket threads
    if not isinstance(message.channel, discord.Thread):
        return

    # Only if it's an active ticket
    if message.channel.id not in active_tickets:
        return

    # Close command
    if message.content.lower().strip() == "close":
        await message.channel.send("🔒 Closing ticket...")
        await message.channel.delete()
        active_tickets.pop(message.channel.id, None)
        return

    # Bad word detection
    if is_bad_message(message.content):
        owner = await bot.fetch_user(OWNER_ID)
        if owner:
            await owner.send(
                f"⚠️ BAD MESSAGE\n"
                f"User: {message.author} ({message.author.id})\n"
                f"Message: {message.content}"
            )
        await message.channel.send("⚠️ Be respectful.")
        return

    await message.channel.send("🤖 Thinking...", delete_after=2)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are JackBot AI, a helpful Discord assistant."},
                {"role": "user", "content": message.content}
            ],
            temperature=0.7,
            max_tokens=500
        )

        reply = response.choices[0].message.content
        await message.channel.send(reply)

    except Exception as e:
        print("AI ERROR:", e)
        await message.channel.send("⚠️ AI failed.")

    # IMPORTANT
    await bot.process_commands(message)

# --------------------------
# READY EVENT
# --------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    try:
        synced = await tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# --------------------------
# RUN BOT
# --------------------------
bot.run(DISCORD_TOKEN)
