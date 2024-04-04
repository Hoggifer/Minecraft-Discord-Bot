from datetime import datetime, timedelta, timezone
import minestat
import discord
from discord.ext import commands
import asyncio

# Bot will listen for the "/" prefix, change the sign to whatever suits you.
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# This Section is for Player Last Seen 

# Dictionary to hold player last seen timestamps
player_last_seen = {}

def format_timedelta(td):
    """Format a timedelta object into a string showing days, hours, and minutes."""
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days = td.days
    return f"{days}d, {hours}h, {minutes}m ago"

# Alive Check.
@bot.event
async def on_ready():
    print(f"Hoggifer's Minecraft Server Status Bot |")


@bot.command()
async def servermonitorsetup(ctx, server_info: str):
    def get_server_status_embed(ip_address, subnet_mask):
        global player_last_seen

        ms = minestat.MineStat(ip_address, int(subnet_mask))
        current_players = set(ms.player_list) if ms.player_list else set()
        now = datetime.now(timezone.utc)

        # Update last seen for current players
        for player in current_players:
            player_last_seen[player] = now

        # Find players not in current list and calculate time since last seen
        missing_players_info = []
        for player, last_seen in player_last_seen.items():
            if player not in current_players:
                time_since_seen = format_timedelta(now - last_seen)
                missing_players_info.append(f"{player} ({time_since_seen})")

        missing_players_str = "\n".join(missing_players_info) if missing_players_info else "All active players are currently online."
        # This function encapsulates the logic to query the server
        # and create an embed with the server status.

        if ms.online:
            embed = discord.Embed(
                title=f'Minecraft Server - {ms.address}:{ms.port}',
                description="Built by Hoggifer and made possible by the Minestat Team!",
                url="https://github.com/Hoggifer/Minecraft-Discord-Bot",
                color=discord.Color.green()
            )
            embed.add_field(name="Server Version", value=ms.version, inline=False)
            embed.add_field(name="MOTD", value=ms.stripped_motd, inline=False)
            if ms.gamemode:
                embed.add_field(name="Game Mode", value=ms.gamemode, inline=False)
            embed.add_field(name="Latency", value=f'{ms.latency}ms', inline=False)
            embed.add_field(name="Players", value=f'{ms.current_players} / {ms.max_players}', inline=False)
            # embed.add_field(name="Protocol", value=ms.slp_protocol, inline=False)
            player_list_str = ', '.join(current_players) if current_players else "Not Available"
            if ms.player_list:
                embed.add_field(name="Player List", value=player_list_str, inline=False)
            embed.add_field(name="Missing Players", value=missing_players_str, inline=False)
        else:
            embed = discord.Embed(title=f'Minecraft Server: {ip_address}', description="Server is offline!", color=discord.Color.red())

        return embed

    ip_address, subnet_mask = server_info.split(':') if ':' in server_info else (server_info, "25565")
    embed = get_server_status_embed(ip_address, subnet_mask)
    status_message = await ctx.send(embed=embed)

    async def update_status():
        while True:
            await asyncio.sleep(60)  # Wait for 1 minutes
            # Update the embed with the latest server status
            embed = get_server_status_embed(ip_address, subnet_mask)
            await status_message.edit(embed=embed)

    # Start the background task to update the status message
    bot.loop.create_task(update_status())

# Run the bot with your token
bot.run('BOT_TOKEN)
