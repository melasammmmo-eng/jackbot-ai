# JackBot AI - Using GPT-5-mini

import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from openai import OpenAI
import asyncio
from datetime import datetime

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID") or 0)

client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

active_tickets = {}

BAD_WORDS = ["kill", "rape", "suicide", "nigger", "faggot", "retard", "cunt", "bitch", "whore"]

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
            type=discord.ChannelType.private_thread,
            reason=f"Ticket by {interaction.user}"
        )

        active_tickets[thread.id] = interaction.user.id

        await thread.add_user(interaction.user)
        await thread.send(
            f"**Hello {interaction.user.mention}!**\n"
            "You are now chatting with **JackBot AI**.\n"
            "Ask me anything! I'm here to help.\n\n"
            "**Type `close` to close this ticket.**"
        )

        await interaction.response.send_message("✅ Ticket created! Go to the thread.", ephemeral=True)


@tree.command(name="setup_tickets", description="Create the ticket panel")
@app_commands.default_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction):
    embed = discord.Embed(
        title="wanna chat?",
        description="Click below to talk to JackBot AI",
        color=0x00ff88
    )
    view = TicketView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Ticket panel created!", ephemeral=True)


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
            await owner.send(
                f"**⚠️ BAD MESSAGE DETECTED**\n"
                f"**User:** {message.author} ({message.author.id})\n"
                f"**Ticket:** {message.channel.mention}\n"
                f"**Message:** {message.content}\n"
                f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        await message.channel.send("⚠️ Please be respectful.")
        return

    await message.channel.send("🤖 JackBot AI is thinking...", delete_after=1.5)

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are JackBot AI, a helpful, friendly, and fun Discord assistant. Keep responses short and clear."},
                {"role": "user", "content": message.content}
            ],
            temperature=0.7,
            max_tokens=300
        )

        reply = response.choices[0].message.content
        await message.channel.send(reply)

    except Exception as e:
        print(f"OpenAI Error: {e}")
        await message.channel.send("Sorry, I'm having trouble responding right now. (Check your OpenAI credits)")


@bot.event
async def on_ready():
    print(f"✅ JackBot AI is online as {bot.user}")


bot.run(DISCORD_TOKEN)
