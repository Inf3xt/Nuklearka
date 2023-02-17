import os
import json
import asyncio
import traceback
from pathlib import Path

import discord
from discord.ext import commands

with open('creds.json', 'r') as f:
    data = json.load(f)

clear = lambda: os.system('clear' if not os.name == 'nt' else 'cls')

bot = commands.Bot(
    command_prefix=data['prefix'],
    intents=discord.Intents.all(),
    case_insensitive=True
)
bot.remove_command("help")

cwd = Path(__file__).parents[0]
cwd = str(cwd)
cogs_folder = f"{cwd}/cogs"
cogs_folder_contents = len([name for name in os.listdir(cogs_folder) if os.path.isfile(os.path.join(cogs_folder, name))])
cogs_folder_contents = cogs_folder_contents + 1

@bot.event
async def on_ready():
    print("You are online and ready!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="people initialise classes."))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, discord.ext.commands.errors.NotOwner):
        print(f"{ctx.author} just tried to access admin commands")
    elif isinstance(error, commands.CommandOnCooldown):
        print(f"Command on cooldown, try again in {error.retry_after:.2f}s")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == "shutdown":
        print(f"{bot.user.name} is offline!")
        await bot.close()
    await bot.process_commands(message)

@bot.command(aliases=['sd'])
@commands.is_owner()
async def shutdown(ctx):
    print(f"{bot.user.name} is offline!")
    await bot.close()

@bot.command(name="reload")
@commands.is_owner()
async def _reload(ctx, cog=None):
    if not cog:
        async with ctx.typing():
            await ctx.send("Reloading all cogs")

            for ext in os.listdir("./cogs/"):
                if ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        await bot.unload_extension(f"cogs.{ext[:-3]}")
                        await bot.load_extension(f"cogs.{ext[:-3]}")
                        await ctx.send("Reloaded `EVERYTHING!`")
                    except Exception as e:
                        await ctx.send("Failed to reload {}\nException: {}".format(ext, e))
                    await asyncio.sleep(0.5)
    else:
        ext = f"{cog.lower()}.py"
        if not os.path.exists(f"./cogs/{ext}"):
            await ctx.send("Failed to reload {} as it does not exist".format(ext))
        elif ext.endswith('.py') and not ext.startswith('_'):
            try:
                await bot.unload_extension(f"cogs.{ext[:-3]}")
                await bot.load_extension(f"cogs.{ext[:-3]}")
                await ctx.send("Reloaded `{}`".format(ext))
            except Exception:
                desired_trace = traceback.format_exc()
                await ctx.send("Failed to reload {}\nException: {}".format(ext, desired_trace))
                await asyncio.sleep(0.5)

async def load_extensions():
    for file in os.listdir(f'{cwd}/cogs'):
        if file.endswith(".py") and not file.startswith("_"):
            await bot.load_extension(f'cogs.{file[:-3]}')

async def start_bot():
    async with bot:
        clear()
        await load_extensions()
        await bot.start(data['token'])


if __name__ == '__main__':
    asyncio.run(start_bot())