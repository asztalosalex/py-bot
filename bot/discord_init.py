import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from lol.lol_requests import LolRequests
from discord.ext import tasks
import random
import logging
from mnb.soap_client import getCurrencyRate
import asyncio
import openai
from openai_service.ai_init import AiInit
from tts.tts import TTS

class DiscordBot(commands.Bot):

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DC_TOKEN')
        if not self.token:
            raise ValueError("No DC_TOKEN found in .env file")

        print("Initializing bot...")
        intents = discord.Intents.default()
        intents.message_content = True
        intents.presences = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents, description='pybot')
        
        self.activity_channel_id = 1201609666099150980
        self.price1_channel_id = 1363559409615372359
        self.price2_channel_id = 1363559630747472083
        self.price3_channel_id = 1363559739190939869
        

    async def setup_hook(self):
        """This is called when the bot starts up"""
        try:
            await self.load_extension('bot.cogs.basic_commands')
            await self.load_extension('bot.cogs.ai_handler')
            print("Extensions loaded successfully")
        except Exception as e:
            print(f"Error loading extensions: {e}")

     async def on_voice_state_update(self, member, before, after):
        try:
            if before.channel is None and after.channel is not None:
                print(f"{member.name} joined the voice channel: {after.channel.name}")
                if member.name != "Gyula":
                    
                    ai_init = AiInit()
                    greeting_text = ai_init.greet_user(member.name)
                    tts = TTS()
                    audio_stream = tts.generate_audio(greeting_text)

                    temp_file = f"{member.name}_joined_voice_channel.mp3"
                    with open(temp_file, "wb") as f:
                        for chunk in audio_stream:
                            f.write(chunk)
                    
                    channel = member.voice.channel
                    voice = await channel.connect(reconnect=False)
                    
                    # Wait until connected or timeout
                    for _ in range(10):  # up to 5 seconds
                        if voice.is_connected():
                            break
                        await asyncio.sleep(0.5)

                    if not voice.is_connected():
                        print("Voice client failed to connect after timeout.")
                        os.remove(temp_file)
                        return

                    # Now safe to play
                    try:
                        voice.play(discord.FFmpegPCMAudio(temp_file))
                    except discord.ClientException as e:
                        print(f"Failed to play audio: {e}")
                        await voice.disconnect()
                        os.remove(temp_file)
                        return

                    while voice.is_playing():
                        await asyncio.sleep(1)

                    await voice.disconnect()
                    os.remove(temp_file)

            elif before.channel is not None and after.channel is None:
                print(f"{member.name} left the voice channel: {before.channel.name}")

            elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
                print(f"{member.name} moved from {before.channel.name} to {after.channel.name}")
        except Exception as e:
            print(f"Error in on_voice_state_update: {e}")
            import traceback
            traceback.print_exc()

    async def on_presence_update(self, before, after):
        try:
            activity_channel = self.get_channel(self.activity_channel_id)
            if not activity_channel:
                print(f"Activity channel {self.activity_channel_id} not found")
                return

            if before.activity is None and after.activity is not None:
                await activity_channel.send(f'{after.name} started playing {after.activity.name}')

            elif before.activity is not None and after.activity is None:
                await activity_channel.send(f'{after.name} stopped playing {before.activity.name}')

            elif (before.activity and after.activity and
                before.activity.details != after.activity.details and
                after.activity.details is not None):
                lol_requests = LolRequests()
                summoner_name: str = lol_requests.get_summoner_name_by_member_id(after.id)
                puuid: int = lol_requests.get_puuid(summoner_name=summoner_name)
                active_game = lol_requests.get_active_game(puuid=puuid)

                await activity_channel.send(
                    f'{after.id} - {after.name} is now playing {after.activity.name} - {after.activity.details}\n Game details{active_game}'
                )
        except Exception as e:
            print(f"Error in on_presence_update: {e}")


    @tasks.loop(minutes=5)
    async def update_channel_name(self):
        mnb_data = getCurrencyRate()
        usd_rate = str(mnb_data.getActual('USD'))
        eur_rate = str(mnb_data.getActual('EUR'))
        gbp_rate = str(mnb_data.getActual('GBP'))

        try:
            channel1 = self.get_channel(self.price1_channel_id)
            channel2 = self.get_channel(self.price2_channel_id)
            channel3 = self.get_channel(self.price3_channel_id)

            if not channel1 or not channel2 or not channel3:
                print(f"One or more channels not found. Channel1: {channel1}, Channel2: {channel2}, Channel3: {channel3}")
                return
            
            await channel1.edit(name=f'EUR - {eur_rate} Ft')
            await channel2.edit(name=f'USD - {usd_rate} Ft')
            await channel3.edit(name=f'GBP - {gbp_rate} Ft')
            
            print(f"Successfully updated channel names")

        except discord.Forbidden as e:
            print(f"Permission error: {e}")
            print(f"Bot permissions in channel1: {channel1.permissions_for(channel1.guild.me)}")
        except Exception as e:
            print(f"Error in update_channel_name: {e}")
            print(f"Channel1 exists: {bool(channel1)}")
            if channel1:
                print(f"Channel1 guild: {channel1.guild.name}")
                print(f"Channel1 permissions: {channel1.permissions_for(channel1.guild.me)}")


    async def on_ready(self):
        print(f'Successfully logged in as {self.user}')
        print(f'Bot ID: {self.user.id}')
        print('Bot is connected servers below:')
        for guild in self.guilds:
            print(f'- {guild.name} (ID: {guild.id})')
        self.update_channel_name.start()

    def run_bot(self):
    
        try:
            print("Starting the bot...")
            super().run(self.token)
        except discord.errors.LoginFailure:
            print("Invalid token. Please check your DC_TOKEN in .env file")
        except Exception as e:
            print(f"An error occurred while running the bot: {e}")
