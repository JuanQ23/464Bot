import discord
from discord import app_commands
from discord.ext import commands
from typing import List


class UserSelectView(discord.ui.View):
    """The user select box that is sent to discord."""

    def __init__(self):
        super().__init__()
        self.value: list[discord.Member | discord.User]

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="search", min_values=1, max_values=3)
    async def my_user_users(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        self.value = select.values
        await interaction.response.send_message("Creating, should be quick..", delete_after=5)
        self.stop()


class Teams(commands.Cog):
    """A set of commands that are used to automate creation and deletion of A team category and teams."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.teamnum = 1

    @app_commands.command()
    @app_commands.default_permissions(manage_guild=True)
    async def createteamcategory(self, interaction: discord.Interaction):
        """creates a category for teams."""

        # error handling / keeping the type checker happy.
        if interaction.guild is None:
            await interaction.response.send_message("The guild appears to not be accessible by the bot. Possibly a permissions issue?")
            return

        cat = await interaction.guild.create_category(name="Teams")
        await interaction.response.send_message("Team category created, please run the /team command to populate the category with teams.", delete_after=10)
        await cat.move(beginning=True)

    @app_commands.command()
    @app_commands.default_permissions(manage_guild=True)
    async def team(self, interaction: discord.Interaction):
        """creates team voice and text channels."""

        # error handling / keeping the type hinter happy
        if interaction.guild is None:
            await interaction.response.send_message("the bot is not in any guilds")
            return
        if not isinstance(interaction.channel, discord.TextChannel):
            print("The interaction channel is not a text channel. Unable to send message. Please initiate command in text channel.")
            return

        category = discord.utils.get(
            interaction.guild.categories, name="Teams")
        if category is None:
            await interaction.response.send_message("unable to find the Teams Category. Please run the createTeams command.")
            return

        # sending view, collecting response.
        view = UserSelectView()
        await interaction.response.send_message(view=view)
        await view.wait()

        # create team voice and text channel.
        overwrites = {
            # users w/ default permission cannot read
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(
                read_messages=True)  # I can read (AKA server owner)
        }
        teammates = view.value

        text = await category.create_text_channel(name=f"Team {self.teamnum}", overwrites=overwrites)
        vc = await category.create_voice_channel(name=f"Team {self.teamnum}", overwrites=overwrites)
        self.teamnum += 1
        for member in teammates:
            if not isinstance(member, discord.Member):
                continue

            await text.set_permissions(target=member, read_messages=True, create_instant_invite=False)
            await vc.set_permissions(target=member,   read_messages=True, create_instant_invite=False)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        print(repr(interaction.channel))
        raise error

    async def on_error(self, interaction, error, /):
        print(repr(interaction.channel))
        raise error

    @commands.Cog.listener()
    async def on_ready(self):
        print("Teams cog loaded")


async def setup(bot):
    await bot.add_cog(Teams(bot))
