import discord
from discord import app_commands
from discord.ext import commands
from typing import List


async def create_channels(interaction: discord.Interaction, member: discord.Member):
    """Helper function that assists in the create function."""
    
    # error handling / keeping the type checker happy.
    if interaction.guild is None:
        return

    # permissions: The default_role cannot see read anything in the Category, or create invites.
    # The Person who ran the command can see the category and the member passed in can see the category.
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, create_instant_invite=False),
        interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
        member: discord.PermissionOverwrite(read_messages=True)
    }

    # creating category and adding channels to the category. 
    # in discord the category shows up as a 'folder'.
    member_name = member.nick or member.name
    category = await interaction.guild.create_category(name=member_name, overwrites=overwrites)
    await category.create_text_channel(name="private text")
    await category.create_voice_channel(name="private voice")
    return category


async def delete_groups(category: discord.CategoryChannel):
    """A helper that assists in the deletetion of categories along with their channels. kind of like recursively delete a folder on windows."""

    channels = category.channels
    for channel in channels:
        await channel.delete()

    await category.delete()


class ChannelSelectView(discord.ui.View):
    """the channel select box that is sent to discord."""

    def __init__(self):
        super().__init__()
        
        # a attribute that will hold the user selected channels.
        self.value: List[app_commands.AppCommandChannel |
                         app_commands.AppCommandThread]

    # The function that is called when the user selects from the ChannelSelect menu.
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="search", min_values=1, max_values=20)
    async def my_user_channels(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        self.value = select.values #storing user selected items.
        await interaction.response.send_message("processing, please wait", delete_after=5)
        self.stop() #stopping the interaction so that View.wait() can stop waiting.


class PrivateRooms(commands.Cog):
    """A set of commands that are used to automate creation and deletion of private text and voice channels between a student and their professor"""

    def __init__(self, bot: commands.Bot):

        self.bot = bot
        self.categories: list[discord.CategoryChannel] = []

    @app_commands.command()
    @app_commands.default_permissions(manage_guild=True) #setting command permission.
    async def create(self, interaction: discord.Interaction):
        """Creates private categories, private text channels, private voice channels for each student"""

        await interaction.response.defer(thinking=True)

        # error handling / keeping the type checker happy.
        if interaction.guild is None:
            await interaction.response.send_message("The guild appears to not be accessible by the bot. Possibly a permissions issue?")
            return

        # Create categories and channels for each member. If the category is already there, then skip its creation
        members = interaction.guild.members
        category_names = [category.name for category in interaction.guild.categories]
        for member in members:
            if member.nick in category_names:
                continue
            elif member.name in category_names:
                continue
            await create_channels(interaction, member)

        await interaction.followup.send("done. ctrl+shift+a to collapse")

    @app_commands.command()
    @app_commands.default_permissions(manage_guild=True) #setting command permission.
    async def destroy(self, interaction: discord.Interaction):
        """destroy selected categories, channels will not work"""

        # error handling / keeping the type checker happy.
        if interaction.guild is None:
            await interaction.response.send_message("The guild appears to not be accessible by the bot. Possibly a permissions issue?")
            return
        if not isinstance(interaction.channel, discord.TextChannel):
            print("the channel in question is not a text")
            return

          
        view = ChannelSelectView()# creating view,
        await interaction.response.send_message(view=view) #sending view
        await view.wait() #waiting for response
        to_delete = view.value #collecting response. which is a list of channels selected by user.


        # ugly one liner that converts partial channel objects into their full formed respective object.
        # categories is a list of categories selected by the user via the select view sent to discord.
        categories = [await element.fetch() for element in to_delete if element.type == discord.ChannelType.category]
        
        # enabling the typing indicator while deleting channels (i.e "I am a bot is typing"). 
        # This is achived via the 'async with' context manager.
        channel = interaction.channel
        async with channel.typing():
            for category in categories:
                if isinstance(category, discord.CategoryChannel):
                    await delete_groups(category)

    @app_commands.command()
    @app_commands.default_permissions(manage_guild=True) #setting command permission.
    async def destroy_all_except(self, interaction: discord.Interaction):
        """Destroy all except that selected categories."""

        # error handling / keeping the type checker happy.
        if interaction.guild is None:
            await interaction.response.send_message("The guild appears to not be accessible by the bot. Possibly a permissions issue?")
            return
        if not isinstance(interaction.channel, discord.TextChannel):
            print("the channel in question is not a text")
            return

        # sending view, waiting for response, collecting response. 
        view: ChannelSelectView = ChannelSelectView()
        await interaction.response.send_message(view=view)
        await view.wait()
        to_save = view.value

        # ugly one liner that converts partial channel objects into their full formed respective object.
        # categories is a list of categories selected by the user via the select view sent to discord.
        categories = [await element.fetch() for element in to_save if element.type == discord.ChannelType.category]

        # deleting all other categories that were not selected.
        channel: discord.TextChannel = interaction.channel
        async with channel.typing():
            for category in interaction.guild.categories:
                if category in categories:
                    continue
                else:
                    await delete_groups(category)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """on_member_update listens for the event the folliwing things change:
        *nickname 
        *roles 
        *pending 
        *timeout
        *guild avatar 

        This functions monitors for changes in Nickname and updates the category to nickname. If there is a change in nickname then it changes the students category name to 
        
        1) the new nickname, if its not None
        2) if nickname is None, then it changes it their name.
         
        Args:
            before (discord.Member): The Member object before the change..
            after (discord.Member): The Member object after the change.
        """
        if before.nick != after.nick:
            print("A nickname update has been detected")
            display_name = before.nick or before.name
            category = discord.utils.get(
                after.guild.categories, name=display_name)
            if category is None:
                return

            name_update = after.nick or after.name
            await category.edit(name=name_update)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tools cog loaded")


async def setup(bot):
    """This function adds the cog to the bot so that it it's command can be ran and the events can be listned for."""
    await bot.add_cog(PrivateRooms(bot))
