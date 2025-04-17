import discord
from discord.ext import commands
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
import ThinkerBoxAI

def run_bot():
    load_dotenv()
    DISCORD_TOKEN = os.getenv("discord_token")
    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    intents.members = True
    client = commands.Bot(command_prefix= "?", intents = intents)

    CurrentPosInQueue = {}
    loopSingleSwitches = {}
    loopAllSwitches = {}
    queues = {}
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

    @client.event
    async def on_ready():
        print(f"{client.user} is now thinking...")
        await client.change_presence(activity=discord.CustomActivity(name='Thinking...' ,emoji='📦'))
    
    @client.event
    async def on_member_join(member):
        await member.send("**Haku welcomes you to 3 AM! Don't get sleepy now...**")

        role = discord.utils.get(member.guild.roles, name="Thiếu Ngủ")
        await member.add_roles(role)


    @client.event
    async def on_message(message):

        await client.process_commands(message)

    async def play_next(ctx, link):
        if ctx.guild.id not in loopSingleSwitches:
            loopSingleSwitches[ctx.guild.id] = False
        if ctx.guild.id not in loopAllSwitches:
            loopAllSwitches[ctx.guild.id] = False

        if loopSingleSwitches[ctx.guild.id] == True:
            await play(ctx, link, insert= False)

        elif loopAllSwitches[ctx.guild.id] == True:
            if queues[ctx.guild.id] != []:
                link = queues[ctx.guild.id].pop(0)
                await play (ctx, link, insert= True)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     

        elif queues[ctx.guild.id] != []: # if song queue is not empty
            queues[ctx.guild.id].pop(0) # pop to remove the previous song

            if queues[ctx.guild.id] != []: # play the next song if there is one lol
                link = queues[ctx.guild.id][0]
                print(link)
                await play(ctx, link, insert= False)

    @client.command(name ="play")

    async def play(ctx, link: str, insert= True):

        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

        except Exception as e:
            print(e)

        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = []
        
        if insert == True:
            queues[ctx.guild.id].append(link)

        try:
            

            if ctx.voice_client.is_playing(): #add to queue if a song is already playing
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download= False))
                # queues[ctx.guild.id].append(link)
                songName = data['title']
                await ctx.send(f"{songName} **is added to queue.**")

            else: #play the song
                link = queues[ctx.guild.id][0]
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download= False))
                song = data['url']
                songName = data['title']
                player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
                await ctx.send(f"**Now playing:** {songName}", delete_after= 30, silent= True)
                
                voice_clients[ctx.guild.id].play(player, after= lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx, link), client.loop))
            
        except Exception as e:
            print(e)

    @client.command(name = "pause")
    async def pause(ctx):
        try:
            voice_clients[ctx.guild.id].pause()
        except Exception as e:
            print(e)
    
    @client.command(name = "resume")
    async def resume(ctx):
        try:
            voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(e)
    
    @client.command(name = "stop")
    async def stop(ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]
            del loopSingleSwitches[ctx.guild.id]
            del loopAllSwitches[ctx.guild.id]
            del queues[ctx.guild.id]

        except Exception as e:
            print(e)
    
    @client.command(name= "skip")
    async def skipSong(ctx):

        voice_clients[ctx.guild.id].stop()

    @client.command(name= "queue")
    async def queue(ctx):

        if queues[ctx.guild.id] == []:
            await ctx.send("Queue is empty. *Just like my soul*.")
        else:
            for i in range(len(queues[ctx.guild.id])):
                await ctx.send(f"{i+1}. {queues[ctx.guild.id][i]}")

    @client.command(name = "clearqueue")
    async def clearQueue(ctx):
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
            await ctx.send("Queue cleared!")
        else:
            await ctx.send(f"{client.user} thinks that there is no queue to clear...")

    @client.command(name = "loop")
    async def singleLoop(ctx, mode):
        if mode == "single":

            if ctx.guild.id not in loopSingleSwitches:
                loopSingleSwitches[ctx.guild.id] = []
            if ctx.guild.id not in loopAllSwitches:
                loopSingleSwitches[ctx.guild.id] = []

            loopSingleSwitches[ctx.guild.id] = True
            loopAllSwitches[ctx.guild.id] = False

            await ctx.send("**Now looping one song!**")

        elif mode == "all":

            if ctx.guild.id not in loopSingleSwitches:
                loopSingleSwitches[ctx.guild.id] = []
            if ctx.guild.id not in loopAllSwitches:
                loopSingleSwitches[ctx.guild.id] = []

            loopAllSwitches[ctx.guild.id] = True
            loopSingleSwitches[ctx.guild.id] = False

            await ctx.send("**Now looping all songs**!")

        elif mode == "off":
            if ctx.guild.id in loopSingleSwitches:
                try:
                    loopSingleSwitches[ctx.guild.id] = False
                    loopAllSwitches[ctx.guild.id] = False
                except Exception as e:
                    print(e)

            await ctx.send("**Stopped looping.**")

    client.run(DISCORD_TOKEN)
