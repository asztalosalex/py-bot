import discord
import os
import logging
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
from openai_service.ai_init import AiInit
from tts.tts import TTS

logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DC_TOKEN')
        if not self.token:
            raise ValueError("No DC_TOKEN found in .env file")

        logger.info("Initializing bot...")
        intents = discord.Intents.default()
        intents.message_content = True
        intents.presences = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents, description='pybot')

        self.ai_init = AiInit()
        self.tts = TTS()


    async def setup_hook(self):
        """This is called when the bot starts up"""
        try:
            await self.load_extension('bot.cogs.ai_handler')
            await self.load_extension('bot.cogs.music')
            logger.info("Extensions loaded successfully")
        except Exception:
            logger.exception("Error loading extensions")

    async def on_voice_state_update(self, member, before, after):
        try:
            if before.channel is None and after.channel is not None:
                if member.name != "Gyula":
                    
                    greeting_text = self.ai_init.greet_user(member.name)
                    audio_stream = self.tts.generate_audio(greeting_text)

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
                        logger.warning("Voice client failed to connect after timeout.")
                        os.remove(temp_file)
                        return

                    # Now safe to play
                    try:
                        voice.play(discord.FFmpegPCMAudio(temp_file))
                    except discord.ClientException:
                        logger.exception("Failed to play audio")
                        await voice.disconnect()
                        os.remove(temp_file)
                        return

                    while voice.is_playing():
                        await asyncio.sleep(1)

                    await voice.disconnect()
                    os.remove(temp_file)
                elif before.channel is not None and after.channel is None:
                    logger.info("%s left the voice channel: %s", member.name, before.channel.name)

                elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
                    logger.info("%s moved from %s to %s", member.name, before.channel.name, after.channel.name)
        except Exception:
            logger.exception("Error in on_voice_state_update")

    async def on_ready(self):
        logger.info("Successfully logged in as %s", self.user)
        logger.info("Bot ID: %s", self.user.id)
        logger.info("Bot is connected to %d server(s):", len(self.guilds))
        for guild in self.guilds:
            logger.info("- %s (ID: %s)", guild.name, guild.id)

    def run_bot(self):
        try:
            logger.info("Starting the bot...")
            super().run(self.token)
        except discord.errors.LoginFailure:
            logger.error("Invalid token. Please check your DC_TOKEN in .env file")
        except Exception:
            logger.exception("An error occurred while running the bot")
