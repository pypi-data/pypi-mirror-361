# youdl-jyan 🚀

## Installation

```
pip install youdl-jyan
```

Please note that you need to install `youdl-jyan` using pip by running `pip install --upgrade youdl-jyan` in your terminal before executing these codes.

## AI Image Generator

```
from youdl-jyan import api
generated_image= api.ai_image("boy image")
print(generated_image)
```

## Chatgpt AI 🤖

```
from youdl-jyan import api

# Execute Chatgpt AI with the input text

response = api.chatgpt("Write simple basic html website")

print(response)

# Execute Chatgpt AI with the input text with modes features

# available modes are "girlfriend","anime","animev2","flirt","santa","elonmusk"

response = api.chatgpt("hi babe","girlfriend")

print(response)

```

## Chatbot AI 🤖

```
from youdl-jyan import api

# Execute Chatbot AI with the input text

print(api.chatbot("hii"))
```

## Blackbox AI 🤖

```
from youdl-jyan import api

# Execute blackbox AI with the input text

print(api.blackbox("write flask app code"))
```

## Password Generator 💡

```
from youdl-jyan import api

# Generate a default length password
print(api.password())

# Generate a password of specific length (e.g., 10)
print(api.password(10))
```

## Gemini AI 🤖

```
from youdl-jyan import api

# Execute Gemini AI with the input text

print(api.gemini("write flask app code"))
```

## Datagpt AI 🤖

```
from youdl-jyan import api

# Execute datagpt AI with the input text
response = api.datagpt("what is data science")
print(response)
```

## BhagwatGita

```
from youdl-jyan import api
verse_data = api.bhagwatgita(1, 5)
print(verse_data)
```

## IMDB Search

```
from youdl-jyan import api


movie_data = api.imdb("The Godfather")

print(movie_data)
```

## Morse Decode

```
from youdl-jyan import api

decoded_result =api.morse_decode(".... . .-.. .-.. --- / .-- --- .-. .-.. -..")

print(decoded_result)
```

## Morse Encode

```
from youdl-jyan import api
encoded_result =api.morse_encode("enter text here")
print(encoded_result)
```

## Hastag Generator

```
from youdl-jyan import api
keyword = "python"
hashtags = api.hashtag(keyword)
print(hashtags)
```

## Unsplash Image Search

```
from youdl-jyan import api
response = api.unsplash("boy image")
print(response)

```

## LeetCode Information

```
from youdl-jyan import api

user_data = api.leetcode("TeamProBots")
print(user_data)
```

## Pypi Info

```
from youdl-jyan import api
user_data = api.pypi("youdl-jyan")
print(user_data)
```

## Github Profile Information

```
from youdl-jyan import api
search_results = api.github("TeamProBots")
print(search_results)
```

## Github Repo Search

```
from youdl-jyan import api
search_results = api.repo("lisa")
print(search_results)
```

## Random Meme

```
from youdl-jyan import api
search_results = api.meme()
print(search_results)
```

## Note:

<p> The above examples are for Python </p>

## Copyright (c) 2024-25

## Author : TeamProBots 👨‍💻

# Functions in the api module are as follows:

1. <b>chatgpt(args) </b>- Executes chatgpt AI functionality
2. <b>gemini(args) </b>- Executes Gemini AI functionality
3. <b>blackbox(args) </b>- Executes blackbox AI functionality 🔮
4. <b>hastag(args) </b>- Generates hashtags based on input
5. <b>imdb(args) </b>- Fetches information from IMDB
6. <b>morse_encode(args) </b>- Encodes text into Morse code
7. <b>morse_decode(args) </b>- Decodes Morse code into text
8. <b>leetcode(args) </b>- Extract leetcode information by username
9. <b>password(args) </b>- Generates a random password
10. <b>pypi(args) </b>- Search PyPI for packages
11. <b>datagpt(args) </b>- Generates data using Datasets from datagpt ai
12. <b>unsplash(args) </b>- search hd image from unsplash website
13. <b>github(args) </b> - Extract github information by username
14. <b>repo(args) </b> - Extract github repo by name
15. <b> meme()</b> - Generate memes
16. <b> weather(args)</b> - Fetches weather information
17. <b> truth()</b> -random truth string
18. <b>dare()</b> -random dare string
19. <b> ai_image(args)</b> - Generate image using AI
20. <b> upload_image(image_url,image_file) </b> - upload image from img url or img file.

<b>🔗 Have fun coding with youdl-jyan! </b>

<h3 align="center">
    ─「 sᴜᴩᴩᴏʀᴛ 」─
</h3>

<p align="center">
<a href="https://telegram.me/ProBotGc"><img src="https://img.shields.io/badge/-Support%20Group-blue.svg?style=for-the-badge&logo=Telegram"></a>
</p>
<p align="center">
<a href="https://telegram.me/ZeoXpro"><img src="https://img.shields.io/badge/-Support%20Channel-blue.svg?style=for-the-badge&logo=telegram"></a>
</p>
