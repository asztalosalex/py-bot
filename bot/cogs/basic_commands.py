from discord.ext import commands

class BasicCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()



async def setup(bot):
    await bot.add_cog(BasicCommands(bot))