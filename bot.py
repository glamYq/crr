# импортируем библиотеки
import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os

PREF = '-'
cll = commands.Bot(command_prefix='-')  # префикс для команд
cll.remove_command('help')

# Списки плохих слов
badwrld = ['дурак']  # тут могут быть плохие слова


@cll.event
async def on_ready():
    print('conected')
    await cll.change_presence(status=discord.Status.online, activity=discord.Game("-help"))


@cll.event
async def on_cmd_error(ctx, error):
    pass


# авто-выдача роли
@cll.event
async def on_member_join(member):
    channel = cll.get_channel(701707673359482964)  # !!!сюда вставить ID канала куда присоеденяются люди

    role = discord.utils.get(member.guild.roles, id=701932367052537896)  # !!!сюда вставить какую роль выдавать
    await member.add_roles(role)
    await channel.send(emb=discord.Embed(discription=f'Ишну-ала,{member.name}', colour=discord.dark_gold()))


# Добавим филтр сообщений
@cll.event
async def filter(message):
    await cll.process_commands(message)

    msg = message.content.lower()

    if msg in badwrld:
        await message.delete()
        await message.author.send(f'{message.author.name}, не пиши таких слов больше, пожалуйста.')


# Очистка сообщений
@cll.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=1)
    await ctx.channel.purge(limit=amount)


# Кик и бан участников
@cll.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)
    await member.kick(reason=reason)


@cll.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)

    emb = discord.Embed(title='Бан', colour=discord.Colour.orange())
    await member.ban(reason=reason)

    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name='Забанен участник: {member.mention}', value='Забанен участник: {member.mention}')

    await ctx.send(embed=emb)


# await ctx.send(f'Забанен участник{member.mention}')


# Если есть бан, то можно и разбанить
@cll.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    await ctx.channel.purge(limit=1)

    ban_list = await ctx.guild.bans()

    for banned in ban_list:
        user = banned.user
        await ctx.guild.unban(user)
        await ctx.send(f"Разбанен {user.mention}")
        retun


# Команда help
@cll.command()
async def help(ctx):
    await ctx.channel.purge(limit=1)

    emb = discord.Embed(title='Команды', colour=discord.Colour.purple())
    emb.add_field(name='-clear', value='Очистка чата')
    emb.add_field(name='-vjoin', value='Присоединение к голосовому каналу в котором вы находитесь')
    emb.add_field(name='-vleave', value='Отключение от голосового канала')
    emb.add_field(name='-play (ссылка)', value='Проигрывание музыки по ссылке с ютуба')
    emb.add_field(name='-rules', value='Правила сервера')
    emb.add_field(name='-mute', value='Ограничить доступ к чату')
    emb.add_field(name='-kick', value='Удаление участника сервера (доступно админам)')
    emb.add_field(name='-ban', value='Ограничение достпа участника к серверу (доступно админам)')
    emb.add_field(name='-unban',
                  value='Удаление ограничения достпа участника к серверу (доступно админам)')

    await ctx.send(embed=emb)


@cll.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)

    mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')

    await member.add_roles(mute_role)
    await ctx.send(f'Участнику:{member.mention}, выдали ограничение чата, за нарушение правил!')


# Присоединение к голосовому каналу
@cll.command()
async def vjoin(ctx):
    await ctx.channel.purge(limit=1)

    global voice

    channel = ctx.message.author.voice.channel
    voice = get(cll.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f'Бот присоеденился к каналу:{channel}')


# Выход с голосового канала
@cll.command()
async def vleave(ctx):
    await ctx.channel.purge(limit=1)

    channel = ctx.message.author.voice.channel
    voice = get(cll.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()
        await ctx.send(f'Бот отключился от канала:{channel}')


# Проигрывание музыки по ссылке
@cll.command()
async def play(ctx, url: str):
    _song = os.path.isfile('song.mp3')

    try:
        if _song:
            os.remove('song.mp3')

    except PermissionError:
        raise

    await ctx.send('вейт')

    voice = get(cll.voice_clients, guild=ctx.guild)
    ytd_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }

    with youtube_dl.YoutubeDL(ytd_opts) as ydl:
        ydl.download([url])

    for file in os.listdir('../'):
        if file.endswith('.mp3'):
            name = file
            os.rename(file, 'song.mp3')

    voice.play(discord.FFmpegPCMAudio('song.mp3'))

    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07  # как 100 процентов

    songname = name.rsplit('-', 2)
    await ctx.send(f'Сейчас играет музыка:{songname[0]}')


@cll.command()
async def rules(ctx):
    await ctx.author.send("Правила сервера")


@cll.command()
async def send_member():
    pass


# Прописываем ошибки для каждой команды
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.name},вы не указали аргумент")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.name},у вас недостаточно прав!")


@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.name},вы не указали пользователя")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.name},у вас недостаточно прав!")


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.name},вы не указали пользователя")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.name},у вас недостаточно прав!")


@ban.error
async def ban_error(ctx,
                    error):  # Я не рассматриваю то, что например нельзя банить админов админами, предпологается, что на сервере 1 админ.
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.name},вы не указали пользователя")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.name},у вас недостаточно прав!")


@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.name},вы не указали пользователя")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.name},у вас недостаточно прав!")


# Подсоединение

token = 'NzAxNzA2ODI5MzEwMTk3ODcx.Xp1g0g.fTAa0KbEbfBtS-H23NoT8OdhMbg'
cll.run(token)

