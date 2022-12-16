import os

import discord
from discord.ext import commands
from discord import utils

# MAKE SURE TO PLACE key.txt CONTAINING YOUR TOKEN IN THE ROOT FOLDER
TOKEN: str = open("../key.txt").read()

# 'client' is intentionally misspelled
clinet: discord.Client = commands.Bot(command_prefix="$")


# voice commands and events
@clinet.command(pass_context=True)
async def join(ctx):
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
async def leave(ctx):
    if not ctx.voice_client:
        await ctx.reply("I'm not in a voice channel.")
        return

    voice_client: discord.VoiceClient = utils.get(clinet.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()
    
    await ctx.guild.voice_client.disconnect()
    return 1


@clinet.command(pass_context=True)
async def play(ctx, *song_name: str):
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

    audio_source = discord.FFmpegPCMAudio(song_path)
    player = voice_client.play(source=audio_source, after=None)
    return player

@clinet.command(pass_context=True)
async def songlist(ctx):
    await ctx.send(f"Available songs: {[song_name[:-4] for song_name in os.listdir('../resources/music')]}")
    return 1
# -------------------------


clinet.run(TOKEN)