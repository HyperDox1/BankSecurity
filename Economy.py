import discord
from discord.ext import commands
import json
import random
import asyncio
from cogs.BankAccount.BankAccountClass import override, BankAccount

class Economy(commands.Cog):
    """
    Contains commands handling earning money and utilizes the BankAccount class to perform banking actions

    accounts.json --> maps user ids to how many accounts they have created (max is 3)
    userpass.json --> maps bank account names to their passwords
    wallets.json --> maps user ids to their wallet value

    """
    accFile = "cogs/jsonfiles/accounts.json"
    userpassFile = "cogs/jsonfiles/userpass.json"
    walletsFile = "cogs/jsonfiles/wallets.json"

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is ready.")

    @commands.guild_only()
    @commands.command(aliases=["create"])
    async def createAccount(self, ctx):
        """
        Creates a new bank account if user has not made one yet. Each user can make a max amount of 3 bank accounts

        """
        with open(self.accFile, "r") as f:
            accounts = json.load(f)
            f.close()
        with open(self.userpassFile, "r") as f:
            info = json.load(f)
            f.close()
        if str(ctx.author.id) in accounts:
            if accounts[str(ctx.author.id)] > 2:
                embed = discord.Embed(
                    title="Bank Accounts Limit Reached",
                    description="You have already made 3 bank accounts, which is the max amount. "
                                "You cannot make another one.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
        channel = await self.client.create_dm(ctx.author)
        await channel.send(
            content="Hello! To create your bank account, you must set a username and a password. "
                    "I will ask you in two different messages for a username and a password. "
                    "Set each by typing in your desired username/password in the DM. "
                    "Do not share these with anyone else."
        )
        await asyncio.sleep(1)
        def check(m):
            return m.channel == channel
        try:
            await channel.send(content="Set your username now:")
            username = await self.client.wait_for("message", check=check, timeout=60.0)
            await asyncio.sleep(1)
            if username.content in info.keys():
                await channel.send(content="That name is not available. Please try again to make an account.")
                return
            await channel.send(content="Username has successfully been set! \n Set your password now: ")
            password = await self.client.wait_for("message", check=check, timeout=60.0)
            await asyncio.sleep(1)
            if password.content.lower() == "override":
                await channel.send(content="That password is not available. Please try again to make an account.")
                return
            await channel.send(content="Password has been successfully set!")
        except asyncio.TimeoutError:
            await channel.send(content="Unable to create account, please try again.")
            return
        BankAccount.storeAccount(username.content, password.content)
        bankAccount = BankAccount(username.content)
        info[username.content] = password.content
        with open(self.userpassFile, "w") as f:
            json.dump(info, f, indent=4)
            f.close()
        if str(ctx.author.id) in accounts:
            accounts[str(ctx.author.id)] += 1
        else:
            accounts[str(ctx.author.id)] = 1
        with open(self.accFile, "w") as f:
            json.dump(accounts, f, indent=4)
            f.close()
        success_embed = discord.Embed(
            title="Success!",
            description="Your bank account has been created. Use !acc to view your account.",
            color=discord.Color.green()
        )
        success_embed.set_footer(text="Try running economy commands to earn money!", icon_url=None)
        await channel.send(embed=success_embed)

    async def CheckBankAccount(self, context, username: str):
        """
        Checks whether a bank account with a specific username exists

        Parameters:
        context --> ctx
        username --> str

        Returns:
        bool

        """

        with open(self.userpassFile, "r") as f:
            info = json.load(f)
            f.close()
        if username not in info.keys():
            embed = discord.Embed(
                title="Bank Account Doesn't Exist",
                description="No bank account exists with that username. "
                            "Please check that you typed the username in correctly.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return False
        return True

    async def login(self, user, accName: str):
        """
        Implements a login system into a bank account with a given username

        Parameters:
        user --> discord.Member
        accName --> str

        Returns:
        bool

        """
        channel = await self.client.create_dm(user)
        def check(m):
            return m.channel == channel
        try:
            await channel.send(content=f"{accName}'s Bank Account")
            await asyncio.sleep(1)
            await channel.send(content="Enter password to login, or type `override` to access the account:")
            await asyncio.sleep(0.5)
            password = await self.client.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await channel.send(content="Unable to login, please try again.")
            return
        with open(self.userpassFile, "r") as f:
            info = json.load(f)
            f.close()
        if password.content == info[accName]:
            embed = discord.Embed(
                title="Login Attempt Successful",
                description=f"You have successfully logged into {accName}'s account!",
                color=discord.Color.green()
            )
            await channel.send(embed=embed)
            return True
        elif password.content.lower() == "override":
            await channel.send(content="Enter the override password:")
            await asyncio.sleep(0.5)
            override_pass = await self.client.wait_for("message", check=check, timeout=60.0)
            if override_pass.content == override:
                embed = discord.Embed(
                    title="Override Successful",
                    description=f"You have successfully logged into {accName}'s account!",
                    color=discord.Color.green()
                )
                await channel.send(embed=embed)
                return True
            embed = discord.Embed(
                title="Override Unsuccessful",
                description=f"Unable to login to {accName}'s account.",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)
            return False
        embed = discord.Embed(
            title="Login Attempt Unsuccessful",
            description=f"Unable to login to {accName}'s account.",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
        return False

    @commands.guild_only()
    @commands.command(aliases=["acc"])
    async def viewAccount(self, ctx, accName: str = None):
        if accName is None:
            await ctx.send("You need to include an account name in this command!")
        elif await self.CheckBankAccount(ctx, accName):
            await ctx.send(embed=BankAccount(accName).account())

    @commands.guild_only()
    @commands.command(aliases=["close"])
    async def closeAccount(self, ctx, accName: str=None):
        if accName is None:
            await ctx.send("You need to include an account name in this command!")
        elif await self.CheckBankAccount(ctx, accName):
            if await self.login(ctx.author, accName):
                try:
                    BankAccount.deleteAccount(accName)
                except Exception as e:
                    log = discord.utils.get(ctx.guild.channels, name="log-channel")
                    await ctx.send(f"Unable to close {accName}'s bank account.")
                    await log.send(f"An error occurred when trying to close {accName}'s account: {e}")
                else:
                    with open(self.userpassFile, "r") as f:
                        userpass = json.load(f)
                        f.close()
                    del userpass[accName]
                    with open(self.userpassFile, "w") as f:
                        json.dump(userpass, f, indent=4)
                        f.close()
                    await ctx.send(f"Successfully closed {accName}'s bank account.")
            else:
                await ctx.send(f"Unable to close {accName}'s bank account.")


    @commands.guild_only()
    @commands.command(aliases=["wall"])
    async def wallet(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        with open("cogs/jsonfiles/wallets.json", "r") as f:
            wallets = json.load(f)
            f.close()
        embed = discord.Embed(
            title=f"{member.name}'s Wallet",
            description="The current wallet value of this user.",
            color=discord.Color.green()
        )
        embed.add_field(name="Current Wallet Value:", value=f"${wallets[str(member.id)]}")
        embed.set_footer(text="Want to earn more money? Try running some economy based commands!", icon_url=None)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(aliases=["leaderboard"])
    async def viewLeaderboard(self, ctx):
        bank = BankAccount.leaderboard()
        await ctx.send(bank)

    @commands.guild_only()
    @commands.command(aliases=["description"])
    async def setDescription(self, ctx, accName: str):
        if await self.CheckBankAccount(ctx, accName):
            if await self.login(ctx.author, accName):
                await BankAccount(accName).description(ctx, self.client)
            else:
                await ctx.send("Unable to set custom message, please try again.")

    @commands.guild_only()
    @commands.command(aliases=["dep"])
    async def deposit(self, ctx, accName: str, amount: int):
        if await self.CheckBankAccount(ctx, accName):
            if await self.login(ctx.author, accName):
                await BankAccount(accName).deposit(ctx, amount)
            else:
                await ctx.send(f"Unable to deposit ${amount} into {accName}'s account.")

    @commands.guild_only()
    @commands.command(aliases=["wd"])
    async def withdraw(self, ctx, accName: str, amount: int):
        if await self.CheckBankAccount(ctx, accName):
            if await self.login(ctx.author, accName):
                await BankAccount(accName).withdraw(ctx, amount)
            else:
                await ctx.send(f"Unable to withdraw ${amount} from {accName}'s account.")

    @commands.guild_only()
    @commands.command()
    async def transfer(self, ctx, acc1: str, acc2: str, amount: int):
        if await self.CheckBankAccount(ctx, acc1) and await self.CheckBankAccount(ctx, acc2):
            if await self.login(ctx.author, acc1):
                await BankAccount(acc1).transferMoney(ctx, acc2, amount)
            else:
                await ctx.send(content=f"Unable to transfer ${amount} from {acc1}'s account to {acc2}'s account.")

    @commands.command(aliases=["ban"])
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, userid: int, reason: str=None):
        print(ctx.guild.members)
        print(ctx.guild.chunked)
        member = ctx.guild.get_member(userid)
        author = ctx.author
        channel = discord.utils.get(ctx.guild.channels, name="log-channel")
        if member is not None:
            if author == member:
                await ctx.send("You cannot ban yourself.")
            elif author.top_role.position <= member.top_role.position or member == ctx.guild.owner:
                await ctx.send("Unable to ban that user due to the role hierarchy of the bank.")
            elif ctx.guild.me.top_role <= member.top_role or member == ctx.guild.owner:
                await ctx.send("Unable to ban that user due to lack of permissions.")
            else:
                try:
                    await ctx.guild.ban(member)
                except discord.Forbidden:
                    await ctx.send("I do not have permissions to ban that member.")
                except Exception as e:
                    await channel.send(f"`Unable to ban {member.mention}: {e}`")
                    await ctx.send(f"Failed to ban {member.mention}.")
                else:
                    with open(self.walletsFile, "r") as f:
                        wallets = json.load(f)
                        f.close()
                    embed = discord.Embed(title="Success!", color=discord.Color.green())
                    embed.add_field(
                        name="Banned:",
                        value=f"{member.mention} has been banned from the bank by {ctx.author.mention}.",
                        inline=False
                    )
                    embed.add_field(name="Reason:", value=reason, inline=False)
                    await ctx.send(embed=embed)
                    wallets[str(userid)] = 0
                    with open(self.walletsFile, "w") as f:
                        json.dump(wallets, f, indent=4)
                        f.close()
        else:
            user = discord.Object(id=userid)
            try:
                await ctx.guild.ban(user)
            except discord.NotFound:
                await ctx.send("That user doesn't exist.")
            except discord.Forbidden:
                await ctx.send("I am missing permissions to ban that user.")
            except Exception as e:
                await channel.send(f"`Unable to ban that user {userid}: {e}`")
                await ctx.send(f"Failed to ban user {userid}")
            else:
                embed = discord.Embed(title="Success!", color=discord.Color.green())
                embed.add_field(
                    name="Banned:",
                    value=f"User {userid} has been banned from the bank by {ctx.author.mention}.",
                    inline=False
                )
                embed.add_field(name="Reason:", value=reason, inline=False)
                await ctx.send(embed=embed)

    @commands.command(aliases=["unban"])
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True, kick_members=True)
    @commands.has_permissions(ban_members=True, kick_members=True)
    async def unban_user(self, ctx, userid: int):
        user = discord.Object(id=userid)
        try:
            await ctx.guild.unban(user)
        except Exception as e:
            channel = discord.utils.get(ctx.guild.channels, name="log-channel")
            await channel.send(f"`Unable to unban <@{userid}>: {e}`")
        else:
            embed = discord.Embed(title="Success!", color=discord.Color.green())
            embed.add_field(
                name="Unbanned:",
                value=f"<@{userid}> has been unbanned from the bank by {ctx.author.mention}.",
                inline=False
            )
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def work(self, ctx):
        with open("cogs/jsonfiles/wallets.json", "r") as f:
            wallets = json.load(f)
        author = ctx.author.id
        amount = random.randint(100, 300)
        wallets[str(author)] += amount
        with open("cogs/jsonfiles/wallets.json", "w") as f:
            json.dump(wallets, f, indent=4)
            f.close()
        embed = discord.Embed(
            title="Nice job!",
            description="After a long shift, here's what you earned!",
            color=discord.Color.green()
        )
        embed.add_field(name="Earnings: ", value=f"${amount}", inline=False)
        embed.add_field(name="New Wallet Balance: ", value=f"${wallets[str(author)]}")
        embed.set_footer(text="Want more? Run this command again, or try some others!", icon_url=None)
        await ctx.send(embed=embed)

    @commands.guild_only()
    #@commands.cooldown(1, per=5)
    @commands.command()
    async def beg(self, ctx):
        author = ctx.author.id
        with open("cogs/jsonfiles/wallets.json", "r") as f:
            wallets = json.load(f)
            f.close()
        cur_wallet = wallets[str(author)]
        amount = random.randint(-10, 50)
        new_wallet = cur_wallet + amount
        if new_wallet < cur_wallet:
            if wallets[str(author)] > 0:
                wallets[str(author)] += amount
            with open("cogs/jsonfiles/wallets.json", "w") as f:
                json.dump(wallets, f, indent=4)
                f.close()
            embed = discord.Embed(
                title="Oh No! - You've been robbed!",
                 description="A group of robbers saw an opportunity in taking advantage of you. ",
                 color=discord.Color.red()
            )
            embed.add_field(name="New Wallet Balance:", value=f"${new_wallet}", inline=False)
            embed.set_footer(text="Should probably beg in a nicer part of town...", icon_url=None)
            await ctx.send(embed=embed)
        elif new_wallet > cur_wallet:
            wallets[str(ctx.author.id)] += amount
            with open("cogs/jsonfiles/wallets.json", "w") as f:
                json.dump(wallets, f, indent=4)
                f.close()
            embed = discord.Embed(
                title="Oh Nice!",
                description="Some kind souls out there have given you what they could.",
                color=discord.Color.green()
            )
            embed.add_field(name="New Wallet Balance:", value=f"${new_wallet}", inline=False)
            embed.set_footer(text="Want more? Run this command again, or try some others!", icon_url=None)
            await ctx.send(embed=embed)
        elif new_wallet == cur_wallet:
            wallets[str(ctx.author.id)] += amount
            with open("cogs/jsonfiles/wallets.json", "w") as f:
                json.dump(wallets, f, indent=4)
                f.close()
            embed = discord.Embed(
                title="Aw, that sucks!",
                description="Looks like begging didn't get you anywhere today.",
                color=discord.Color.light_gray()
            )
            embed.add_field(name="New Wallet Balance:", value=f"${new_wallet}", inline=False)
            embed.set_footer(text="Want more? Run this command again, or try some others!", icon_url=None)
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def steal(self, ctx, member: discord.Member):
        with open("cogs/jsonfiles/wallets.json", "r") as f:
            wallets = json.load(f)
        author = ctx.author.id
        steal_probability = random.randint(0, 1)
        if member.bot == True:
            await ctx.send("Come on! You can't steal from a bot...")
        elif wallets[str(member.id)] == 0:
            await ctx.send(f"You cannot steal from that user! {member.name} has no money!")
        elif steal_probability == 1:
            amount = random.randint(10, 100)
            wallets[str(author)] += amount
            wallets[str(member.id)] -= amount
            with open("cogs/jsonfiles/wallets.json", "w") as f:
                json.dump(wallets, f, indent=4)
                f.close()
            await ctx.send(f"{ctx.author.mention}, You have stolen ${amount} from "
                           f"{member.mention}! Be sure to keep it safe as they may be looking for revenge...")
        else:
            await ctx.send("Uh oh...You did not get to steal from this user, better luck next time!")

async def setup(client):
    await client.add_cog(Economy(client))