import os
import aiohttp
import discord
from src.aclient import client
from src import log


logger = log.setup_logger(__name__)

headers = {"X-CMC_PRO_API_KEY": os.getenv("CMC_API")}


async def get_price(message, user_message: str) -> str:
    await message.response.defer(ephemeral=False)
    author = message.user.id
    symbol = user_message.upper()
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?symbol={symbol}"
            ) as r:
                if r.status == 200:
                    js = await r.json()
                    name = str(symbol).upper()
                    price = js["data"][name][0]["quote"]["USD"]["price"]
                    pct_24h = js["data"][name][0]["quote"]["USD"]["percent_change_24h"]
                    mc = js["data"][name][0]["quote"]["USD"]["market_cap"]
                    cs = js["data"][name][0]["circulating_supply"]
                    res = f"**{name}**\n- **Price**: $ {price} ({pct_24h}%)\n- **Market Cap**: $ {mc}\n- **Circulating Supply**: {cs}"
                    response = f"> **{user_message}** - <@{str(author)}" + "> \n\n"
                    response = f"{response}{res}"
                    await message.followup.send(response, suppress_embeds=True)
    except Exception as e:
        await message.followup.send(
            "> **Pirce query Error: Something went wrong, please try again later!**"
        )
        logger.exception(f"Pirce query Error while sending message: {e}")


def run_discord_bot():
    @client.event
    async def on_ready():
        await client.send_start_prompt()
        await client.tree.sync()
        logger.info(f"{client.user} is now running!")

    @client.tree.command(name="p", description="Get Price of symbol from CMC")
    async def p(interaction: discord.Interaction, *, message: str):
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : /p [{message}] in ({channel})")
        await get_price(interaction, message)

    @client.tree.command(name="chat", description="Have a chat with Bard")
    async def bard(interaction: discord.Interaction, *, message: str):
        if client.is_replying_all == True:
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **Warn: You already on replyAll mode. If you want to use slash command, switch to normal mode, use `/replyall` again**"
            )
            logger.warning(
                "\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m"
            )
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
        await client.send_bard_message(interaction, message)

    @client.tree.command(name="bing", description="Have a chat with BingGPT")
    async def bing(interaction: discord.Interaction, *, message: str):
        if client.is_replying_all == True:
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **Warn: You already on replyAll mode. If you want to use slash command, switch to normal mode, use `/replyall` again**"
            )
            logger.warning(
                "\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m"
            )
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : /bing [{message}] in ({channel})")
        await client.send_bing_message(interaction, message)

    @client.tree.command(name="private", description="Toggle private access")
    async def private(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not client.isPrivate:
            client.isPrivate = not client.isPrivate
            logger.warning("\x1b[31mSwitch to private mode\x1b[0m")
            await interaction.followup.send(
                "> **Info: Next, the response will be sent via private message. If you want to switch back to public mode, use `/public`**"
            )
        else:
            logger.info("You already on private mode!")
            await interaction.followup.send(
                "> **Warn: You already on private mode. If you want to switch to public mode, use `/public`**"
            )

    @client.tree.command(name="public", description="Toggle public access")
    async def public(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.isPrivate:
            client.isPrivate = not client.isPrivate
            await interaction.followup.send(
                "> **Info: Next, the response will be sent to the channel directly. If you want to switch back to private mode, use `/private`**"
            )
            logger.warning("\x1b[31mSwitch to public mode\x1b[0m")
        else:
            await interaction.followup.send(
                "> **Warn: You already on public mode. If you want to switch to private mode, use `/private`**"
            )
            logger.info("You already on public mode!")

    @client.tree.command(name="delete", description="Delete message by the message ID")
    async def delete(interaction: discord.Interaction, *, message: str):
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        user_message = message
        channel = str(interaction.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
        channel_id, msg_id = user_message.split(",")
        channel = client.get_channel(int(channel_id))
        msg = await channel.fetch_message(msg_id)
        await msg.delete()

    @client.tree.command(
        name="reset_bing", description="Complete reset Bing conversation history"
    )
    async def resetbing(interaction: discord.Interaction):
        await client.bing_chatbot.reset()
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("> **Info: I have forgotten everything.**")
        logger.warning("\x1b[31mBingGPT bot has been successfully reset\x1b[0m")

    @client.tree.command(
        name="reset", description="Complete reset Bard conversation history"
    )
    async def reset(interaction: discord.Interaction):
        client.bard_chatbot.conversation_id = ""
        client.bard_chatbot.response_id = ""
        client.bard_chatbot.choice_id = ""
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("> **Info: I have forgotten everything.**")
        print("Google Bard Reset:")
        response = await client.send_start_prompt()
        print("response: ", response)
        logger.warning("\x1b[31mBard bot has been successfully reset\x1b[0m")

    @client.tree.command(name="help", description="Show help for the bot")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(
            """:star:**BASIC COMMANDS** \n
- `/p [message]` Query Pirce!
- `/chat [message]` Chat with GoogleBard!
- `/bing [message]` Chat with BingGPT!
- `/private` Chat switch to private mode
- `/public` Chat switch to public mode
- `/reset` Clear Bard conversation history
- `/reset_bing` Clear BingGPT conversation history
- `/delete` [channel_id, message_id] Delete SocksGPT's message

        """
        )

        logger.info("\x1b[31mSomeone needs help!\x1b[0m")

    @client.event
    async def on_message(message):
        if client.is_replying_all == True:
            if message.author == client.user:
                return
            if client.replying_all_discord_channel_id:
                if message.channel.id == int(client.replying_all_discord_channel_id):
                    username = str(message.author)
                    user_message = str(message.content)
                    channel = str(message.channel)
                    logger.info(
                        f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})"
                    )
                    await client.send_message(message, user_message)

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    client.run(TOKEN)
