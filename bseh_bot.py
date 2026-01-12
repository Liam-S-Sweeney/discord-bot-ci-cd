# Required Libraries
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
from PIL import Image

# Global Variables
from misc_global_var import *
from verification_survey import *

# Keep Bot Running
from keep_bot_running import keep_running
keep_running()

# API Keys
load_dotenv()
discord_token = os.getenv('discord_api_token')
print("Token loaded?", discord_token is not None)

COMMAND_LIST = [
'list here'
]

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Bot is ready to use!\n---------------------\n')
    start_leaderboard_task(bot)
    STARTUP_CHANNEL_ID = 1449952821645414501
    channel = bot.get_channel(STARTUP_CHANNEL_ID)
    if channel:
        await channel.send("Bot restarted and is online!")

###

@bot.command()
async def test(ctx):
    await ctx.send('testing if vm is alive and working | TAKE 2')

###

@bot.command()
async def hello(ctx):
    await ctx.send('Hello! I am BSEH Bot, here to assist you!')

###

@bot.command()
async def goodbye(ctx):
    await ctx.send('Goodbye! I hope to see you again soon!')

###

@bot.command()
async def love (ctx, member: discord.Member):
    await ctx.send(f'Love u, {member.mention} <3')

###

@bot.command()
async def cock(ctx):
    await ctx.send(random.choice(SAFE_CHICKEN_GIFS))

###

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

###

@bot.command()
async def bot_help(ctx):
    await ctx.send(f'Available commands: {", ".join(COMMAND_LIST)}')

###

@bot.event
async def on_member_remove(member):
    print(f'{member} has left the server.')
    channel = bot.get_channel(GENERAL_ID)
    await channel.send(f'{member} has left the server.')

###

@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    role = guild.get_role(UNVERIFIED_ID)
    if role == None:
        print(f"Role with ID {UNVERIFIED_ID} not found in guild {guild.name}.")
        return
    
    try:
        await member.add_roles(role, reason="Assigning unverified role on join")
        print(f'{member} has joined the server.')
        channel = bot.get_channel(GENERAL_ID)
        await channel.send(f'Welcome {member.mention} to Boston Social Events Hub! Please verify yourself by using the `!verify` command in #General to become a member.')

    except discord.Forbidden:
        print("Missing permissions to add roles (check role order & Manage Roles).")
    except Exception as e:
        print(f"Failed to assign 'Unverified' role to {member.name}: {e}")

###

@bot.command(name='verify')
async def star_verification(ctx: commands.Context):
    user = ctx.author
    member = ctx.author

    if member.roles == None:
        print(member.roles)
        await ctx.reply(f"{member.mention}is not currently assigned a role.")
        return
    elif any(role.id in [MEMBER_ID, VERIFYING_ID] for role in member.roles):
        await ctx.reply(f"{member.mention} is not unverified.")
        return

# Only allow in this guild (not DMs with random guilds)
    if ctx.guild is None:
        await ctx.send("Run this command in the server, not in DMs.")
        return

    # Try moving conversation to DM
    try:
        dm = await user.create_dm()
        await dm.send(
            "Please fill out this quick verification questionnaire to become a member.\n"
        )
    except discord.Forbidden:
        await ctx.reply("I can't DM you. Please enable DMs from server members and try again.")
        return

    answers = []

    def check(m: discord.Message):
        return m.author == user and isinstance(m.channel, discord.DMChannel)

    for q in QUESTIONS:
        await dm.send(q)
        msg = await bot.wait_for("message", check=check)
        answers.append(msg.content)

    await dm.send("Thanks! Your answers have been sent to the admins for review.")

    # Post answers to staff review channel as an embed
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return

    member = guild.get_member(user.id)
    if member is None:
        return

    review_channel = guild.get_channel(REVIEW_CHANNEL_ID)
    if review_channel is None:
        return

    embed = discord.Embed(
        title="New Verification Questionnaire",
        description=f"User: {member.mention} (`{member.id}`)",
        color=discord.Color.blue(),
    )
    for i, (q, a) in enumerate(zip(QUESTIONS, answers), start=1):
        embed.add_field(name=f"Q{i}: {q[:61]}", value=a[:25] or "No answer", inline=False)

    await review_channel.send(embed=embed)

    # Change roles: Unverified -> Verifying
    unverified = guild.get_role(UNVERIFIED_ID)
    verifying = guild.get_role(VERIFYING_ID)

    roles_to_add = []
    roles_to_remove = []

    if unverified in member.roles:
        roles_to_remove.append(unverified)
    if verifying is not None:
        roles_to_add.append(verifying)

    try:
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason="Completed questionnaire")
        if roles_to_add:
            await member.add_roles(*roles_to_add, reason="Marked as Verifying")
    except discord.Forbidden:
        print("Missing permissions while switching roles to Verifying.")
    except discord.HTTPException as e:
        print(f"Error switching roles: {e}")

