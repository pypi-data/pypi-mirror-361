import os
import sys
sys.path.insert(0, os.path.dirname(os.getcwd()))

from datetime import datetime
import discord
from zikomo.constants import *

class MyClient(discord.Client):
    def __init__(self, *, 
                 title, 
                 project_name, 
                 version,                  
                 update_points, 
                 image_url, 
                 docs_url, 
                 site_url, 
                 channel_id,
                 **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.project_name = project_name
        self.version = version        
        self.update_points = update_points
        self.image_url = image_url
        self.docs_url = docs_url
        self.site_url = site_url
        self.channel_id = channel_id

    def safe_truncate(self, text, limit=1024):
        if len(text) <= limit:
            return text
        return text[:limit - 3].rstrip() + "..."

    async def on_ready(self):
        now = datetime.now()
        current_date = now.strftime("%d-%b-%Y")  
        current_time = now.strftime("%I:%M %p")
    
        channel = self.get_channel(self.channel_id)
        
        if channel:                        
            embed = discord.Embed(
                title=self.title,
                color=discord.Color.green()
            )
            embed.add_field(name="", value=f'🧩 {self.project_name}', inline=True)
            embed.add_field(name="", value=f'🔖 {self.version}', inline=True)

            embed.add_field(name="", value='', inline=False)  # spacer

            embed.add_field(name="", value=f'📅 {current_date}', inline=True)
            embed.add_field(name="", value=f'🕒 {current_time}', inline=True)

            embed.add_field(name="", value='', inline=False)  # spacer

            truncated_changelog = self.safe_truncate(self.update_points)
            embed.add_field(name="Changelog", value=truncated_changelog, inline=False)

            embed.add_field(name="", value='', inline=False)  # spacer
            embed.add_field(name="", value=f"🔗 [View Docs]({self.docs_url})", inline=True)
            embed.add_field(name="", value=f"🌐 [Visit the site]({self.site_url})", inline=True)

            embed.set_image(url=self.image_url)
            embed.set_footer(text="Zikomo Mini")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)
        else:
            print("❌ Channel not found. Check CHANNEL_ID.")

        await self.close()

def send_discord_message(
    env: str,
    project_name: str,
    version: str,    
    update_points:str,
    image_url: str,
    docs_url: str,
    site_url: str    
):
    intents = discord.Intents.default()
        
    update_points = update_points.replace("• •"," • ")
    update_points = update_points.replace("• -", "• ")
    update_points = update_points.replace("**", "*")

    title=f"{env.upper()} UPDATED!"
    selected_channel=DISCORD_SELECTED_CHANNEL_ID
    
    client = MyClient(
        title=title,
        project_name=project_name,
        version=version,        
        update_points=update_points,
        image_url=image_url,
        docs_url=docs_url,
        site_url=site_url,
        channel_id=selected_channel,
        intents=intents
    )
    
    try:
        client.run(DISCORD_BOT_TOKEN)
        print("✅ Message sent to Discord channel.")
    except Exception as e:
        print(f"Error while sending Discord message: {e}")
        
# --- Usage ---
if __name__ == "__main__":
    title = "🚀 Staging Updated"
    project_name = "Backoffice"
    version = "v1.7.6-staging"
    update_time = datetime.now()
    update_points ="".join([
        "Improved user login speed",
        "Fixed payment gateway timeout bug",
        "Updated booking flow UX",
        "API response time optimised",
    ])
    image_url = "https://zikomo.azureedge.net/media/general/images/staging/1.png"
    docs_url = "https://developers.zikomosolutions.com/api/releases/backoffice/staging-2025/"
    site_url = "https://developers.zikomosolutions.com/api/releases/backoffice/staging-2025/"
    selected_channel = DISCORD_SELECTED_CHANNEL_ID  # or ZIKOMO_CHANNEL_ID

    send_discord_message(
        env="Staging",
        project_name=project_name,
        version=version,       
        update_points=update_points,
        image_url=image_url,
        docs_url=docs_url,
        site_url=site_url
       
    )
    
