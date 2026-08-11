import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class AIHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ai = bot.ai_init
        self.bot_mention = f'<@{bot.user.id}>'
        self.conversations = {}

    @commands.command(name='draw')
    async def draw(self, ctx, *, prompt):
        """
        Creates an image based on the provided prompt
        Usage: !draw a beautiful sunset over mountains
        """
        try:
            await ctx.channel.typing()

            if ctx.channel.id not in self.conversations:
                self.conversations[ctx.channel.id] = []

            image_url = self.call_openai_draw(prompt=prompt)

            # Create an embed with the image
            embed = discord.Embed()
            embed.set_image(url=image_url)
            embed.description = f"🎨 **Prompt:** {prompt}"

            await ctx.reply(embed=embed)
        except Exception as e:
            logger.exception("Error while creating image for prompt: %s", prompt)
            await ctx.reply(f"Sorry, I encountered an error while creating the image: {str(e)}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot:
            return

        if self.bot_mention in message.content:
            prompt = message.content.replace(self.bot_mention, '').strip()

            if message.channel.id not in self.conversations:
                self.conversations[message.channel.id] = []

            try:
                await message.channel.typing()
                response = self.call_openai(
                    prompt=prompt,
                    channel_id=message.channel.id
                )
                await message.reply(response)
            except Exception as e:
                logger.exception("Error handling prompt: %s", prompt)
                await message.reply(f"Sorry, I encountered an error: {str(e)}")

    def call_openai(self, prompt, channel_id):
        conversation_history = self.conversations[channel_id]
        response = self.ai.send_request_to_ai(
            request_from_user=prompt,
            conversation_history=conversation_history
        )
        if not response:
            raise ValueError("Received empty response from AI")

        self.conversations[channel_id].append(
            {"role": "user", "content": prompt})
        self.conversations[channel_id].append(
            {"role": "assistant", "content": response})

        if len(self.conversations[channel_id]) > 10:
            self.conversations[channel_id] = self.conversations[channel_id][-10:]
        return response

    def call_openai_draw(self, prompt):
        response = self.ai.generate_image(
            request_from_user=prompt,
        )
        if not response:
            raise ValueError("Received empty response from AI")

        return response

    def get_server_information():
        pass


async def setup(bot):
    await bot.add_cog(AIHandler(bot))
