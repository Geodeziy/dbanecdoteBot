async def translation(text, language):
    import aiohttp
    from settings import RapidAPI_Key
    url = "https://microsoft-translator-text.p.rapidapi.com/translate"
    querystring = {"api-version": "3.0", "to[0]": language, "textType": "plain", "profanityAction": "NoAction"}
    payload = [{"Text": text}]
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RapidAPI_Key,
        "X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers, params=querystring) as response:
            json_response = await response.json()

    return json_response[0]['translations'][0]['text']


# import asyncio
# async def main():
#     translated_text = await translation('Длинный текст', 'en')
#     print(translated_text)
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
