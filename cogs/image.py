import nextcord
from nextcord.ext import commands
from nextcord.enums import ButtonStyle
import aiohttp
import aiofiles
from PIL import Image
import asyncio
import io
import os
import uuid
import src.ai as ai
import base64
import json

class RowButtons(nextcord.ui.View):
    def __init__(self, uuid, prompt):
        super().__init__(timeout=6000)
        self.uuid = uuid
        self.prompt = prompt
        self.variation_num = None

    async def upscale_and_send(self, inter, file_index):
        await inter.response.defer()
        msg = await inter.send("Upscalling Image...")
        file_path = f"images/{self.uuid}_{file_index - 1}.png"
        async with aiofiles.open(file_path, 'rb') as f:
            image = await f.read()
        image_base64 = base64.b64encode(image).decode('utf-8')
        upscaled_image = await upscale_request(image_base64)
        upscale_path = f"images/{self.uuid}_{file_index}_upscale.png"
        await download(upscaled_image, upscale_path)
        file = nextcord.File(upscale_path, filename="upscaled.png")
        await msg.edit(content="Upscaled Image", file=file)

    async def variations_and_send(self, inter: nextcord.Interaction, file_index):
        await inter.response.defer()
        sus = await inter.send("Creating Variations 0/4")
        file_path = f"images/{self.uuid}_{file_index - 1}.png"
        async with aiofiles.open(file_path, 'rb') as f:
            image = await f.read()
        image_base64 = base64.b64encode(image).decode('utf-8')
        files = []
        grid_path = f"images/{self.uuid}_grid_variation.png"
        for i in range(4):
            await sus.edit(f"Creating Variations {i+1}/4")
            variation_path = f"images/{self.uuid}_{file_index}_v{i}.png"
            url = await ai.transform_image(self.prompt, image_base64)
            await download(url, variation_path)            
            img = Image.open(variation_path).resize((512, 512))
            files.append(img)
        
        if len(files) == 4:
            width, height = files[0].size
            grid = Image.new('RGB', (width * 2, height * 2))
            grid.paste(files[0], (0, 0))
            grid.paste(files[1], (width, 0))
            grid.paste(files[2], (0, height))
            grid.paste(files[3], (width, height))
            grid.save(grid_path, "PNG")
            file = nextcord.File(grid_path, filename="variations.png")
            await sus.edit(content="Image Variations", file=file, view=Variations(self.uuid, self.prompt, file_index, file_index))
        else:
            await sus.edit(embed=nextcord.Embed(title="Error", description="Not enough images for the grid.", color=0xff0000))

    @nextcord.ui.button(label="U1", style=ButtonStyle.grey, row=1)
    async def U1(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.upscale_and_send(inter, 1)

    @nextcord.ui.button(label="U2", style=ButtonStyle.grey, row=1)
    async def U2(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.upscale_and_send(inter, 2)

    @nextcord.ui.button(label="U3", style=ButtonStyle.grey, row=1)
    async def U3(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.upscale_and_send(inter, 3)

    @nextcord.ui.button(label="U4", style=ButtonStyle.grey, row=1)
    async def U4(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.upscale_and_send(inter, 4)

    @nextcord.ui.button(emoji="🔃", style=ButtonStyle.blurple, row=1)
    async def regenerate_images(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await inter.response.defer()
        await inter.edit_original_message("Regenarating Images 0/4", file=None, embed=None)
        file = uuid.uuid4()
        files = []
        grid_path = f"images/{file}_grid.png"
        for i in range(4):
            await inter.edit_original_message(f"Regenarating Images {i+1}/4", file=None, embed=None)
            url = await generate_image(self.prompt)
            file_path = f"images/{file}_{i}.png"
            await download(url, file_path)
            img = Image.open(file_path).resize((512, 512))
            files.append(img)

        if len(files) == 4:
            width, height = files[0].size
            grid = Image.new('RGB', (width * 2, height * 2))
            grid.paste(files[0], (0, 0))
            grid.paste(files[1], (width, 0))
            grid.paste(files[2], (0, height))
            grid.paste(files[3], (width, height))
            grid.save(grid_path, "PNG")
            row_buttons = RowButtons(file, self.prompt)
            file = nextcord.File(grid_path, filename="regenerated.png")
            await inter.edit_original_message(content="Regenerated Images", file=file, view=row_buttons)
        else:
            await inter.edit_original_message(content="", embed=nextcord.Embed(title="Error", description="Not enough images for the grid.", color=0xff0000))

    @nextcord.ui.button(label="V1", style=ButtonStyle.grey, row=2)
    async def V1(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.variations_and_send(inter, 1)

    @nextcord.ui.button(label="V2", style=ButtonStyle.grey, row=2)
    async def v2(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.variations_and_send(inter, 2)

    @nextcord.ui.button(label="V3", style=ButtonStyle.grey, row=2)
    async def v3(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.variations_and_send(inter, 3)

    @nextcord.ui.button(label="V4", style=ButtonStyle.grey, row=2)
    async def v4(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.variations_and_send(inter, 4)

class Variations(nextcord.ui.View):
    def __init__(self, uuid, prompt, num, variation_num=None):
        super().__init__(timeout=6000)
        self.uuid = uuid
        self.prompt = prompt
        self.num = num
        self.variation_num = variation_num

    async def upscale_and_send(self, inter, image_idx):
        await inter.response.defer()
        msg = await inter.send("Upscalling Image...")
        image_path = f"images/{self.uuid}_{self.variation_num-1 if self.variation_num - 1 else self.num - 1}.png"
        async with aiofiles.open(image_path, 'rb') as f:
            image = await f.read()
        image_base64 = base64.b64encode(image).decode('utf-8')
        upscaled_filename = f'images/{self.uuid}_{self.num}_u{image_idx + 1}.png'
        upscaled_image = await upscale_request(image_base64)
        await download(upscaled_image, upscaled_filename)
        file = nextcord.File(upscaled_filename, filename="upscaled.png")
        await msg.edit(content="Upscaled Image", file=file)

    @nextcord.ui.button(label="U1", style=ButtonStyle.grey, row=1)
    async def U1(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.upscale_and_send(inter, 1)

    @nextcord.ui.button(label="U2", style=ButtonStyle.grey, row=1)
    async def U2(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.upscale_and_send(inter, 2)

    @nextcord.ui.button(label="U3", style=ButtonStyle.grey, row=1)
    async def U3(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.upscale_and_send(inter, 3)

    @nextcord.ui.button(label="U4", style=ButtonStyle.grey, row=1)
    async def U4(self, button: nextcord.ui.Button, inter: nextcord.Interaction):
        await self.upscale_and_send(inter, 4)

async def upscale_request(image_base):
    upscale_url = "https://try.readme.io/https://api.prodia.com/v1/upscale"
    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9,en-GB;q=0.8",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "x-prodia-key": "f18136a8-b375-4362-8459-e651a89c4e0b",
        "x-readme-api-explorer": "5.51.0",
        "Referer": "https://docs.prodia.com",
        "Origin": "https://docs.prodia.com",
    }
    payload = {
        "resize": 2,
        "model": "R-ESRGAN 4x+",
        "imageData": image_base
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(upscale_url, headers=headers, json=payload) as response:
            response_data = await response.json()
            job_id = response_data['job']
    while True:
        async with aiohttp.ClientSession() as session:
            job_status_url = f"https://api.prodia.com/v1/job/{job_id}"
            async with session.get(job_status_url, headers=headers) as status_response:
                status_data = await status_response.json()
                if status_data.get("status") == "succeeded":
                    return status_data["imageUrl"]
                elif status_data.get("status") == "failed":
                    return None
                else:
                    await asyncio.sleep(2)

async def generate_image(prompt):
    return await ai.generate_image(prompt)

async def download(url: str, filename: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(filename, 'wb') as file:
                    await file.write(await response.read())
            else:
                raise Exception(f"Failed to download file. Status code: {response.status}")

class MJ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command()
    async def imagine(self, inter: nextcord.Interaction, prompt: str):
        await inter.response.defer()
        file_uuid = uuid.uuid4()
        files = []
        grid_path = f"images/{file_uuid}_grid.png"
        try:
            for i in range(4):
                url = await generate_image(prompt)
                file_path = f"images/{file_uuid}_{i}.png"
                if not os.path.exists('images'):
                    os.makedirs('images')
                await download(url, file_path)
                img = Image.open(file_path).resize((512, 512))
                files.append(img)
                await inter.edit_original_message(content=f"Generating Image: {i+1}/4")

            if len(files) == 4:
                width, height = files[0].size
                grid = Image.new('RGB', (width * 2, height * 2))
                grid.paste(files[0], (0, 0))
                grid.paste(files[1], (width, 0))
                grid.paste(files[2], (0, height))
                grid.paste(files[3], (width, height))
                grid.save(grid_path, "PNG")
                row_buttons = RowButtons(file_uuid, prompt)
                file = nextcord.File(grid_path, filename="generated.png")
                await inter.edit_original_message(content="Generated Images", file=file, view=row_buttons)
            else:
                await inter.edit_original_message(content=None, embed=nextcord.Embed(title="Error", description="Not enough images for the grid.", color=0xff0000))
        except Exception as e:
            await inter.edit_original_message(content=None, embed=nextcord.Embed(title="Error", description=f"An error occurred: {str(e)}", color=0xff0000))

def setup(bot):
    bot.add_cog(MJ(bot))
