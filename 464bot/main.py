"""Main file that creates the bot, loads the cogs, and runs the bot.

This file creates a bot using commands.Bot with all the intents and loads all of the cogs in the
cogs folder onto the bot.
"""
import os
import asyncio
import discord

from discord.ext import commands

# creating bot object with all intents and * is a optional command prefix.
# the only command that uses a prefix is sync
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="*", intents=intents)


@bot.event
async def on_ready():
    """Even that is called once the bot is ready.

    Called when the client is done preparing the data received from Discord.
    Usually after login is successful and the Client.guilds is filled up.
    """
    print("bot, ready")


async def load():
    """loads all the cogs in the cogs file using the bot.load_extension method."""
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f"cogs.{file[:-3]}")


async def main():
    """creates bot instance, loads cogs onto bot, and starts the bot.

    Once the Bot is created the load function adds all of the cogs
    in the cogs file onto the bot.

    THe bot.start method is short hand  coroutine for discord.Client.login() &
    discord.Client.Connect()

    login(): Logs in the client with the specified credentials and calls the setup_hook.
    Connect(): Creates a websocket connection that listens to messages from Discord.
    This is a loop that runs the entire event system (amoung other things).
    """
    await load()
    async with bot:
        token = "YOUR TOKEN HERE"
        await bot.start(token)

asyncio.run(main())  # Starting the event loop
