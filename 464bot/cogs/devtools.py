import asyncio

import discord

from discord import app_commands
from discord.ext import commands


class DevTools(commands.Cog):
    """set of commands that are used to maintain and manage the commands across all servers."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="sync")
    async def sync(self, ctx):
        """syncing commands with discord API"""

        # TODO: find out why sync takes much longer with slash commands.
        await self.bot.tree.sync()
        await ctx.send("commands synced")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        raise error

    @commands.Cog.listener()
    async def on_ready(self):
        print("CommandTools cog loaded")


async def setup(bot):
    await bot.add_cog(DevTools(bot))
