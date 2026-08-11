import logging

from bot.discord_init import DiscordBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

bot = DiscordBot()
bot.run_bot()
