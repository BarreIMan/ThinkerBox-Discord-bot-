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

    AI_Cooldown_For_User = {}
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

    async def play_next(ctx, link):
        if ctx.guild.id in loopSingleSwitches:
            if loopSingleSwitches[ctx.guild.id] == True:
                await play(ctx, link)

            elif queues[ctx.guild.id] != []: # if song queue is not empty
                link = queues[ctx.guild.id].pop(0)
                await play(ctx, link)

    @client.command(name= "history")
    async def get_history(ctx):
        channel = ctx.channel
        history_log = ""
        messages = [message async for message in channel.history(limit=50)]

        for message in range(len(messages)-1, -1, -1):
            text = messages[message]
            # print(f"Time:{text.created_at}| UserID: {text.author.id} | User {text.author} said: {text.clean_content}")
            history_log += f"Time:{text.created_at}| UserID: {text.author.id} | User {text.author} said: {text.clean_content}\n\n"
            


    @client.command(name ="play")

    async def play(ctx, link):
        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

        except Exception as e:
            print(e)

        try:

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download= False))

            if 'entries' in data:
                data = data['entries'][0]

            if ctx.voice_client.is_playing(): #add to queue if a song is already playing
                if ctx.guild.id not in queues:
                    queues[ctx.guild.id] = []
                
                queues[ctx.guild.id].append(link)
                songName = data['title']
                await ctx.send(f"{songName} **is added to queue.**")

            else: #play the next song normally if there is a next song else just ends
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
                try:
                    loopSingleSwitches[ctx.guild.id] = []
                except Exception as e:
                    print(e)

            loopSingleSwitches[ctx.guild.id] = True

            await ctx.send("**Now looping one song!**")
        elif mode == "all":
            await ctx.send("**Now looping all songs**!")
        elif mode == "off":
            if ctx.guild.id in loopSingleSwitches:
                try:
                    loopSingleSwitches[ctx.guild.id] = False
                except Exception as e:
                    print(e)

            await ctx.send("**Stopped looping.**")

    client.run(DISCORD_TOKEN)
