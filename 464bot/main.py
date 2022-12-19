import discord
import os
import asyncio

from discord.ext import commands

#create bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="*", intents=intents)

@bot.event
async def on_ready():
    print("bot, ready")
    print(f"is the bot rate limited? {bot.is_ws_ratelimited()}")

async def load():
    """loads all the cogs in cogs file"""
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f"cogs.{file[:-3]}")

@bot.tree.context_menu()
async def react(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message('Very cool message!', ephemeral=True)

async def main():
    await load()
    async with bot:
        token = "YOUR TOKEN HERE"
        await bot.start(token)

asyncio.run(main())