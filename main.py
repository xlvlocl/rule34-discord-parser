import os

import Logger
import disnake
from disnake.ext import commands
import config

logger = Logger.Logger()
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(config.config['prefix']),
    intents=disnake.Intents.all(),
    owner_id=int(config.config["ID"])
)

bot.remove_command("help")


@bot.listen("on_ready")
async def start():
    await bot.wait_until_ready()
    logger.info(f"{bot.user} запущен!")


@bot.command()
async def reload(ctx, module: str = None):
    if ctx.author.id == int(config.config["ID"]):
        if module is None:
            for filename in os.listdir("./moduls"):
                if filename.endswith(".py"):
                    try:
                        bot.reload_extension(f"moduls.{filename[:-3]}")
                    except:
                        pass
            await ctx.send("Все модули перезагружены!", delete_after=10)
        else:
            try:
                bot.reload_extension(f"moduls.{module}")
            except:
                pass
            await ctx.send(f"Модуль {module} перезагружен!", delete_after=10)
        await ctx.message.delete()
    else:
        await ctx.message.delete()


def load_extensions():
    for filename in os.listdir("./moduls"):
        if filename.endswith(".py"):
            bot.load_extension(f"moduls.{filename[:-3]}")
            logger.info(f"Загрузил модуль {filename}")


load_extensions()
bot.run(config.config['token'])
