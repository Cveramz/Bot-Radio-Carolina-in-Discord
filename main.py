import discord
from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.utils import get
from discord import Embed
from random import choice
from discord.ext.commands import Cog
from discord.ext.commands import has_permissions
import asyncio
import youtube_dl
token="ESCRIBIR AQUÍ TOKEN DE BOT"

bot = commands.Bot(command_prefix = "radio! ", description="Carolina.cl")
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' 
}
ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class RADIO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def soloconectar(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def conectar(self, ctx, *, url: str = 'http://unlimited3-cl.dps.live/carolinafm/aac/icecast.audio'):
        try:
          async with ctx.typing():
              await ctx.reply("Cargando. . . . ",mention_author=True)
              player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
              ctx.voice_client.play(player, after=lambda e: print(f'Error de reproducción: {e}') if e else None)
          embed = discord.Embed(title=f"CAROLINA.CL", description=f'Estás escuchando Radio Carolina!\n\nCambia el volumen con ***radio! volumen [x]*** (X puede ser un numero de 0 a 100)\nResvisa el listado de comandos con ***radio! ayuda***', color=discord.Color.blue() )
          embed.set_thumbnail(url=f"https://i.postimg.cc/5NyDcqwC/Logo-Radio-Carolina-2020.png")
          await ctx.reply(embed=embed, mention_author=True)
          print(ctx.guild.name+" <- Ha sido conectada la radio desde este servidor")
        except:
          await ctx.send("Error con el enlace o error para conectar al canal. Contactar a @cvr#2378")
    @commands.command()
    async def volumen(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("¡No estás conectado a un canal de sonido!.")
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Has cambiado el volumen a: {volume}%")
    @commands.command()
    async def desconectar(self, ctx):
        embed = discord.Embed(title=f"CAROLINA.CL", description=f'La radio se ha detenido\nResvisa el listado de comandos con ***radio! ayuda***', color=discord.Color.red() )
        embed.set_thumbnail(url=f"https://i.postimg.cc/5NyDcqwC/Logo-Radio-Carolina-2020.png")
        await ctx.reply(embed=embed, mention_author=True)
        print(ctx.guild.name+" <-Radio Desconectada de este servidor")
        await ctx.voice_client.disconnect()

    @conectar.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Escuchando radio CAROLINA, usa: radio! comandos", url="https://www.carolina.cl"))
    print("Bot iniciado")

bot.add_cog(RADIO(bot))
bot.run(token)
