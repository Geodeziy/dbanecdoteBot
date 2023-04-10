def translation(text, language):
    import requests
    from settings import RapidAPI_Key
    url = "https://microsoft-translator-text.p.rapidapi.com/translate"

    querystring = {"api-version": "3.0", "to[0]": language, "textType": "plain", "profanityAction": "NoAction"}

    payload = [{"Text": text}]
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RapidAPI_Key,
        "X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    json_response = response.json()
    # print(json_response)
    return json_response[0]['translations'][0]['text']


# print(translation('Длинный текст', 'en'))

