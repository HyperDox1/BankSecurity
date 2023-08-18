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
client = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")
bot_status = cycle(["Test out Python vulnerabilities!", "Be careful that your money stays safe..."])

@tasks.loop(seconds=120)
async def change_status():
    await client.change_presence(activity=discord.Game(next(bot_status)))

@client.event
async def on_ready():
    #await client.tree.sync()
    print(f'Success! {client.user} is now connected!')
    change_status.start()

"""@client.command()
async def sync(ctx):
    if ctx.author.id == 502642668476825601:
        await client.tree.sync()
        print('Command tree synced.')
    else:
        await ctx.send(content='You must be the owner to use this command!') """

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

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with client:
        await load()
        await client.start(TOKEN)

asyncio.run(main())