###

@bot.command(name="approve")
@commands.has_permissions(manage_roles=True)
async def approve_member(ctx: commands.Context, member: discord.Member):
    if member == ctx.bot.user or member.id == ctx.bot.user.id:
        await ctx.reply("Nice try, but leave the bot alone.")
        return

    if member is None:
        await ctx.reply("Please specify a valid member to approve | Usage: `!approve @user`")
        return
    
    guild = ctx.guild
    if guild is None:
        await ctx.reply("This command must be used in a server.")
        return

    verifying = guild.get_role(VERIFYING_ID)
    member_role = guild.get_role(MEMBER_ID)

    if member.roles == None:
        print(member.roles)
        await ctx.reply(f"{member.mention}is not currently assigned a role.")
        return
    elif any(role.id in [MEMBER_ID, UNVERIFIED_ID] for role in member.roles):
        await ctx.reply(f"{member.mention} is not currently verifying their status.")
        return


    to_add = []
    to_remove = []

    if verifying in member.roles:
        to_remove.append(verifying)
    if member_role is not None and member_role not in member.roles:
        to_add.append(member_role)

    try:
        if to_remove:
            await member.remove_roles(*to_remove, reason="Approved by admin")
        if to_add:
            await member.add_roles(*to_add, reason="Approved by admin")

        await ctx.reply(f"{member.mention} has been approved and is now a Member.")
    except discord.Forbidden:
        await ctx.reply("I don't have permission to change that member's roles.")
    except discord.HTTPException as e:
        await ctx.reply(f"Error changing roles: {e}")

###

@approve_member.error
async def approve_member_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.BadArgument):
        # e.g. "!approve some_random_text"
        await ctx.reply(
            "I couldn't find that user.\n"
            "Use a proper mention or ID, like: `!approve @username`."
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("You need the `Manage Roles` permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Please specify a member to approve. Usage: `!approve @user`")
    else:
        # Fallback: log but don't spam the channel
        print(f"Unexpected error in !approve: {error!r}")

###

@bot.command(name="reject")
@commands.has_permissions(manage_roles=True)
async def reject_member(ctx: commands.Context, member: discord.Member):
    if member == ctx.bot.user or member.id == ctx.bot.user.id:
        await ctx.reply("Nice try, but leave the bot alone.")
        return
    
    guild = ctx.guild
    if guild is None:
        await ctx.reply("This command must be used in a server.")
        return

    unverified = guild.get_role(UNVERIFIED_ID)
    verifying = guild.get_role(VERIFYING_ID)

    if member.roles == None:
        print(member.roles)
        await ctx.reply(f"{member.mention}is not currently assigned a role.")
        return
    elif any(role.id in [MEMBER_ID, UNVERIFIED_ID] for role in member.roles):
        await ctx.reply(f"{member.mention} is not currently verifying their status.")
        return

    to_add = []
    to_remove = []

    if verifying in member.roles:
        to_remove.append(verifying)
    if unverified is not None and unverified not in member.roles:
        to_add.append(unverified)

    try:
        if to_remove:
            await member.remove_roles(*to_remove, reason="Rejected by admin")
        if to_add:
            await member.add_roles(*to_add, reason="Rejected by admin")

        await ctx.reply(f"{member.mention} has been moved back to Unverified.")
        await member.send("Your verification has been rejected by the admins. Please reattempt verification using the `!verify` command.")
    except discord.Forbidden:
        await ctx.reply("I don't have permission to change that member's roles.")
    except discord.HTTPException as e:
        await ctx.reply(f"Error changing roles: {e}")

###

@reject_member.error
async def reject_member_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.BadArgument):
        # e.g. "!approve some_random_text"
        await ctx.reply(
            "I couldn't find that user.\n"
            "Use a proper mention or ID, like: `!reject @username`."
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("You need the `Manage Roles` permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Please specify a member to reject. Usage: `!reject @user`")
    else:
        print(f"Unexpected error in !reject: {error!r}")

###

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("Unknown command. Please check your input.")
        return

    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don't have permission to use that command.")
        return

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("You're missing a required argument for that command.")
        return
    else:
        print(f"Unhandled error in command {getattr(ctx.command, 'name', None)}: {repr(error)}")
        return


bot.run(discord_token)

