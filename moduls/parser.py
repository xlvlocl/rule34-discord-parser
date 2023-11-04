import datetime
import random

import disnake
import re
import requests
from disnake.ext import commands, tasks

import config


def get_list_of_urls_from_site():
    pid = 0
    page_url = []
    while True:
        url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&tags={config.config['tag']}&pid={str(pid)}"
        page_text = requests.get(url).text.replace(' ', '')
        if len(page_text) < 1000:
            break
        else:
            pid += 42
            page_text = requests.get(url).text
            urls = re.findall(r'file_url="(.*?)"', page_text)
            page_url.extend(urls)
    return page_url


async def send_to_discord(channel):
    if len(config.config['urls']) == 0:
        config.config['ended'] = True
        await channel.send("Все файлы загружены!")
    else:
        embed = disnake.Embed(color=disnake.Color.random(), timestamp=datetime.datetime.now())
        url = random.choice(config.config['urls'])
        config.config['urls'].remove(url)
        if url.endswith("mp4"):
            file = disnake.File(url)
            await channel.send(file=file)
        else:
            buttons = disnake.ui.View()
            buttons.add_item(disnake.ui.Button(label='Скачать', emoji='🔞', style=disnake.ButtonStyle.url, url=url))
            embed.set_image(url=url)
            await channel.send(embed=embed, view=buttons)


class Parser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pars.start()

    def cog_unload(self):
        self.pars.stop()
        return

    @commands.command()
    async def tag(self, ctx, tag: str):
        config.config['tag'] = tag
        config.config['ended'] = False
        self.pars.restart()
        await ctx.send(f"Тэг изменен на {tag}")

    @tasks.loop(seconds=config.config['time'])
    async def pars(self):
        await self.bot.wait_until_ready()
        if config.config['ended']:
            pass
        else:
            guild = self.bot.get_guild(config.config['guild_id'])
            channel = guild.get_channel(config.config['channel_id'])
            if self.pars.current_loop == 0:
                await channel.send(f"Начинаю загрузку ссылок по тэгу `{config.config['tag']}`.\n"
                                   f"Это происходит единожды за запуск бота "
                                   f"или после написания команды `{config.config['prefix']}reload` "
                                   f"или `{config.config['prefix']}tag`\n"
                                   f"(Может занять до нескольких минут, в это время бот не будет реагировать на команды)")
                config.config['urls'] = get_list_of_urls_from_site()
                await send_to_discord(channel)
            else:
                await send_to_discord(channel)


def setup(bot):
    bot.add_cog(Parser(bot))
