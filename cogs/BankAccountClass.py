import discord
from discord.ext import commands
import json
import asyncio

override = "superspecialpassword"

class BankAccount():
    """
    Stores a bank account with all related information (username, password, balance, description)
    as well information about all accounts (that can be leaked)

    """
    bankFile = "cogs/BankAccount/BankInformation/bank.json"
    walletsFile = "cogs/jsonfiles/wallets.json"
    name = "FastMoney Bank"

    with open(bankFile, "r") as f:
        bankInfo = json.load(f)
        f.close()

    def __init__(self, name: str):
        self.name = name
        self.password = BankAccount.bankInfo[name]["Password"]
        self.balance = BankAccount.bankInfo[name]["Balance"]
        self.message = BankAccount.bankInfo[name]["Description"]

    @classmethod
    def storeAccount(cls, name: str, password: str):
        """
        Stores information about a bank account's password and balance when it is first created so that it can be
        accessed by the BankAccount class in the future

        Parameters:
        name --> str
        password --> str

        Returns:
        None

        """
        with open(cls.bankFile, "r") as f:
            bank = json.load(f)
            f.close()
        bank[name] = {}
        bank[name]["Password"] = password
        bank[name]["Balance"] = 0
        bank[name]["Description"] = "No description"
        cls.bankInfo = bank
        with open(cls.bankFile, "w") as f:
            json.dump(bank, f, indent=4)
            f.close()

    @classmethod
    def deleteAccount(cls, name: str):
        """
        Deletes a bank account with a given name and all related information.

        Parameters:
        name --> str

        Returns:
        None

        """
        del cls.bankInfo[name]
        with open(cls.bankFile, "w") as f:
            json.dump(cls.bankInfo, f, indent=4)
            f.close()
    @classmethod
    def leaderboard(cls):
        """
        ***Contains a str.format() Vulnerability

        Displays the top 10 bank accounts with the highest balance.

        Parameters:
        None

        Returns:
        str
            contains a header and the account names separated by \n character

        """
        top = ["Leaderboard (by balance):"]
        names = []
        for name in cls.bankInfo:
            names.append(name)
        topUser = 0
        while len(top) < 11 and len(top) < len(cls.bankInfo)+1:
            for i in range(len(names)-1):
                if cls.bankInfo[names[i+1]]["Balance"] > cls.bankInfo[names[i+1]]["Balance"]:
                    topUser = i+1
            if len(names) == 1:
                top.append(names.pop(0))
            else:
                top.append(names.pop(topUser))
        board = "\n".join(top).format(bank=cls)
        return f"```{board}```"

    def account(self):
        """
        ***Contains str.format() Vulnerability***

        Displays the balance and custom message of a bank account with a given username

        Parameters:
        ctx --> discord.Context
        accName --> str

        Returns:
        discord.Embed
            An embed containing the information about that user's bank account

        """
        embed = discord.Embed(
            title=f"{self.name}'s Bank Account",
            description="The current balance of this user.",
            color=discord.Color.green()
        )
        embed.add_field(name="Current Balance:", value=f"${self.balance}")
        embed.add_field(name="Description:", value=self.message.format(bank=BankAccount))
        embed.set_footer(text="Want to earn more money? Try running some economy based commands!", icon_url=None)
        return embed

    async def description(self, ctx, client):
        """
        Allows a user to set a description for a certain bank account once he/she logs in

        Parameters:
        ctx --> discord.Context
        client --> discord.Client
            The discord client/bot object

        Returns:
        None

        """
        channel = await client.create_dm(ctx.author)
        try:
            await channel.send(content=f"Set a description for {self.name}'s account when the !acc command is called:")
            await asyncio.sleep(0.5)
            def check(m):
                return m.channel == channel
            description = await client.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await channel.send(content="Unable to set description, please try again.")
            await ctx.send(content="Unable to set description, please try again.")
            return
        BankAccount.bankInfo[self.name]["Description"] = description.content
        self.message = description.content
        with open(self.bankFile, "w") as f:
            json.dump(BankAccount.bankInfo, f, indent=4)
            f.close()
        embed = discord.Embed(
            title="Description set!",
            description=f"{self.name}'s description has been successfully set. Use !acc to view this message.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)
        if channel != ctx.channel:
            await ctx.send(embed=embed)

    async def deposit(self, ctx, amount: int):
        """
        Deposits a certain amount of money into a bank account

        Parameters:
        accName --> str
            The name of the bank account
        amount --> int
            The amount of money to be deposited in the bank account

        Returns:
        None

        """
        with open(self.walletsFile, "r") as f:
            wallets = json.load(f)
            f.close()
        author = ctx.author.id
        if amount > wallets[str(author)]:
            await ctx.send("You do not have that much money!")
        elif amount < 0:
            await ctx.send("You cannot deposit a negative amount of money!")
        else:
            wallets[str(author)] -= amount
            BankAccount.bankInfo[self.name]["Balance"] += amount
            self.balance += amount
            with open(self.walletsFile, "w") as f:
                json.dump(wallets, f, indent=4)
                f.close()
            with open(self.bankFile, "w") as f:
                json.dump(BankAccount.bankInfo, f, indent=4)
                f.close()
            await ctx.send(f"Successfully deposited ${amount} into {self.name}'s bank account. ")

    async def withdraw(self, ctx, amount: int):
        """
        Withdraws a certain amount of money from a bank account

        Parameters:
        accName --> str
            The bank account to withdraw money from
        amount --> int
            The amount of money to be withdrawn from the bank account

        Returns:
        None

        """
        with open(self.walletsFile, "r") as f:
            wallets = json.load(f)
            f.close()
        author = ctx.author.id
        if amount > BankAccount.bankInfo[self.name]["Balance"]:
            await ctx.send(f"{self.name}'s account does not have that much money!")
        elif amount < 0:
            await ctx.send("You cannot withdraw a negative amount of money!")
        else:
            BankAccount.bankInfo[self.name]["Balance"] -= amount
            wallets[str(author)] += amount
            self.balance -= amount
            with open(self.walletsFile, "w") as f:
                json.dump(wallets, f, indent=4)
                f.close()
            with open(self.bankFile, "w") as f:
                json.dump(BankAccount.bankInfo, f, indent=4)
                f.close()
            await ctx.send(f"Successfully withdrawn ${amount} from {self.name}'s bank account.")

    async def transferMoney(self, ctx, otherAccount: str, amount: int):
        """
        Transfers money from one bank account to another

        Parameters:
        ctx --> discord.Context
        otherAccount --> str
            The bank account that will receive the money
        amount --> int

        Returns:
        None

        """
        if amount > BankAccount.bankInfo[self.name]["Balance"]:
            await ctx.send(f"{self.name}'s account does not have that much money!")
        elif amount < 0:
            await ctx.send("Invalid amount.")
        else:
            BankAccount.bankInfo[self.name]["Balance"] -= amount
            BankAccount.bankInfo[otherAccount]["Balance"] += amount
            self.balance -= amount
            with open(self.bankFile, "w") as f:
                json.dump(BankAccount.bankInfo, f, indent=4)
                f.close()
        await ctx.send(f"Successfully transferred ${amount} from {self.name}'s account to {otherAccount}'s account.")