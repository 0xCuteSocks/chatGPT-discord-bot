import os
import json
import asyncio
import discord

from src import log, responses
from dotenv import load_dotenv
from discord import app_commands
from EdgeGPT.EdgeGPT import Chatbot as BingChatbot
from Bard import AsyncChatbot as BardChatbot


logger = log.setup_logger(__name__)
load_dotenv()


class aclient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.activity = discord.Activity(
            type=discord.ActivityType.listening, name="/chat | /help"
        )
        self.isPrivate = False
        self.is_replying_all = os.getenv("REPLYING_ALL")
        self.replying_all_discord_channel_id = os.getenv(
            "REPLYING_ALL_DISCORD_CHANNEL_ID"
        )
        self.bard_session_token = os.getenv("BARD_SESSION_TOKEN")
        self.loop = asyncio.get_event_loop()
        self.bard_chatbot = self.loop.run_until_complete(self.get_bard_chatbot_model())
        self.bing_chatbot = self.loop.run_until_complete(self.get_bing_chatbot_model())

    async def get_bing_chatbot_model(self) -> BingChatbot:
        cookies = json.loads(open("./cookies.json", encoding="utf-8").read())
        bot = await BingChatbot.create(cookies=cookies)
        await asyncio.sleep(1)
        return bot

    async def get_bard_chatbot_model(self) -> BardChatbot:
        bot = await BardChatbot.create(session_id=self.bard_session_token)
        await asyncio.sleep(1)
        return bot

    async def send_bard_message(self, message, user_message):
        if self.is_replying_all == "False":
            author = message.user.id
            await message.response.defer(ephemeral=self.isPrivate)
        else:
            author = message.author.id
        try:
            response = f"> **{user_message}** - <@{str(author)}" + "> \n\n"
            response = (
                f"{response}{await responses.bard_handle_response(user_message, self)}"
            )
            char_limit = 1900
            if len(response) > char_limit:
                # Split the response into smaller chunks of no more than 1900 characters each(Discord limit is 2000 per chunk)
                if "```" in response:
                    # Split the response if the code block exists
                    parts = response.split("```")

                    for i in range(len(parts)):
                        if i % 2 == 0:  # indices that are even are not code blocks
                            if self.is_replying_all == True:
                                await message.channel.send(
                                    parts[i], suppress_embeds=True
                                )
                            else:
                                await message.followup.send(
                                    parts[i], suppress_embeds=True
                                )
                        else:  # Odd-numbered parts are code blocks
                            code_block = parts[i].split("\n")
                            formatted_code_block = ""
                            for line in code_block:
                                while len(line) > char_limit:
                                    # Split the line at the 50th character
                                    formatted_code_block += line[:char_limit] + "\n"
                                    line = line[char_limit:]
                                formatted_code_block += (
                                    line + "\n"
                                )  # Add the line and seperate with new line

                            # Send the code block in a separate message
                            if len(formatted_code_block) > char_limit + 100:
                                code_block_chunks = [
                                    formatted_code_block[i : i + char_limit]
                                    for i in range(
                                        0, len(formatted_code_block), char_limit
                                    )
                                ]
                                for chunk in code_block_chunks:
                                    if self.is_replying_all == True:
                                        await message.channel.send(
                                            f"```{chunk}```", suppress_embeds=True
                                        )
                                    else:
                                        await message.followup.send(
                                            f"```{chunk}```", suppress_embeds=True
                                        )
                            elif self.is_replying_all == True:
                                await message.channel.send(
                                    f"```{formatted_code_block}```",
                                    suppress_embeds=True,
                                )
                            else:
                                await message.followup.send(
                                    f"```{formatted_code_block}```",
                                    suppress_embeds=True,
                                )
                else:
                    response_chunks = [
                        response[i : i + char_limit]
                        for i in range(0, len(response), char_limit)
                    ]
                    for chunk in response_chunks:
                        if self.is_replying_all == True:
                            await message.channel.send(chunk, suppress_embeds=True)
                        else:
                            await message.followup.send(chunk, suppress_embeds=True)
            elif self.is_replying_all == True:
                await message.channel.send(response, suppress_embeds=True)
            else:
                await message.followup.send(response, suppress_embeds=True)
        except Exception as e:
            if self.is_replying_all == True:
                await message.channel.send(
                    "> **Bard Error: Something went wrong, please try again later!**"
                )
            else:
                await message.followup.send(
                    "> **Bard Error: Something went wrong, please try again later!**"
                )
            logger.exception(f"Bard Error while sending message: {e}")

    async def send_bing_message(self, message, user_message):
        if self.is_replying_all == "False":
            author = message.user.id
            await message.response.defer(ephemeral=self.isPrivate)
        else:
            author = message.author.id
        try:
            response = f"> **{user_message}** - <@{str(author)}" + "> \n\n"
            response = (
                f"{response}{await responses.bing_handle_response(user_message, self)}"
            )
            char_limit = 1900
            if len(response) > char_limit:
                # Split the response into smaller chunks of no more than 1900 characters each(Discord limit is 2000 per chunk)
                if "```" in response:
                    # Split the response if the code block exists
                    parts = response.split("```")

                    for i in range(len(parts)):
                        if i % 2 == 0:  # indices that are even are not code blocks
                            if self.is_replying_all == True:
                                await message.channel.send(
                                    parts[i], suppress_embeds=True
                                )
                            else:
                                await message.followup.send(
                                    parts[i], suppress_embeds=True
                                )
                        else:  # Odd-numbered parts are code blocks
                            code_block = parts[i].split("\n")
                            formatted_code_block = ""
                            for line in code_block:
                                while len(line) > char_limit:
                                    # Split the line at the 50th character
                                    formatted_code_block += line[:char_limit] + "\n"
                                    line = line[char_limit:]
                                formatted_code_block += (
                                    line + "\n"
                                )  # Add the line and seperate with new line

                            # Send the code block in a separate message
                            if len(formatted_code_block) > char_limit + 100:
                                code_block_chunks = [
                                    formatted_code_block[i : i + char_limit]
                                    for i in range(
                                        0, len(formatted_code_block), char_limit
                                    )
                                ]
                                for chunk in code_block_chunks:
                                    if self.is_replying_all == True:
                                        await message.channel.send(
                                            f"```{chunk}```", suppress_embeds=True
                                        )
                                    else:
                                        await message.followup.send(
                                            f"```{chunk}```", suppress_embeds=True
                                        )
                            elif self.is_replying_all == True:
                                await message.channel.send(
                                    f"```{formatted_code_block}```",
                                    suppress_embeds=True,
                                )
                            else:
                                await message.followup.send(
                                    f"```{formatted_code_block}```",
                                    suppress_embeds=True,
                                )
                else:
                    response_chunks = [
                        response[i : i + char_limit]
                        for i in range(0, len(response), char_limit)
                    ]
                    for chunk in response_chunks:
                        if self.is_replying_all == True:
                            await message.channel.send(chunk, suppress_embeds=True)
                        else:
                            await message.followup.send(chunk, suppress_embeds=True)
            elif self.is_replying_all == True:
                await message.channel.send(response, suppress_embeds=True)
            else:
                await message.followup.send(response, suppress_embeds=True)
        except Exception as e:
            if self.is_replying_all == True:
                await message.channel.send(
                    "> **BingGPT Error: Something went wrong, please try again later!**"
                )
                await self.bing_chatbot.reset()
            else:
                await message.followup.send(
                    "> **BingGPT Error: Something went wrong, please try again later!**"
                )
                await self.bing_chatbot.reset()
            logger.exception(f"BingGPT Error while sending message: {e}")

    async def send_message(self, message, user_message):
        if self.is_replying_all == "False":
            author = message.user.id
            await message.response.defer(ephemeral=self.isPrivate)
        else:
            author = message.author.id
        try:
            response = f"> **{user_message}** - <@{str(author)}" + "> \n\n"
            if self.chat_model == "OFFICIAL":
                response = f"{response}{await responses.official_handle_response(user_message, self)}"
            elif self.chat_model == "UNOFFICIAL":
                response = f"{response}{await responses.unofficial_handle_response(user_message, self)}"
            char_limit = 1900
            if len(response) > char_limit:
                # Split the response into smaller chunks of no more than 1900 characters each(Discord limit is 2000 per chunk)
                if "```" in response:
                    # Split the response if the code block exists
                    parts = response.split("```")

                    for i in range(len(parts)):
                        if i % 2 == 0:  # indices that are even are not code blocks
                            if self.is_replying_all == True:
                                await message.channel.send(parts[i])
                            else:
                                await message.followup.send(parts[i])
                        else:  # Odd-numbered parts are code blocks
                            code_block = parts[i].split("\n")
                            formatted_code_block = ""
                            for line in code_block:
                                while len(line) > char_limit:
                                    # Split the line at the 50th character
                                    formatted_code_block += line[:char_limit] + "\n"
                                    line = line[char_limit:]
                                formatted_code_block += (
                                    line + "\n"
                                )  # Add the line and seperate with new line

                            # Send the code block in a separate message
                            if len(formatted_code_block) > char_limit + 100:
                                code_block_chunks = [
                                    formatted_code_block[i : i + char_limit]
                                    for i in range(
                                        0, len(formatted_code_block), char_limit
                                    )
                                ]
                                for chunk in code_block_chunks:
                                    if self.is_replying_all == True:
                                        await message.channel.send(f"```{chunk}```")
                                    else:
                                        await message.followup.send(f"```{chunk}```")
                            elif self.is_replying_all == True:
                                await message.channel.send(
                                    f"```{formatted_code_block}```"
                                )
                            else:
                                await message.followup.send(
                                    f"```{formatted_code_block}```"
                                )
                else:
                    response_chunks = [
                        response[i : i + char_limit]
                        for i in range(0, len(response), char_limit)
                    ]
                    for chunk in response_chunks:
                        if self.is_replying_all == True:
                            await message.channel.send(chunk)
                        else:
                            await message.followup.send(chunk)
            elif self.is_replying_all == True:
                await message.channel.send(response)
            else:
                await message.followup.send(response)
        except Exception as e:
            if self.is_replying_all == True:
                await message.channel.send(
                    "> **Error: Something went wrong, please try again later!**"
                )
            else:
                await message.followup.send(
                    "> **Error: Something went wrong, please try again later!**"
                )
            logger.exception(f"Error while sending message: {e}")

    async def send_start_prompt(self):
        import os.path

        config_dir = os.path.abspath(f"{__file__}/../../")
        prompt_name = "starting-prompt.txt"
        prompt_path = os.path.join(config_dir, prompt_name)
        discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
        try:
            if os.path.isfile(prompt_path) and os.path.getsize(prompt_path) > 0:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    prompt = f.read()
                    if discord_channel_id:
                        logger.info(f"Send starting prompt with size {len(prompt)}")
                        response = ""
                        response = f"{response}{await responses.bard_handle_response(prompt, self)}"
                        channel = self.get_channel(int(discord_channel_id))
                        await channel.send(response)
                        logger.info(f"Starting prompt response:{response}")
                    else:
                        logger.info(
                            "No Channel selected. Skip sending starting prompt."
                        )
            else:
                logger.info(f"No {prompt_name}. Skip sending starting prompt.")
        except Exception as e:
            logger.exception(f"Error while sending starting prompt: {e}")


client = aclient()
