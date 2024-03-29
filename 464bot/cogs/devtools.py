"""A file meant to hold the DevTools Cog which responsible for maintance.
Raises:
    error: Error raised within any command.
"""
from discord.ext import commands
from discord import app_commands


class DevTools(commands.Cog):
    """The Cog that will be used for command maintanance."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="sync")
    # setting command permission.
    @app_commands.default_permissions(manage_guild=True)
    async def sync(self, ctx):
        """syncing commands with discord API"""

        await self.bot.tree.sync()
        await ctx.send("commands synced")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """listening for errors with commands"""
        raise error

    @commands.Cog.listener()
    async def on_ready(self):
        """event that is called when the cog is ready."""
        print("CommandTools cog loaded")


async def setup(bot):
    """This function adds the cog to the bot so that it it's command can be ran and the
    events can be listned for."""
    await bot.add_cog(DevTools(bot))
