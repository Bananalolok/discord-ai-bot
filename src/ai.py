import aiohttp
import asyncio
import config

async def generate_image(prompt: str):
    url = f"{config.openai_base}/images/generations"
    payload = {
        "prompt": prompt,
        "model":config.openai_image_gen_model,
    }
    headers = {"Authorization": f"Bearer {config.openai_key}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"][0]["url"]
            else:
                print(f"Request failed with status code: {response.status}")
                return None
            
async def transform_image(prompt, image_b64):
    url = "https://api.prodia.com/v1/sdxl/transform"
    payload = {
        "imageData": image_b64,
        "model": config.prodia_variation_model,
        "prompt": prompt,
        "sampler": "DPM++ 2M Karras",
        "negative_prompt": "badly drawn",
        "width": 1024,
        "height": 1024,
        "cfg_scale": 12
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": config.prodia_key
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json()
            job_id = data.get("job")
            print(f"Job ID: {job_id}")
            if not job_id:
                print("Error: No job ID returned")
                return None
        image_url = f"https://images.prodia.xyz/{job_id}.png"
        while True:
            async with session.get(image_url) as img_response:
                if img_response.status == 200: 
                    print(f"Image is ready at: {image_url}")
                    return image_url
                else:
                    print(f"Image not ready yet, status: {img_response.status}. Retrying...")
            await asyncio.sleep(2)  

async def respond(messages):
    url = f"{config.openai_base}/chat/completions"
    payload = {
        "messages": messages,   
        "model":config.openai_chat_model,
    }
    headers = {"Authorization": f"Bearer {config.openai_key}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"Request failed with status code: {response.status}")
                return None