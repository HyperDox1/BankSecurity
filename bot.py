import discord
from discord.ext import commands, tasks
from itertools import cycle
import os
import asyncio
from dotenv import load_dotenv
import json

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
#intents.members = True

#flag = discord.MemberCacheFlags.none()
client = commands.Bot(command_prefix="!", intents=intents, help_command=None)
TOKEN = os.getenv("DISCORD_TOKEN")
bot_status = cycle(["Test out Python vulnerabilities!", "Be careful that your money stays safe..."])

@tasks.loop(seconds=120)
async def change_status():
    await client.change_presence(activity=discord.Game(next(bot_status)))

@client.event
async def on_ready():
    await client.tree.sync()
    print(f'Success! {client.user} is now connected!')
    change_status.start()

"""
@client.command()
async def sync(ctx):
    await client.tree.sync()
    if ctx.author.id == 502642668476825601:
        await client.tree.sync()
        print('Command tree synced.')
    else:
        await ctx.send(content='You must be the owner to use this command!')"""

@client.event
async def on_guild_join(guild):
    for member in guild.members:
        if member.bot == False:
            with open("cogs/jsonfiles/wallets.json", "r") as f:
                wallets = json.load(f)
                f.close()
            if member.id in wallets:
                continue
            wallets[member.id] = 0
            with open("cogs/jsonfiles/wallets.json", "w") as f:
                json.dump(wallets, f, indent=4)
                f.close()
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(
                'Hello! I am BankSecurity, simulating a banking system with built in Python vulnerabilities. Use !help '
                'To test these out and learn about them!'
            )
        break

@client.event
async def on_member_join(member):
    if member.bot == False:
        with open("cogs/jsonfiles/wallets.json", "r") as f:
            wallets = json.load(f)
            f.close()
        wallets[member.id] = 0
        with open("cogs/jsonfiles/wallets.json", "w") as f:
            json.dump(wallets, f, indent=4)
            f.close()
        with open("cogs/jsonfiles/bankrole.json", "r") as f:
            bank_role = json.load(f)
            f.close()
        join_role = discord.utils.get(member.guild.roles, name=bank_role[str(member.guild.id)])
        await member.add_roles(join_role)


@client.command()
async def joinrole(ctx, role: discord.Role):
    """
    Sets the role that is automatically added to users when they join the server.
    Parameters: Discord Role

    """
    with open("cogs/jsonfiles/bankrole.json", "r") as f:
        bank_role = json.load(f)
        f.close()
    bank_role[str(ctx.guild.id)] = str(role.name)
    with open("cogs/jsonfiles/autorole.json", "w") as f:
        json.dump(bank_role, f, indent=4)
        f.close()
    embed = discord.Embed(color=discord.Color.green())
    embed.add_field(name="Success!", value=f"The automatic role for this bank has been set to {role.mention}.")
    await ctx.send(embed=embed)

@client.command()
async def vulnerabilities(ctx):
    """
    Displays all the vulnerabilities implemented into the bot. Explains why they exist and how they function.
    Parameters: None

    """
    embed = discord.Embed(title="Vulnerabilities in BankSecurity's Commands")
    embed.add_field(
        name="!leaderboard",
        value="Description: Contains a string formatting vulnerability. The code uses Python's str.format() function "
              "and substitutes a class in for the given value. "
              "If users create a bank account with a key word (bank) inside curly braces, then the "
              "function will treat it as a class, allowing users to access internal attributes. This principle applies "
              "to objects as well. When "
              "the leaderboard command is called with such accounts, the value of these attributes will be processed "
              "and displayed in the leaderboard. \nHow to exploit: The account name `{bank.bankInfo}` "
              "accesses the `bankInfo` attribute of "
              "the class `BankAccount`, which contains a dictionary with all bank account passwords. The account name "
              "`{bank.name:>9999999999}` pads the attribute bank.name, the name of the account, with a large amount of "
              "whitespace, which overwhelms the bot's memory and performs a denial of service attack. The bot will "
              "crash if the leaderboard command is called with an account having this name. \nFixes: Filter out user "
              "input for special characters such as `{}` to ensure that users cannot inject code into the program. "
              "Another fix is to find an alternate method of achieving the desired function without substituting a "
              "class or using Python's string formatting function. "
    )
    embed.add_field(
        name="!acc",
        value="Description: Contains a string formatting vulnerability. The code uses Python's str.format() function and "
              "substitutes a class in for the given value. If users create a bank account and set the description to "
              "include a key word `bank` inside curly braces, then the function will treat it as a class, allowing users "
              "to access internal attributes. This principle applies to objects as well. "
              "When the `!acc` command is called on a bank account with a custom description"
              "set in this manner, the bot will process the value of the attributes and display them in an embed. "
              "\nHow to exploit: Setting the description to the string `{bank.bankInfo}` accesses the `bankInfo` attribute"
              " of the class `BankAccount`, which contains a dictionary with all bank account passwords. The description"
              "`{bank.override}` accesses the `override` attribute of the `BankAccount` class, which contains the value "
              "of a password allowing users to log into any bank account. \nFixes: Filter out user "
              "input for special characters such as `{}` to ensure that users cannot inject code into the program. "
              "Another fix is to find an alternate method of achieving the desired function without substituting a "
              "class or using Python's string formatting function."
    )
    embed.add_field(
        name="!ban",
        value="Description: Users can bypass role hierarchy checks due to mishandling user information. When guild " 
              "chunking is disabled for the bot (`intents.members = False` or `intents = discord.Intents.default()` "
              "in the code), it is unable to retrieve information about members in the server, such as roles, so moderators "
              "can ban people who are higher than them in the role hierarchy. \nHow to exploit: Turn off member intents"
              "for the bot. Then, give an account moderator permissions by giving the account a role that "
              "is regarded as a moderator by the bot. Give another account a role that is higher than the `moderator` "
              "role. With the moderator account, call the command `!ban` on the account that is above in the hierarchy."
              " The bot should successfully ban the other, regardless of their roles. Then, turn on member intents and "
              "attempt to do the same thing. The bot should not ban the other account, since it is able to access user "
              "information when guild chunking is on. \nFixes: If guild chunking is disabled in a bot, query the server "
              " for user information to ensure the bot can retrieve information about server members. This can be done "
              "by using the `guild.query_members()` function to get information about users in the server. "
    )
    await ctx.send(embed=embed)

@client.command()
async def help(ctx):
    """
    Displays BankSecurity's Help Menu

    """
    commands = [command.name for command in client.commands]
    embed = discord.Embed(title="BankSecurity's Help Menu")
    for command in commands:
        embed.add_field(name=command, value=client.get_command(command).help)
    embed.add_field(
        name="Additional Information",
        value="Created by HyperDox \nSource Code: https://github.com/HyperDox1/BankSecurity \nDiscord Contact: 1nOnlyHyperDox"
    )
    await ctx.send(embed=embed)

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with client:
        await load()
        await client.start(TOKEN)

asyncio.run(main())
