import discord
from discord.ext import commands
import aiohttp
import json
import os
import openai 


intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True
intents.guilds = True

openai.api_key = os.environ['OPENAI_API_KEY']
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']

# Set up the Discord bot and OpenAI
bot = commands.Bot(command_prefix="!", intents=intents)

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

async def chat_gpt_image(p):
  response = openai.Image.create(
    prompt=p,
    n=1,
    size="1024x1024"
    )

  try:
    text = dict(response.data[0])['url']
    return text
  except e:
    return f'Error {e}'

@bot.command()
async def draw(ctx, *, question):
  print(f'Drawing: {question}')
  prompt = f"{question}"
  try:
    response = await chat_gpt_image(prompt)
    await ctx.send(response)
  except Exception as e:
    await ctx.send(f"Error: {e}")

@bot.command()
async def ask(ctx, *, question):
  print(f'Asked: {question}')
  prompt = f"{question}"
  try:
    response = await chat_gpt(prompt)
    await ctx.send(response)
  except Exception as e:
    await ctx.send(f"Error: {e}")


# Run the bot
bot.run(DISCORD_BOT_TOKEN)

