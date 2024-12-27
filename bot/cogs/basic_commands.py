from discord.ext import commands

class BasicCommands(commands.Cog):

    def __init__(self) -> None:
        super().__init__()


    @commands.command(name="test")
    async def test(self, ctx, *, arg):
        await ctx.send(arg)


    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send('pong')

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))