import os

import pandas as pd
import pickle
import sqlite3
import urllib.request
import discord

from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime as dt
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

class Query(commands.Cog):
    '''
    Any commands that directly relate to scraped Indeed
    data and related queries.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.pickle_path = '/Users/isaiahjones/PycharmProjects/CareerBot/data/jobs.pickle'
        self.db_path = '/Users/isaiahjones/PycharmProjects/CareerBot/data/indeed_jobs.db'

    @commands.command(help='Input {"title/workplaceType/exp"} (Remote, Onsite, Hybrid)')
    # Primary command used to generate scrape query; stores results as pickle
    async def generate(self, ctx, criteria):

        if criteria.count('/') != 2:
            await ctx.send('Please ensure that your query is formatted properly (see -help).')
            return 'Improper format.'

        # Create BeautifulSoup object for scraping job data
        title, workplaceType, exp = criteria.replace(' ', '+').split('/')
        workplaceType = workplaceType.split(',')
        search_state = {
            "searchQuery": title,
            "physicalEnvironments": ["Office", "Industrial", "Customer-Facing"],
            "workplaceTypes": workplaceType,
            "seniorityLevel": [f"{exp} Level"]
        }
        encoded_state = urllib.parse.quote(str(search_state).replace("'", '"'))
        url = f"https://hiring.cafe/?searchState={encoded_state}"
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")  # Run in background
        options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        print('Soup cooked.')

        # Wait for the job grid to load
        driver.implicitly_wait(10)

        try:
            job_grid = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".grid.grid-cols-1"))
            )
            listings = job_grid.find_elements(By.CLASS_NAME, "relative")
            jobs = []
            data = []

            for job in listings:
                job_info = job.text.split('\n')

                title = job_info[1] if len(job_info) > 1 else None
                location = job_info[2] if len(job_info) > 2 else None
                salary = job_info[3] if len(job_info) > 3 else None
                workplace_type = job_info[4] if len(job_info) > 4 else None
                company = job_info[6] if len(job_info) > 6 else None
                link = job.find_elements(By.XPATH, '//a[contains(@class, "text-pink-600/50")]')[0].get_attribute(
                    "href") if job.find_elements(By.XPATH, '//a[contains(@class, "text-pink-600/50")]') else None
                jobs.append({
                    "Title": title if title else None,
                    "Company": company if company else None,
                    "Location": location if location else None,
                    "Salary": salary if salary else None,
                    "Workplace Type": workplace_type if workplace_type else None,
                    "URL": link if link else None
                })

            data = jobs

        except Exception as e:
                await ctx.send('Error parsing jobs data.')
                return f'Parsing error: {e}'

        if not data:
            await ctx.send('No jobs found that meet your criteria.')
            return 'No jobs found.'
        # Create pandas DataFrame from scraped data
        jobs_df_pre_transform = pd.DataFrame(data).fillna('')

        print('Dataframe generated.')

        await ctx.send(f'{jobs_df_pre_transform.shape[0]} jobs found that meet your critera:')
        await ctx.send('- - -')
        await ctx.send('Sending first few results...')

        jobs_df = jobs_df_pre_transform.drop_duplicates(subset=['Title', 'Company', 'Location', 'Salary', 'Workplace Type', 'URL'])
        jobs_df = jobs_df.reset_index(drop=True)
        if jobs_df.shape[0] > 5:
            for i in range(5):
                title = jobs_df.loc[i]['Title']
                company = jobs_df.loc[i]['Company']
                location = jobs_df.loc[i]['Location']
                salary = jobs_df.loc[i]['Salary']
                workplace_type = jobs_df.loc[i]['Workplace Type']
                embed = discord.Embed(
                    title=f'{title} | {salary} | {workplace_type}',
                    url=f"{jobs_df['URL'].iloc[i]}",
                    description=f"Company: {company}\nLocation: {location}\n\nHere's the link to your new job!"
                )
                await ctx.send(embed=embed)
        else:
            for i in range(jobs_df.shape[0]):
                title = jobs_df.loc[i]['Title']
                company = jobs_df.loc[i]['Company']
                location = jobs_df.loc[i]['Location']
                salary = jobs_df.loc[i]['Salary']
                workplace_type = jobs_df.loc[i]['Workplace Type']
                embed = discord.Embed(
                    title=f'{title} | {salary} | {workplace_type}',
                    url=f"{jobs_df['URL'].iloc[i]}",
                    description=f"Company: {company}\nLocation: {location}\n\nHere's the link to your new job!"
                )
                await ctx.send(embed=embed)

        await ctx.send('- - -')
        await ctx.send('Utilize -url or -save to view or store individual postings, respectively.')

        # Creating pickle object to save pd.DataFrame for use in other functions
        pickle_out = open(self.pickle_path, 'wb')
        pickle.dump(jobs_df, pickle_out, protocol=2)
        pickle_out.close()

    @generate.error
    async def generate_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please input query criteria using the format found in -help.')

    @commands.command(help='Deletes job query')
    async def clear(self, ctx):
        if os.path.exists(self.pickle_path):
            os.remove(self.pickle_path)
            await ctx.send('Query cleared. Use -generate to create a new query.')
        else:
            await ctx.send('No query to delete. Use -generate to create a new query.')

    @commands.command(help='Generates URL of {index} job from query')
    async def url(self, ctx, index):
        try:
            pickle_in = open(self.pickle_path, 'rb')
            jobs_df = pickle.load(pickle_in)
            job_url = jobs_df['URL'].iloc[int(index)-1]
            await ctx.send(f'https://www.indeed.com{job_url}')
        except FileNotFoundError:
            await ctx.send('Query not found; please use -generate to create a query.')
        except IndexError:
            await ctx.send('Index of desired job is out of scope of query.')

    @url.error
    async def url_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please specify the index of the saved job.')

    @commands.command(help='Saves {index} job to database')
    async def save(self, ctx, index, date=dt.today().strftime('%m/%d/%Y')):
        try:
            pickle_in = open(self.pickle_path, 'rb')
            jobs_df = pickle.load(pickle_in)
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            title, company, location, url = jobs_df.iloc[int(index)-1]
            user = str(ctx.message.author.id)
            c.execute("INSERT INTO job_postings VALUES (?, ?, ?, ?, ?, ?)",
                      (title, company, location, url, user, date)
                      )
            conn.commit()
            conn.close()

            await ctx.send('Job posting saved in database. Use -db_refresh to see all saved postings.')

        except FileNotFoundError:
            await ctx.send('Query not found; please use -generate to create a query.')
        except IndexError:
            await ctx.send('Index of desired job is out of scope of query.')
        except sqlite3.OperationalError:
            print('Database already created and located in /data.')

    @save.error
    async def save_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please specify the index of the saved job.')


async def setup(bot):
    await bot.add_cog(Query(bot))
