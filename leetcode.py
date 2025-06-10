import discord
from discord.ext import commands

from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

class Leetcode(commands.Cog):
    '''
    Any commands that relate to Leetcode problems and solutions.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Fetches a random Leetcode problem')
    async def leetcode(self, ctx):
        await ctx.send('This command will fetch a random Leetcode problem.')

        url = "https://leetcode.com/problemset/"
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")  # Run in background
        options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        button = driver.find_element(By.CSS_SELECTOR,
                                     "button.relative.inline-flex.items-center.justify-center.font-medium.transition-colors.focus-visible\\:outline-none.focus-visible\\:ring-1.focus-visible\\:ring-sd-ring.disabled\\:pointer-events-none.disabled\\:opacity-50.text-sd-foreground.hover\\:bg-sd-accent.hover\\:text-sd-accent-foreground.text-xs.rounded-full.h-8.p-2")
        button.click()
        driver.implicitly_wait(10)
        leetcode_problem = driver.current_url
        embed = discord.Embed(title='LeetCode Problem',
                              description='Here is a random LeetCode problem for you to solve.',
                             url = leetcode_problem)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leetcode(bot))