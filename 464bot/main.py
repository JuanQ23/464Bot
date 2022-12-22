import discord
import os
import asyncio

from discord.ext import commands

#creating bot object with all intents and * is a optional command prefix.
#the only command that uses a prefix is sync
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="*", intents=intents)

@bot.event
async def on_ready():
    """event that is called when the bot is ready."""
    print("bot, ready")

async def load():
    """loads all the cogs in the cogs file"""
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    """function that starts the loads all of the cogs in the cogs folder. and starts the bot."""
    await load()
    async with bot:
        token = "YOUR TOKEN HERE"
        await bot.start(token)

asyncio.run(main()) #Starting the event loop