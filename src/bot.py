import os
import codecs
import time

import discord
from discord.ext import commands
from discord import utils

# MAKE SURE TO PLACE key.txt CONTAINING YOUR TOKEN IN THE ROOT FOLDER
TOKEN: str = open("../key.txt").read()

# 'client' is intentionally misspelled
clinet: discord.Client = commands.Bot(command_prefix="$")


@clinet.event
async def on_ready():
    global log
    log = codecs.open("../log.txt", "a", "utf-8")
    log.write(f"\n{time.ctime(time.time())} : Logged in as {str(clinet.user)}\n")
    return 1


# voice commands and events
@clinet.command(pass_context=True)
async def join(ctx: commands.context.Context):
    if not ctx.author.voice:
        await ctx.reply("You must be connected to a voice channel for me to join.")
        return
    
    voice_client: discord.VoiceClient = utils.get(clinet.voice_clients, guild=ctx.guild)
    author_voice: discord.VoiceChannel = ctx.message.author.voice.channel
    if voice_client and voice_client.is_connected():
        await voice_client.move_to(author_voice)
        return 1

    await author_voice.connect()
    return 1


@clinet.command(pass_context=True)
async def leave(ctx: commands.context.Context):
    if not ctx.voice_client:
        await ctx.reply("I'm not in a voice channel.")
        return

    voice_client: discord.VoiceClient = utils.get(clinet.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()
    
    await ctx.guild.voice_client.disconnect()
    return 1


@clinet.command(pass_context=True)
async def play(ctx: commands.context.Context, *song_name: str):
    if song_name == ():
        await ctx.reply("You must specify a song name")
        return
    
    song_name: str = " ".join(song_name).lower().strip()
    song_path: str = f"../resources/music/{song_name}.mp3"
    if not os.path.exists(song_path):
        await ctx.reply("Couldn't find that song. Type $songlist show available songs.")
        return

    if not await join(ctx):
        return

    voice_client: discord.VoiceClient = utils.get(clinet.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()

    audio_source: discord.FFmpegPCMAudio = discord.FFmpegPCMAudio(song_path)
    voice_client.play(source=audio_source, after=None)
    return 1

@clinet.command(pass_context=True)
async def songlist(ctx: commands.context.Context):
    await ctx.send(f"Available songs: {[song_name[:-4] for song_name in os.listdir('../resources/music')]}")
    return 1
# -------------------------


# Message event
def log_message(message: discord.Message):
    if not message.channel.type == discord.ChannelType.private:
        channel_name: str = str(message.channel.name)
    else:
        channel_name: str = str(message.channel)
    log.write(f"{time.ctime(time.time())} : {message.guild.name} : {channel_name} : {str(message.author)} : {str(message.content)}\n")
    return 1


@clinet.event
async def on_message(message: discord.Message):
    author: discord.member.Member = message.author
    if author == clinet.user:
        return
    user_name, user_tag = str(author).split("#")
    content: str = str(message.content)
    channel: discord.ChannelType = message.channel
    if not channel.type == discord.ChannelType.private:
        channel_name: str = str(channel.name)
    else:
        channel_name: str = str(channel)
    
    log_message(message)

    # message processing goes here

    await clinet.process_commands(message)
    return 1
# -------------


# Error handling
@clinet.event
async def on_command_error(ctx: commands.context.Context, error: commands.errors.CommandError):
    match error:
        case commands.errors.CommandNotFound():
            message: str = "I don't know that command."
        case _:
            pass
    await ctx.reply(message)
    return 1
# --------------


clinet.run(TOKEN)
