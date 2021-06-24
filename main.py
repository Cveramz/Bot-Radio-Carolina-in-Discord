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
@bot.command()
async def comandos(ctx):
    embed=discord.Embed(title="COMANDOS", color=0xff0000)
    embed.set_thumbnail(url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.add_field(name="Conectar a canal", value="radio! conectar", inline=False)
    embed.add_field(name="Desconectar", value="radio! desconectar", inline=True)
    embed.add_field(name="Volumen (1-100)", value="radio! volumen", inline=True)
    embed.add_field(name="Pagina web", value="radio! web", inline=True)
    embed.add_field(name="Noticias", value="radio! noticias", inline=True)
    embed.add_field(name="Redes Sociales", value="radio! rs", inline=True)
    embed.add_field(name="Programas", value="radio! programas", inline=True)
    embed.add_field(name="Mood", value="radio! mood", inline=True)
    embed.add_field(name="Podcast", value="radio! podcast", inline=True)
    embed.add_field(name="Contacto desarrollador: ", value="Instagram: @crackhogg", inline=True)
    embed.set_footer(text="(Considerar espacios)")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Comandos solicitados por este servidor")
@bot.command()
async def web(ctx):
    embed=discord.Embed(title="PÁGINA WEB", url="https://www.carolina.cl/", description="¡Haz click en el titulo para ir a la página!", color=discord.Color.red())
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/KjW19D22/Logo-Sitio-Web.png")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Web solicitada por este servidor")
@bot.command()
async def noticias(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://www.carolina.cl/noticias/", description="Para entrar a la sección de noticias de CAROLINA.CL haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/KjW19D22/Logo-Sitio-Web.png")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Noticias: solicitado por este servidor")
@bot.command()
async def programas(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://www.carolina.cl/programas/", description="Para ver los programas de CAROLINA.CL haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/KjW19D22/Logo-Sitio-Web.png")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- programas: solicitado por este servidor")
@bot.command()
async def mood(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://www.carolina.cl/#mood", description="Para ver el apartado de #mood de CAROLINA.CL haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/KjW19D22/Logo-Sitio-Web.png")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- mood: solicitado por este servidor")
@bot.command()
async def podcast(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://www.carolina.cl/senal-en-vivo/#podcast", description="Para entrar al PODCAST de CAROLINA.CL haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/KjW19D22/Logo-Sitio-Web.png")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- podcast: solicitado por este servidor")
@bot.command()
async def rs(ctx):
    print(ctx.guild.name+" <- Redes sociales: Solicitado por este servidor")
    embed=discord.Embed(title="Redes sociales", color=0xff0000)
    embed.set_thumbnail(url="https://i.postimg.cc/qqGx5Y73/1573754720-627318-1575646049-noticia-normal.jpg")
    embed.add_field(name="Spotify", value="radio! spotify", inline=True)
    embed.add_field(name="Facebook", value="radio! facebook", inline=True)
    embed.add_field(name="Twitter", value="radio! twitter", inline=True)
    embed.add_field(name="Instagram", value="radio! instagram", inline=True)
    embed.add_field(name="Youtube", value="radio! youtube", inline=True)
    embed.add_field(name="Tik Tok", value="radio! tiktok", inline=True)
    embed.set_footer(text="Revisa más comandos con ***radio! comandos**")
    await ctx.send(embed=embed)

@bot.command()
async def spotify(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://open.spotify.com/user/radiocarolina993", description="Para entrar al Spotify haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/tRFS6v9y/Color-Spotify-Logo.jpg")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Spotify: solicitado por este servidor")
@bot.command()
async def facebook(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://www.facebook.com/RADIOCAROLINA/", description="Para entrar al Facebook haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/N0WD9mV5/facebook-logo-icon-134597.png")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Facebook: solicitado por este servidor")
@bot.command()
async def twitter(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://twitter.com/RadioCarolina", description="Para entrar al Twitter haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/50d5N1Yz/twitter-bird-white-on-blue.jpg")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Twitter: solicitado por este servidor")
@bot.command()
async def instagram(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://www.instagram.com/radiocarolina/", description="Para entrar al Instagram haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/zvqnKjkX/como-ocultar-mensajes-dms-de-instagram-conversaciones-andoid-ios-cover-e1600965280592.jpg")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Instagram: solicitado por este servidor")
@bot.command()
async def youtube(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://www.youtube.com/user/yoveocarolina", description="Para entrar al canal de Youtube haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/Yqq6Sd9d/youtube-logo-81-1024x228.png")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Youtube: solicitado por este servidor")
@bot.command()
async def tiktok(ctx):
    embed=discord.Embed(title="¡HAZ CLICK AQUÍ!", url="https://vm.tiktok.com/ZMehRUY6L/", description="Para entrar al Tik Tok de CAROLINA.CL haz click arriba.")
    embed.set_author(name="CAROLINA.CL", icon_url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.set_thumbnail(url="https://i.postimg.cc/L8GLNRVW/tik-tok-para-empresas.jpg")
    embed.set_footer(text="Revisa más comandos con ***radio! comandos***")
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Tik Tok: solicitado por este servidor")

@bot.command()
async def contacto(ctx):
    embed=discord.Embed(title="CONTACTO", url="https://www.carolina.cl/page/contacto.html", color=0xff0000)
    embed.set_thumbnail(url="https://i.postimg.cc/SR6PdD8X/image.jpg")
    embed.add_field(name="Avenida Vicuña Mackenna #1370", value="Ñuñoa, Santiago Chile", inline=False)
    embed.add_field(name="Telefono:", value="+56962458214", inline=True)
    embed.add_field(name="Correo Electronico:", value="contacto@carolina.cl", inline=True)
    await ctx.send(embed=embed)
    print(ctx.guild.name+" <- Contado solicitado por este servidor")



@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Escuchando radio CAROLINA, usa: radio! comandos", url="https://www.carolina.cl"))
    print("Bot iniciado")

bot.add_cog(RADIO(bot))
bot.run(token)
