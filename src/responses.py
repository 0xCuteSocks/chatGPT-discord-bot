import pprint as pp
from EdgeGPT.EdgeGPT import ConversationStyle

async def bing_handle_response(message, client) -> str:
    response = await client.bing_chatbot.ask(
        prompt=message, conversation_style=ConversationStyle.balanced
    )
    pp.pprint(response)
    try:
        for i in range(1,5):
            try:
                responseMessage = response["item"]["messages"][i]["adaptiveCards"][0]["body"][0]["text"]
                return responseMessage
            except:
                continue
    except:
        responseMessage = "Unknow error, please use /reset_bing to reset."
        return responseMessage

async def bard_handle_response(message, client) -> str:
    response = await client.bard_chatbot.ask(message)
    pp.pprint(response)
    responseMessage = response["content"]
    return responseMessage
