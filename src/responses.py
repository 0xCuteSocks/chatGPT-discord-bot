import pprint as pp
from EdgeGPT.EdgeGPT import ConversationStyle


async def bing_handle_response(message, client) -> str:
    response = await client.bing_chatbot.ask(
        prompt=message, conversation_style=ConversationStyle.creative
    )
    pp.pprint(response)
    try:
        responseMessage = response["item"]["messages"][1]["adaptiveCards"][0]["body"][
            0
        ]["text"]
    except IndexError as e:
        responseMessage = response["item"]["messages"][1]["text"]
    except KeyError as e:
        responseMessage = (
            response["item"]["messages"][1]["hiddenText"]
            + ", please use /reset_bing to reset."
        )
    except Exception as e:
        responseMessage = "Unknow error, please use /reset_bing to reset."

    return responseMessage


async def bard_handle_response(message, client) -> str:
    response = await client.bard_chatbot.ask(message)
    pp.pprint(response)
    responseMessage = response["content"]
    return responseMessage
