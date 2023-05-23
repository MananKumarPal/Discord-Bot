import discord
import os
import asyncio
import youtube_dl
import time

token = "insert your token here" 
voice_clients = {}

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

ffmpeg_options = {'options': "-vn"}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = discord.Client(intents=intents)

block_words = ["gaali", "kutta"]   #"http://", "https://"

# Function to check if the message is from a moderator
def is_moderator(message):
    return "Moderator" in [role.name for role in message.author.roles]

# Function to check if the message contains a blocked word
def contains_blocked_word(message):
    for word in block_words:
        if word in message.content.lower():
            return True
    return False

# Event for when the bot logs in
@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")

# Event for when a message is received
@client.event
async def on_message(message):
    # Ignore messages from the bot
    if message.author == client.user:
        return
    
    # Greet user if they say hi
    if message.content.lower().startswith("?hi"):
        await message.channel.send(f"Hi, {message.author.display_name}")
    
    # Check if message contains blocked word and delete it if not from moderator
    if contains_blocked_word(message) and not is_moderator(message):
        await message.delete()
    
    # Voice commands
    if message.content.startswith("?play"):
        try:
            voice_client = await message.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except:
            print("error")

        try:
            url = message.content.split()[1]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

            voice_clients[message.guild.id].play(player)

        except Exception as err:
            print(err)


    if message.content.startswith("?pause"):
        try:
            voice_clients[message.guild.id].pause()
        except Exception as err:
            print(err)

    # This resumes the current song playing if it's been paused
    if message.content.startswith("?resume"):
        try:
            voice_clients[message.guild.id].resume()
        except Exception as err:
            print(err)

    # This stops the current playing song
    if message.content.startswith("?stop"):
        try:
            voice_clients[message.guild.id].stop()
            await voice_clients[message.guild.id].disconnect()
        except Exception as err:
            print(err)

client.run(token)

   # ?hi - Sends a greeting message to the user who sent this command.
   # Blocking specific words - If any of the words in the block_words list are present in a user's message, the bot deletes the message.
   # ?play <url> - Plays the audio from the given YouTube video URL in the voice channel of the user who sent the command.
   # ?pause - Pauses the currently playing audio in the voice channel.
   # ?resume - Resumes the currently paused audio in the voice channel.
   # ?stop - Stops the currently playing audio in the voice channel and disconnects the bot from the voice channel.
