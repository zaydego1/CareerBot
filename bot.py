import os
import asyncio

from discord.ext import commands
from secret import credentials_dict
from discord import Intents

intents = Intents.default()
intents.message_content = True  # For command processing
intents.members = True  # For member events
intents.presences = True

bot = commands.Bot(command_prefix='-', intents=intents)

@bot.event
async def on_ready():
    print('Bot is ready.')

@bot.event
async def on_member_join(member):
    print(f'{member} has joined the server.')

@bot.event
async def on_member_remove(member):
    print(f'{member} has left the server.')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid command used. Use -help to see valid commands.')
    else:
        raise error

@bot.command(help='Removes {num} messages from the chat')
async def clean(ctx, amount: int):
    await ctx.channel.purge(limit=amount)

@clean.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify an amount of messages to delete.')

@bot.command(help='Enables {title} category')
async def enable(ctx, ext):
    await ctx.send(f'Category "{ext.title()}" enabled.')
    await bot.load_extension(f'cogs.{ext}')

@bot.command(help='Disables {title} category')
async def disable(ctx, ext):
    await ctx.send(f'Category "{ext.title()}" disabled.')
    await bot.unload_extension(f'cogs.{ext.lower()}')

@bot.command(help='Reenables all categories')
async def reset(ctx):
    await ctx.send(f'Reset to factory settings.')
    ext_list = [ext for ext in os.listdir('/Users/isaiahjones/PycharmProjects/CareerBot/cogs')]
    for ext in ext_list:
        await bot.load_extension(f'cogs.{ext[:-3]}')

def main():
    async def runner():
        await bot.load_extension('cogs.general')
        await bot.load_extension('cogs.query')
        await bot.load_extension('cogs.database')
        await bot.load_extension('cogs.leetcode')
        await bot.start(credentials_dict['token'])
    asyncio.run(runner())