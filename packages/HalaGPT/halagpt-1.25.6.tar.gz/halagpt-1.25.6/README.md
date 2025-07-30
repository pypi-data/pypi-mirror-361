library HalaGPT
===============

HalaGPT is a free, powerful Python library designed to provide easy access to a variety of advanced AI models and tools. It offers a unified and straightforward interface to interact with multiple AI-powered features such as text generation, voice synthesis, chatbots, image generation, code assistance, and more — all available without complex setup. You do not need any API key; it’s completely free.

---

## Installation

Install HalaGPT quickly using pip:

```bash
pip install HalaGPT
```

or:

```bash
python -m pip install HalaGPT
```

Install HalaGPT via GitHub:

```bash
git clone https://github.com/HalaGPT/HalaGPT.git
```


---

Project Structure

After installation (or cloning), you will have the following files:

```
HalaGPT/
├── wormgpt.py
├── gpt.py
├── blackbox.py
├── deepinfra.py
├── image.py
├── chat.py
├── deepseek.py
├── gemini.py
├── voice.py
└── README.md
```

Each module corresponds to one AI feature, and you import them directly:

```import
import wormgpt
import gpt
import blackbox
import deepinfra
import image
import chat
import deepseek
import gemini
import voice
```

---

Features and Modules

All classes are imported in lowercase for consistency:

import voice, image, blackbox, deepinfra, gpt, wormgpt, gemini, chat, deepseek

1. Voice

Generate human-like speech from text.

Supported voices: alloy, coral, echo, shimmer, verse, onyx

Supported styles: friendly, calm, noir_detective, cowboy


Example:

```
import voice

# Default voice
resp = voice.openai("Hello from HalaGPT!")
print(resp.get("result"))

# Custom voice and style
resp = voice.openai(
    text="Welcome to HalaGPT voice service",
    voice="echo",
    style="calm"
)
print(resp.get("result"))
```


---

2. Image

Generate images from text prompts.

Supported models: fluex-pro, flux, schnell, imger-12, deepseek, gemini-2-5-pro, blackbox, redux, halagpt-7-i, r1, gpt-4-1


Example:

```bash
import image

resp = image.generate(
    prompt="A futuristic city skyline at sunset",
    model="imger-12"
)
print(resp.get("result"))
```


---

3. BlackBox

Specialized models for programming and development tasks.

Example:

```bash
import blackbox

# Generate a Flask hello world app
resp = blackbox.ask(
    text="Create a Flask 'Hello World' app",
    model="python"
)
print(resp.get("result"))
```


---

4. DeepInfra

Access DeepInfra text models for advanced text tasks.

Example:

```bash
import deepinfra

resp = deepinfra.ask(
    text="Explain the theory of relativity in simple terms",
    model="deepseekv3"
)
print(resp.get("result"))
```


---

5. GPT

Unified access to popular GPT-style models.

Example:

```bash
import gpt

resp = gpt.ask(
    text="What is artificial intelligence?",
    model="gpt-4o"
)
print(resp.get("result"))
```

---

6. WormGPT

DarkGPT and Worm endpoints for specialized conversational AI.

Example:

```bash
import wormgpt

resp1 = wormgpt.worm("Generate a random sci-fi plot outline")
print(resp1.get("result"))

resp2 = wormgpt.darkgpt("Write a compelling resume in Arabic")
print(resp2.get("result"))
```

---

7. Gemini

Access Google Gemini conversational models.

Example:

```bash
import gemini

resp = gemini.ask("Analyze the current crypto market trends.")
print(resp.get("result"))
```

---

8. Chat

Lightweight chat interface using OpenAI GPT-3.5.

Example:

```bash
import chat

resp = chat.ask("Who founded Apple Inc.?")
print(resp.get("result"))
```


---

9. DeepSeek

Code generation and understanding assistance.

Example:

```bash
import deepseek

resp = deepseek.codeify("Build a login page with HTML and JavaScript")
print(resp.get("result"))
```

---

Response Handling

Most functions return a dict with the following fields:

```json
status: "OK", "Error", or "Bad"
```

result: main output or raw response
error: error message (if any)

Example:

```bash
import gpt

resp = gpt.ask("Tell me a joke", model="gpt-4")
if resp.get("status") == "OK":
    print(resp.get("result"))
else:
    print("Error:", resp.get("error", "Unknown error"))
```


---

Telegram Bot Integration

Easily integrate HalaGPT into Telegram bots:

```bash
import voice, chat, image
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def start(update: Update, context):
    update.message.reply_text("Welcome to HalaGPT bot!")

def handle_text(update: Update, context):
    user_text = update.message.text
    resp = chat.ask(user_text)
    update.message.reply_text(resp.get("result"))

updater = Updater("YOUR_TELEGRAM_TOKEN")
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_text))
updater.start_polling()
updater.idle()
```


---

Advantages

Free to use: No cost barriers for advanced AI.

Unified library: Multiple AI modules in one package.

Simple API: Start quickly without complex setup.

Multilingual: Supports Arabic and English out of the box.



---

Requirements

Python 3.7+

requests

beautifulsoup4

mnemonic

pycountry

user_agent


Install requirements with:

```bash
pip install requests beautifulsoup4 mnemonic pycountry user_agent

```
---

Contributing & Support

Contributions, bug reports, and feature requests are welcome!
Open issues on GitHub or contact the maintainer.


---

Contact

Owner Telegram: https://t.me/sii_3

Telegram Channel: https://t.me/HalaGPT

Instagram: https://www.instagram.com/1.44110