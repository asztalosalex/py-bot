import discord
from discord.ext import commands
from openai_service.ai_init import AiInit

class AIHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_mention = f'<@{bot.user.id}>'
        self.conversations = {}

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
                    channel_id = message.channel.id
                    )
                await message.reply(response)
            except Exception as e:
                print(f'Prompt: {prompt}')
                await message.reply(f"Sorry, I encountered an error: {str(e)}")

    def call_openai(self, prompt, channel_id):
        ai = AiInit()
        conversation_history = self.conversations[channel_id]
        response = ai.send_request_to_ai(
            request_from_user=prompt,
            conversation_history=conversation_history
            )
        if not response:
            print(f'response: {response}')
            raise ValueError("Received empty response from AI")
        

        self.conversations[channel_id].append({"role": "user", "content": prompt})
        self.conversations[channel_id].append({"role": "assistant", "content": response})

        
        if len(self.conversations[channel_id]) > 10:
            self.conversations[channel_id] = self.conversations[channel_id][-10:]
        
        return response
    

    def get_server_information():
        pass

async def setup(bot):
    await bot.add_cog(AIHandler(bot))