import csv
import json
import random

from discord.ext import commands


class General(commands.Cog):
    '''
    Any commands that are miscellaneous or do not fit in another cog.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.responses = json.load(open('/data/responses.json'))

        with open('/data/motivational_quotes.csv', 'r') as f:
            reader = csv.reader(f, delimiter=',')
            quotes = [quote for quote in list(reader)[0]]
            self.quotes = quotes

    @commands.command(help='Responds with a greeting')
    async def hello(self, ctx):
        responses = self.responses['hello']
        await ctx.send(f'{random.choice(responses)}')

    @commands.command(help='Responds with parting words')
    async def goodbye(self, ctx):
        responses = self.responses['goodbye']
        await ctx.send(f'{random.choice(responses)}')

    @commands.command(help='Responds with a motivational quote')
    async def motivate(self, ctx):
        responses = self.quotes
        await ctx.send(f'{random.choice(responses)}')

async def setup(bot):
    await bot.add_cog(General(bot))
