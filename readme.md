# Python Discord Bot



## Features
- Responds to user messages.
- Can genarate images using Dall-e-3
- Has a midjourney like UI for genarating images

## Prerequisites

Before installing and running the bot, make sure you have the following installed:

1. **Python** - You can download Python from [here](https://www.python.org/downloads/).

## Installation Guide

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-bot-repo.git
cd your-bot-repo
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Edit config.py

```python
# config.py
bot_token = "" # your bot token

prodia_key = "xxxxxxxxxxxxxxxxxxx" # change with your own prodia key
openai_key = "sk-xxxxxxxxxxxxxxxxx" # change with your own openai key
openai_base = "https://api.openai.com/v1" # change this if you use another openai like api

openai_chat_model = "gpt-4o" 
openai_image_gen_model = "dall-e-3"
prodia_variation_model = "dreamshaperXL10_alpha2.safetensors [c8afe2ef]"

chat_system_prompt = """
    You are an Helpful assistant
""" 
```

You can get token by the [Discord Developer Portal](https://discord.com/developers/applications).

### 5. Run the bot
```bash
python main.py
```
