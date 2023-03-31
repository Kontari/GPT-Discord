import discord
from discord.ext import commands
import aiohttp
import json
import os
import openai 

# Bard code
import argparse
import json
import random
import re
import string

import requests
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.markdown import Markdown


intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True
intents.guilds = True

openai.api_key = os.environ['OPENAI_API_KEY']
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']

# Bard requires the __Secure-1PSID cookie which can be obtained
# by viewing console on the chat page
BARD_COOKIE = os.environ['BARD_COOKIE']

# Set up the Discord bot and OpenAI
bot = commands.Bot(command_prefix="!", intents=intents)

class Chatbot:
    """
    A class to interact with Google Bard.
    Parameters
        session_id: str
            The __Secure-1PSID cookie.
    """
    __slots__ = [
        "headers",
        "_reqid",
        "SNlM0e",
        "conversation_id",
        "response_id",
        "choice_id",
        "session",
    ]

    def __init__(self, session_id):
        headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }
        self._reqid = int("".join(random.choices(string.digits, k=4)))
        self.conversation_id = ""
        self.response_id = ""
        self.choice_id = ""
        self.session = requests.Session()
        self.session.headers = headers
        self.session.cookies.set("__Secure-1PSID", session_id)
        self.SNlM0e = self.__get_snlm0e()

    def __get_snlm0e(self):
        resp = self.session.get(url="https://bard.google.com/", timeout=10)
        # Find "SNlM0e":"<ID>"
        if resp.status_code != 200:
            raise Exception("Could not get Google Bard")
        SNlM0e = re.search(r"SNlM0e\":\"(.*?)\"", resp.text).group(1)
        return SNlM0e

    def ask(self, message: str) -> dict:
        """
        Send a message to Google Bard and return the response.
        :param message: The message to send to Google Bard.
        :return: A dict containing the response from Google Bard.
        """
        # url params
        params = {
            "bl": "boq_assistant-bard-web-server_20230326.21_p0",
            "_reqid": str(self._reqid),
            "rt": "c",
        }

        # message arr -> data["f.req"]. Message is double json stringified
        message_struct = [
            [message],
            None,
            [self.conversation_id, self.response_id, self.choice_id],
        ]
        data = {
            "f.req": json.dumps([None, json.dumps(message_struct)]),
            "at": self.SNlM0e,
        }

        # do the request!
        resp = self.session.post(
            "https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
            params=params,
            data=data,
            timeout=120,
        )

        chat_data = json.loads(resp.content.splitlines()[3])[0][2]
        if not chat_data:
            return {"content": f"Google Bard encountered an error: {resp.content}."}
        json_chat_data = json.loads(chat_data)
        results = {
            "content": json_chat_data[0][0],
            "conversation_id": json_chat_data[1][0],
            "response_id": json_chat_data[1][1],
            "factualityQueries": json_chat_data[3],
            "textQuery": json_chat_data[2][0] if json_chat_data[2] is not None else "",
            "choices": [{"id": i[0], "content": i[1]} for i in json_chat_data[4]],
        }
        self.conversation_id = results["conversation_id"]
        self.response_id = results["response_id"]
        self.choice_id = results["choices"][0]["id"]
        self._reqid += 100000
        return results




# Function to call the ChatGPT API asynchronously
async def chat_bard(p):
    response = chatbot.ask(p)
    try:
        text = response['content']
        return text
    except e:
        return f'Error {e}'



# Function to call the ChatGPT API asynchronously
async def chat_gpt(p):
    response = openai.Completion.create(
        model="text-davinci-003",
        max_tokens=2048,
        prompt=p,
        temperature=0.7)
    try:
        text = dict(response.choices[0])['text']
        return text
    except e:
        return f'Error {e}'

async def chat_gpt_image(p):
    response = openai.Image.create(
        prompt=p,
        n=1,
        size="1024x1024")
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
async def bard(ctx, *, question):
    print(f'Asked: {question}')
    prompt = f"{question}"
    try:
        response = await chat_bard(prompt)
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


chatbot = Chatbot(BARD_COOKIE)

# Run the bot
bot.run(DISCORD_BOT_TOKEN)

