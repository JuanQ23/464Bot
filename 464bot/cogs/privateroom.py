import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from typing import List, Union

async def create_channels(interaction: discord.Interaction, member: discord.Member):
    
    #error handling
    if interaction.guild is None:
        return
    
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.guild.default_role: discord.PermissionOverwrite(create_instant_invite=False),
        # users w/ default permission cannot read
        interaction.guild.me: discord.PermissionOverwrite(read_messages=True),  # I can read (AKA server owner)
        member: discord.PermissionOverwrite(read_messages=True)  # the individual student can read.
    }
    member_name = member.nick or member.name

    category = await interaction.guild.create_category(name=member_name, overwrites=overwrites)

    await category.create_text_channel(name=f"private")
    await category.create_voice_channel(name=f"private voice")
    return category

async def delete_groups(category: discord.CategoryChannel):
    channels = category.channels
    for channel in channels:
        await channel.delete()

    await category.delete()


class UserSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value: list[discord.Member | discord.User]
        
    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="search", min_values=1, max_values=3)
    async def my_user_users(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        self.value = select.values
        await interaction.response.send_message("Creating, should be quick..", delete_after=5)
        self.stop()

class ChannelSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value: List[app_commands.AppCommandChannel| app_commands.AppCommandThread]

    # @ui.select(cls=type_we_want, **other_things)
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="search", min_values=1, max_values=20)
    async def my_user_channels(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        self.value = select.values
        await interaction.response.send_message("processing, please wait", delete_after=5)
        self.stop()

class PrivateRooms(commands.Cog):
    """A set of commands that are used to automate creation and deletion of private text and voice channels between a student and their professor"""

    def __init__(self, bot: commands.Bot):

        self.bot = bot
        self.categories: list[discord.CategoryChannel] = []

    @commands.is_owner()
    @app_commands.command()
    async def create(self, interaction: discord.Interaction):
        """Creates private categories, private text channels, private voice channels for each student"""

        await interaction.response.defer(thinking=True)

        #error handling
        if interaction.guild is None:
            await interaction.response.send_message("The guild appears to not be accessible by the bot. Possibly a permissions issue?")
            return
        
        members = interaction.guild.members
        category_names = [category.name for category in interaction.guild.categories]
        for member in members:
            if member.nick in category_names:
                continue
            elif member.name in category_names:
                continue
            await create_channels(interaction, member)

        await interaction.followup.send("done")
    
    @commands.is_owner()     
    @app_commands.command()
    async def destroy(self, interaction: discord.Interaction):
        """destroy selected categories, channels will not work"""
        
        #error handling
        if interaction.guild is None:
            await interaction.response.send_message("The guild appears to not be accessible by the bot. Possibly a permissions issue?")
            return
        if not isinstance(interaction.channel, discord.TextChannel):
            print("the channel in question is not a text")
            return
        
        #send view
        view = ChannelSelectView()
        await interaction.response.send_message(view=view)
        channel:discord.TextChannel = interaction.channel
        await view.wait()

        #collect response
        to_delete = view.value
        categories = [await element.fetch() for element in to_delete if element.type == discord.ChannelType.category]
        
        
        
        async with channel.typing():
            for category in categories:
                if isinstance(category, discord.CategoryChannel):
                    await delete_groups(category)
    
    @commands.is_owner()
    @app_commands.command()
    async def destroy_all_except(self, interaction: discord.Interaction):
        """Destroy all except that selected categories."""
        
        #error handling
        if interaction.guild is None:
            await interaction.response.send_message("The guild appears to not be accessible by the bot. Possibly a permissions issue?")
            return
        if not isinstance(interaction.channel, discord.TextChannel):
            print("the channel in question is not a text")
            return

        #sending view, waiting for response.
        view: ChannelSelectView = ChannelSelectView()
        await interaction.response.send_message(view=view)
        await view.wait()
        
        #collecting response. creating list of categories to be saved.
        to_delete = view.value
        categories = [await element.fetch() for element in to_delete if element.type == discord.ChannelType.category]
        channel: discord.TextChannel = interaction.channel

        #deleting all other categories.
        async with channel.typing():
            for category in interaction.guild.categories:
                if category in categories:
                    continue
                else:
                    await delete_groups(category)
    
    @commands.is_owner()
    @app_commands.command()
    async def createteamcategory(self, interaction: discord.Interaction):
        """creates a category for teams."""
    
        #error handling
        if interaction.guild is None:
            await interaction.response.send_message("The guild appears to not be accessible by the bot. Possibly a permissions issue?")
            return

        cat = await interaction.guild.create_category(name="Teams")
        await interaction.response.send_message("Team category created, please run the /team command to populate the category with teams.", delete_after=10)        
        await cat.move(beginning = True)
    
    @commands.is_owner()
    @app_commands.command()
    async def team(self, interaction: discord.Interaction):
        """creates team voice and text channels."""
        
        #error handling
        if interaction.guild is None:
            await interaction.response.send_message("the bot is not in any guilds")
            return
        if not isinstance(interaction.channel, discord.TextChannel):
            print("The interaction channel is not a text channel. Unable to send message. Please initiate command in text channel.")
            return
        
        category = discord.utils.get(interaction.guild.categories, name="Teams")
        if category is None:
            await interaction.response.send_message("unable to find the Teams Category. Please run the createTeams command.")
            return
        

        view = UserSelectView()
        await interaction.response.send_message(view=view)
        await view.wait()


        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), # users w/ default permission cannot read
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True)  # I can read (AKA server owner)
            }

        teammates = view.value
        text = await category.create_text_channel(name="Team 1", overwrites=overwrites)
        vc = await category.create_voice_channel(name="Team 1", overwrites=overwrites)
        
        for member in teammates:
            if not isinstance(member, discord.Member):
                continue
            
            await text.set_permissions(target=member, read_messages=True, create_instant_invite=False)
            await vc.set_permissions(target=member, read_messages=True, create_instant_invite= False)

        

    async def cog_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        print(repr(interaction.channel))
        raise error


    async def on_error(self, interaction, error, /):
        print(repr(interaction.channel))
        raise error


    @commands.Cog.listener()
    async def on_member_update(self, before:discord.Member, after: discord.Member):
        if before.nick != after.nick:
            print("A nickname update has been detected")
            display_name = before.nick or before.name            
            category = discord.utils.get(after.guild.categories, name=display_name)
            if category is None:
                return
            
            name_update = after.nick or after.name
            await category.edit(name=name_update)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tools cog loaded")

async def setup(bot):
    await bot.add_cog(PrivateRooms(bot))