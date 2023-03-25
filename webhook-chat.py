import discord
from discord.ext import commands
import aiohttp
import json
import os
import openai 
import asyncio
import time
import random


openai.api_key = os.environ['OPENAI_API_KEY']


# Function to call the ChatGPT API asynchronously
async def chat_gpt(p):
  response = openai.Completion.create(
    model="text-davinci-003",
    max_tokens=2048,
    prompt=p,
    temperature=0.7
  )

  try:
    text = dict(response.choices[0])['text']
    return text
  except e:
    return f'Error {e}'

bot = [
 #'webhook', 'chance', 'prefix', 'name'
 # Add your webhook here and any additional behaviors for the bot to speak with
 ['https://discord.com/api/webhooks/111111111111111/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 2, 'Please speak with with a british accent', 'Testuser1'],
['https://discord.com/api/webhooks/111111111111111/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 2, 'Please speak with with an annoyed tone', 'Testuser2'],
]

async def run():
  r = []
  t = 100
  r.append(await chat_gpt('Give me a fun topic of conversation'))
  r.append(r[-1])
  r.append(r[-1])
  r.append(r[-1])

  while t:
    for b in bot:
      #if(random.randint(1,10) > b[2]): 
      prompt = f'{b[2]}\nFriend: {r[0]}\nYou: {r[1]}\nFriend: {r[2]}\nYou:'
      resp = await chat_gpt(prompt)
      resp = resp.replace('\'','')
      resp = resp.replace('\?','')

      r.append(resp)
      r.pop(0)
      # https://github.com/fieu/discord.sh
      os.system(f'discord.sh --webhook-url="{b[0]}" --text="{resp}"')
      print('>>> ' + prompt)
      time.sleep(10)
    random.shuffle(bot)
    t -= 1

asyncio.run(run())

