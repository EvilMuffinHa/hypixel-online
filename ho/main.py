from discord.ext.commands import Bot
from dotenv import load_dotenv
import discord
from discord.ext import tasks
import aiohttp
import os
import firebase_admin
from firebase_admin import credentials, db
# noinspection PyUnresolvedReferences
import EmbedSystem
import asyncio
import argparse
import shlex



load_dotenv()

with open("sudoers.txt", "r") as f:
	widlist = f.read()

WHITELISTED_IDS = [int(x) for x in widlist.split("\n")]
STANDARD_PREFIX = "!"


def get_prefix(client, message):
	ref = db.reference("guilds")
	if ref.get() is None:
		js = {}
	else:
		js = (ref.get())
	if message.guild:
		try:
			return js[str(message.guild.id)][0]
		except KeyError:
			return STANDARD_PREFIX
		except TypeError:
			return STANDARD_PREFIX
	else:
		return STANDARD_PREFIX


client = Bot(command_prefix=get_prefix, case_insensitive=True)
client.remove_command("help")

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
	'databaseURL': 'https://hypixelonline-35a51.firebaseio.com'
})
r = db.reference("linked")


async def get_name_from_uuid(uuid):
	async with aiohttp.ClientSession() as s:
		async with s.get(
				'https://api.hypixel.net/player?key=' + os.getenv("HYPIXELAPITOKEN") + '&uuid=' + uuid + "/") as r:
			if r.status == 200:
				html = await r.json()
				try:
					name = html["player"]["displayname"]
					return name
				except KeyError:
					return "No minecraft account found. "
			else:
				return "Connection error: ERROR " + str(r.status)


async def get_data(filename):
	ref = db.reference(filename)
	if ref.get() is None:
		return {}

	return ref.get()


async def set_data(filename, data):
	ref = db.reference(filename)
	ref.set(data)


async def prefix_writing(msg):
	ref = db.reference("guilds")
	if ref.get() is None:
		js = {}
	else:
		js = (ref.get())

	if msg.message.guild:
		try:
			return js[str(msg.message.guild.id)][0]
		except KeyError:
			return STANDARD_PREFIX
	else:
		return STANDARD_PREFIX


e_link = EmbedSystem.SimpleEmbedSystem("Connection", 0x5a8fdd, emoji="\U0001F517")
e_ukc = EmbedSystem.SimpleEmbedSystem("Unknown Command", 0x5a8fdd,
									  icon_url="https://cdn.discordapp.com/avatars/694645515983519794/9d425f6f93006a03dfa32b060a8449ee.png?size=128")
e_help = EmbedSystem.SimpleEmbedSystem("HypixelOnline Help", 0x5a8fdd,
									   icon_url="https://cdn.discordapp.com/avatars/694645515983519794/9d425f6f93006a03dfa32b060a8449ee.png?size=128")
e_bws = EmbedSystem.SimpleEmbedSystem("Bedwars Stats", 0xfefb00, emoji="🛏️")
e_info = EmbedSystem.SimpleEmbedSystem("Info", 0xe549b6,
									   icon_url="https://evilmuffinha.github.io/discord-bot/hypixel-online/files/ico.png",
									   url="https://discord.com/api/oauth2/authorize?client_id=694645515983519794&permissions=515136&scope=bot")
e_mod = EmbedSystem.SimpleEmbedSystem("Moderator Settings", 0x2d4fe5, emoji="🧰")
e_prestige = EmbedSystem.SimpleEmbedSystem("Congrats!", 0xdda9e5, emoji="🎉")
e_online = EmbedSystem.SimpleEmbedSystem("Status", 0x85e57e, emoji="🎮")
e_err = EmbedSystem.SimpleEmbedSystem("Error", 0xe8252e, emoji="❌")
e_ping = EmbedSystem.SimpleEmbedSystem("Pong!", 0x01011c, emoji="🏓")
e_sudo = EmbedSystem.SimpleEmbedSystem("Sudo", 0x000000,
									   icon_url="https://cdn.discordapp.com/avatars/694645515983519794/9d425f6f93006a03dfa32b060a8449ee.png?size=128")


@client.command(name="mod")
async def mod(msg):
	if not msg.message.guild:
		embed = EmbedSystem.SimpleEmbed(e_mod)
		embed.add_field("You must be in a discord server to perform this!", "", False)
		await stext(msg, embed)
		return
	if not msg.message.author.guild_permissions.administrator and (msg.message.author.id not in WHITELISTED_IDS) and (
			"Party Leader" not in [x.name for x in msg.message.author.roles]) and (
			"Bot Oppression" not in [x.name for x in msg.message.author.roles]) and (
			"Moderator" not in [x.name for x in msg.message.author.roles]):
		embed = EmbedSystem.SimpleEmbed(e_mod)
		embed.add_field(
			"You must have the `Administrator` permission, a role named `Party Leader`, a role named `Bot Oppression`, a role named `Moderator`, or you must be whitelisted.",
			"", False)
		await stext(msg, embed)
		return
	if len(msg.message.content.split(" ")) != 3:
		embed = EmbedSystem.SimpleEmbed(e_mod)
		embed.add_field("Please input the right arguments. Usage: `" + await prefix_writing(msg) + "mod setting value`",
						"", False)
		await stext(msg, embed)
		return
	setting = msg.message.content.split(" ")[1]
	value = msg.message.content.split(" ")[2]
	if setting == "prefix":
		js = await get_data("guilds")
		if msg.message.guild.id in js.keys():

			if js[msg.message.guild.id][1]:
				embed = EmbedSystem.SimpleEmbed(e_mod)
				embed.add_field("The prefix has been forcelocked by a sudoer!", "", False)
				await stext(msg, embed)
				return
			js[msg.message.guild.id][0] = value
		else:
			js[msg.message.guild.id] = [value, False]
		await set_data("guilds", js)
		embed = EmbedSystem.SimpleEmbed(e_mod)
		embed.add_field("Prefix set to `" + value + "`!", "", False)
		await stext(msg, embed)


@client.command(name="sudo")
async def sudo(msg):
	if msg.message.author.id not in WHITELISTED_IDS:
		embed = EmbedSystem.SimpleEmbed(e_err)
		embed.add_field(msg.message.author.name + " is not in the sudoers file. This incident will be reported. ", "",
						False)
		await stext(msg, embed)
		return
	if len(msg.message.content.split(" ")) == 1:
		embed = EmbedSystem.SimpleEmbed(e_sudo)
		embed.add_field("What are you using sudo for anyways?!??? Idiot. ", "", False)
		await stext(msg, embed)
		return
	if msg.message.content.split(" ")[1] == "say":
		parser = argparse.ArgumentParser(description='Says something')
		parser.add_argument("message", type=str, help='sends message')
		parser.add_argument("-g", "--guild", type=str, help="Specifies the server")
		parser.add_argument("-c", "--channel", type=str, help="Specifies the channel")
		parser.add_argument("-s", "--silent", help="Silences message on response. ", action="store_true")
		parser.add_argument("-d", "--dm", type=int, help="Direct messages someone. ")

		try:
			string = ' '.join(msg.message.content.split(" ")[2:])
			args = parser.parse_args(shlex.split(string))
			if not (args.guild or args.channel or args.dm):
				await msg.send(args.message)
				if not args.silent:
					embed = EmbedSystem.SimpleEmbed(e_sudo)
					embed.add_field("Message sent!", args.message, False)
					await stext(msg, embed)
				return
			elif args.channel and not args.guild and not args.dm:
				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("Please specify a guild along with the channel using -g. ", "", False)
				await stext(msg, embed)
				return
			elif args.guild and not args.channel and not args.dm:
				for guild in client.guilds:
					if guild.name == ' '.join(args.guild):
						await guild.text_channels[0].send(args.message)
						if not args.silent:
							embed = EmbedSystem.SimpleEmbed(e_sudo)
							embed.add_field("Message sent!", args.message, False)
							await stext(msg, embed)
						return
				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("Guild not found. ", "", False)
				await stext(msg, embed)
				return
			elif args.guild and args.channel and not args.dm:
				for guild in client.guilds:
					if guild.name == args.guild:
						for i in range(len(guild.text_channels)):
							if guild.text_channels[i].name == args.channel:
								await guild.text_channels[i].send(args.message)
								if not args.silent:
									embed = EmbedSystem.SimpleEmbed(e_sudo)
									embed.add_field("Message sent!", args.message, False)
									await stext(msg, embed)
								return

				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("Guild / Channel not found. ", "", False)
				await stext(msg, embed)
				return
			elif args.dm and (args.guild or args.channel):
				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("The --dm flag must be on its own! ", "", False)
				await stext(msg, embed)
			else:
				try:
					user = client.get_user(args.dm)
				except:
					embed = EmbedSystem.SimpleEmbed(e_sudo)
					embed.add_field("User not found. ", args.message, False)
					await stext(msg, embed)
					return
				await user.send(args.message)
				if not args.silent:
					embed = EmbedSystem.SimpleEmbed(e_sudo)
					embed.add_field("Message sent!", args.message, False)
					await stext(msg, embed)
				return
		except SystemExit:
			embed = EmbedSystem.SimpleEmbed(e_sudo)
			embed.add_field(parser.format_usage(), '\n'.join(parser.format_help().split("\n")[1:]), False)
			await stext(msg, embed)
	if msg.message.content.split(" ")[1] == "embed":
		parser = argparse.ArgumentParser(description="Sends an embed")
		parser.add_argument("title", type=str, help="Adds a title to the embed")
		parser.add_argument("color", type=int, help="Sets the color of the embed")
		parser.add_argument("-m", "--message", type=str, help="Adds a message along with the embed. ", default="")
		parser.add_argument("-a", "--aname", type=str, help="Sets the name of the author", default="")
		parser.add_argument("-u", "--aurl", type=str, help="Sets the url of the author", default="")
		parser.add_argument("-i", "--aicourl", type=str, help="Sets the icon url of the author", default="")
		parser.add_argument("-t", "--thumbnail", type=str, help="Sets the thumbnail of the embed", default="")
		parser.add_argument("-p", "--picture", type=str, help="Sets the image of the embed", default="")
		parser.add_argument("-o", "--footer", type=str, help="Sets the footer of the embed", default="")
		parser.add_argument("-f", "--field", nargs=3,
							help="Adds a field (usage: --field <name> <val> <inline=1/0>", default=[], action="append")
		parser.add_argument("-g", "--guild", type=str, help="Specifies the server")
		parser.add_argument("-c", "--channel", type=str, help="Specifies the channel")
		parser.add_argument("-s", "--silent", help="Silences message on response. ", action="store_true")
		parser.add_argument("-d", "--dm", type=int, help="Direct messages someone. ")
		try:
			string = ' '.join(msg.message.content.split(" ")[2:])
			args = parser.parse_args(shlex.split(string))
			if not (args.guild or args.channel or args.dm):
				embed = discord.Embed(title=args.title, author="", color=args.color)
				embed.set_author(name=args.aname, url=args.aurl, icon_url=args.aicourl)
				embed.set_thumbnail(url=args.thumbnail)
				embed.set_image(url=args.picture)
				embed.set_footer(text=args.footer)
				if args.field != "":
					for i in args.field:
						if i[2] not in ["1", "0"]:
							raise SystemExit
						embed.add_field(name=i[0], value=i[1], inline=bool(int(i[2])))
				await msg.send(args.message, embed=embed)

				if not args.silent:
					embed = EmbedSystem.SimpleEmbed(e_sudo)
					embed.add_field("Sent!", "", False)
					await stext(msg, embed)
			elif args.channel and not args.guild and not args.dm:
				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("Please specify a guild along with the channel using -g. ", "", False)
				await stext(msg, embed)
				return
			elif args.guild and not args.channel and not args.dm:
				for guild in client.guilds:
					if guild.name == ' '.join(args.guild):

						embed = discord.Embed(title=args.title, author="", color=args.color)
						embed.set_author(name=args.aname, url=args.aurl, icon_url=args.aicourl)
						embed.set_thumbnail(url=args.thumbnail)
						embed.set_image(url=args.picture)
						embed.set_footer(text=args.footer)
						if args.field != "":
							for i in args.field:
								if i[3] not in ["1", "0"]:
									raise SystemExit
								embed.add_field(name=i[0], value=i[1], inline=i[3])
						await guild.text_channels[0].send(args.message, embed=embed)
						if not args.silent:
							embed = EmbedSystem.SimpleEmbed(e_sudo)
							embed.add_field("Sent!", "", False)
							await stext(msg, embed)
						return
				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("Guild not found. ", "", False)
				await stext(msg, embed)
				return
			elif args.guild and args.channel and not args.dm:
				for guild in client.guilds:
					if guild.name == args.guild:
						for i in range(len(guild.text_channels)):
							if guild.text_channels[i].name == args.channel:
								embed = discord.Embed(title=args.title, author="", color=args.color)
								embed.set_author(name=args.aname, url=args.aurl, icon_url=args.aicourl)
								embed.set_thumbnail(url=args.thumbnail)
								embed.set_image(url=args.picture)
								embed.set_footer(text=args.footer)
								if args.field != "":
									for i in args.field:
										if i[3] not in ["1", "0"]:
											raise SystemExit
										embed.add_field(name=i[0], value=i[1], inline=i[3])
								await guild.text_channels[i].send(args.message, embed=embed)
								if not args.silent:
									embed = EmbedSystem.SimpleEmbed(e_sudo)
									embed.add_field("Sent!", "", False)
									await stext(msg, embed)
								return

				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("Guild / Channel not found. ", "", False)
				await stext(msg, embed)
				return
			elif args.dm and (args.guild or args.channel):
				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("The --dm flag must be on its own! ", "", False)
				await stext(msg, embed)
			else:
				try:
					user = client.get_user(args.dm)
				except:
					embed = EmbedSystem.SimpleEmbed(e_sudo)
					embed.add_field("User not found. ", args.message, False)
					await stext(msg, embed)
					return
				embed = discord.Embed(title=args.title, author="", color=args.color)
				embed.set_author(name=args.aname, url=args.aurl, icon_url=args.aicourl)
				embed.set_thumbnail(url=args.thumbnail)
				embed.set_image(url=args.picture)
				embed.set_footer(text=args.footer)
				if args.field != "":
					for i in args.field:
						if i[3] not in ["1", "0"]:
							raise SystemExit
						embed.add_field(name=i[0], value=i[1], inline=i[3])
				await user.send(args.message, embed=embed)
				if not args.silent:
					embed = EmbedSystem.SimpleEmbed(e_sudo)
					embed.add_field("Sent!", "", False)
					await stext(msg, embed)
				return

		except SystemExit:
			embed = EmbedSystem.SimpleEmbed(e_sudo)
			embed.add_field(parser.format_usage(), '\n'.join(parser.format_help().split("\n")[1:]), False)
			await stext(msg, embed)
	if msg.message.content.split(" ")[1] == "rm":
		parser = argparse.ArgumentParser(description="Removes messages")
		parser.add_argument("messageid", type=int, help="Specifies the message id")
		parser.add_argument("channelid", type=int, help="Specifies the channel id")
		parser.add_argument("-s", "--silent", help="Silences message on response. ", action="store_true")

		try:
			string = ' '.join(msg.message.content.split(" ")[2:])
			args = parser.parse_args(shlex.split(string))
			try:
				await client.http.delete_message(channel_id=args.channelid, message_id=args.messageid)
				if not args.silent:
					embed = EmbedSystem.SimpleEmbed(e_sudo)
					embed.add_field("Message deleted!", "[" + str(args.channelid) + ", " + str(args.messageid) + "]", False)
					await stext(msg, embed)
				return
			except:
				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("Message / Channel not found. ", "", False)
				await stext(msg, embed)
				return
		except SystemExit:
			embed = EmbedSystem.SimpleEmbed(e_sudo)
			embed.add_field(parser.format_usage(), '\n'.join(parser.format_help().split("\n")[1:]), False)
			await stext(msg, embed)
			return

	if msg.message.content.split(" ")[1] == "edit":
		parser = argparse.ArgumentParser(description="Edits messages")
		parser.add_argument("messageid", type=int, help="Specifies the message id")
		parser.add_argument("channelid", type=int, help="Specifies the channel id")
		parser.add_argument("message", type=str, help="Specifies the message")
		parser.add_argument("-s", "--silent", help="Silences message on response. ", action="store_true")

		try:
			string = ' '.join(msg.message.content.split(" ")[2:])
			args = parser.parse_args(shlex.split(string))
			try:
				await client.http.edit_message(channel_id=args.channelid, message_id=args.messageid, content=args.message)
				if not args.silent:
					embed = EmbedSystem.SimpleEmbed(e_sudo)
					embed.add_field("Message edited!", "[" + str(args.channelid) + ", " + str(args.messageid) + "]", False)
					await stext(msg, embed)
				return
			except:
				embed = EmbedSystem.SimpleEmbed(e_sudo)
				embed.add_field("Message / Channel not found. ", "", False)
				await stext(msg, embed)
				return
		except SystemExit:
			embed = EmbedSystem.SimpleEmbed(e_sudo)
			embed.add_field(parser.format_usage(), '\n'.join(parser.format_help().split("\n")[1:]), False)
			await stext(msg, embed)
			return








@client.command(name="ping")
async def ping(msg):
	embed = EmbedSystem.SimpleEmbed(e_ping)
	embed.add_field("Latency", str(round(client.latency * 1000)) + " ms", False)
	await stext(msg, embed)


@client.command(name="bw")
async def bw(msg):
	# Check if there are the right number of inputs
	if len(msg.message.content.split(" ")) != 3:
		embed = EmbedSystem.SimpleEmbed(e_bws)
		embed.add_field("Please input the right arguments! ",
						"Usage: `" + await prefix_writing(
							msg) + "bw playername gamemode`. Gamemodes - level, overall, solo (1), doubles (2), 3v3v3v3 (3), 4v4v4v4 (4).",
						False)
		embed.add_field("Advanced gamemodes: ", ", ".join(
			["eight_one", "eight_two", "four_three", "four_four", "two_four", "four_four_ultimate",
			 "eight_two_voidless", "four_four_armed", "four_four_rush", "eight_two_rush", "tourney_bedwars4s_1",
			 "castle", "eight_two_lucky", "four_four_lucky", "eight_two_ultimate", "four_four_voidless",
			 "eight_two_armed"]), False)
		embed.add_field("", "", False)
		await stext(msg, embed)
		return

	# Inputs
	inputs = msg.message.content.split(" ")
	playername = inputs[1]
	gamemode = inputs[2]
	gamemode = gamemode.replace("-", " ")

	async with aiohttp.ClientSession() as s:
		async with s.get('https://api.mojang.com/users/profiles/minecraft/' + playername) as r:

			if r.status == 200:
				html = await r.json()
				UUID = html["id"]
			else:
				embed = EmbedSystem.SimpleEmbed(e_err)
				embed.add_field("No minecraft account found. ", "", False)
				await stext(msg, embed)
				return

	# Getting the Stats of the player
	async with aiohttp.ClientSession() as s:
		async with s.get(
				"https://api.hypixel.net/player?key=" + os.getenv("HYPIXELAPITOKEN") + "&name=" + playername) as r:
			if r.status == 200:
				html = await r.json()
				try:
					if gamemode not in ["level", "overall", "solo", "doubles", "3v3v3v3", "4v4v4v4", "1", "2", "3",
										"4", "eight_one", "eight_two", "four_three", "four_four", "two_four",
										"four_four_ultimate",
										"eight_two_voidless", "four_four_armed", "four_four_rush", "eight_two_rush",
										"tourney_bedwars4s_1",
										"castle", "eight_two_lucky", "four_four_lucky", "eight_two_ultimate",
										"four_four_voidless",
										"eight_two_armed"]:
						embed = EmbedSystem.SimpleEmbed(e_bws)
						embed.add_field("That is not a valid gamemode. ", "", False)
						await stext(msg, embed)
						return
					else:
						if gamemode == "1" or gamemode == "solo":
							gamemode = "eight_one_"
						if gamemode == "2" or gamemode == "doubles":
							gamemode = "eight_two_"
						if gamemode == "3" or gamemode == "3v3v3v3":
							gamemode = "four_three_"
						if gamemode == "4" or gamemode == "4v4v4v4":
							gamemode = "four_four_"
						if gamemode == "4v4":
							gamemode = "two_four_"
						if gamemode in ["eight_one", "eight_two", "four_three", "four_four", "two_four",
										"four_four_ultimate",
										"eight_two_voidless", "four_four_armed", "four_four_rush", "eight_two_rush",
										"tourney_bedwars4s_1",
										"castle", "eight_two_lucky", "four_four_lucky", "eight_two_ultimate",
										"four_four_voidless",
										"eight_two_armed"]:
							gamemode = gamemode + "_"
						if gamemode == "level":
							embed = EmbedSystem.SimpleEmbed(e_bws)
							embed.add_field("Level: ",
											str(html["player"]["achievements"]["bedwars_level"]),
											False)
							embed.set_thumbnail("https://crafatar.com/renders/body/" + UUID + "?overlay=true")
							await stext(msg, embed)
						else:
							if gamemode == "overall":
								gamemode = ""
							embed = EmbedSystem.SimpleEmbed(e_bws)
							embed.set_thumbnail("https://crafatar.com/renders/body/" + UUID + "?overlay=true")
							embed.add_field(playername + "'s Stats", "Overall", False)
							embed.add_field("Normal Kills",
											str(html["player"]["stats"]["Bedwars"][gamemode + "kills_bedwars"]), True)
							embed.add_field("Normal Deaths",
											str(html["player"]["stats"]["Bedwars"][gamemode + "deaths_bedwars"]), True)
							embed.add_field("Normal KDR",
											str(round(html["player"]["stats"]["Bedwars"][gamemode + "kills_bedwars"] /
													  html["player"]["stats"]["Bedwars"][gamemode + "deaths_bedwars"],
													  3)), False)
							embed.add_field("Final Kills",
											str(html["player"]["stats"]["Bedwars"][gamemode + "final_kills_bedwars"]),
											True)
							embed.add_field("Final Deaths",
											str(html["player"]["stats"]["Bedwars"][gamemode + "final_deaths_bedwars"]),
											True)
							embed.add_field("Final KDR",
											str(round(
												html["player"]["stats"]["Bedwars"][gamemode + "final_kills_bedwars"] /
												html["player"]["stats"]["Bedwars"][gamemode + "final_deaths_bedwars"],
												3)), False)
							embed.add_field("Wins", str(html["player"]["stats"]["Bedwars"][gamemode + "wins_bedwars"]),
											True)
							embed.add_field("Losses",
											str(html["player"]["stats"]["Bedwars"][gamemode + "losses_bedwars"]),
											True)
							embed.add_field("WLR", str(round(
								html["player"]["stats"]["Bedwars"][gamemode + "wins_bedwars"] /
								html["player"]["stats"]["Bedwars"][gamemode + "losses_bedwars"], 3)), True)
							embed.add_field("Beds Broken",
											str(html["player"]["stats"]["Bedwars"][gamemode + "beds_broken_bedwars"]),
											True)
							embed.add_field("Winstreak",
											str(html["player"]["stats"]["Bedwars"][gamemode + "winstreak"]), True)
							await stext(msg, embed)
				except KeyError:
					embed = EmbedSystem.SimpleEmbed(e_bws)
					embed.add_field("No minecraft account found. ", "", False)
					await stext(msg, embed)
					return
			else:
				embed = EmbedSystem.SimpleEmbed(e_err)
				embed.add_field("Connection error: ERROR " + str(r.status), "", False)
				await stext(msg, embed)
				return


@client.command(name="info")
async def info(msg):
	embed = EmbedSystem.SimpleEmbed(e_info)
	embed.set_thumbnail("https://crafatar.com/avatars/dc1a1d7f-66f1-46f5-92de-161f5dd051c9")
	embed.add_field(
		"This bot was built by EvilMuffinHa#5417. It gets bedwars stats using the hypixel and mojang APIs. ",
		"Invite it using this [link.](https://discord.com/api/oauth2/authorize?client_id=694645515983519794&permissions=515136&scope=bot) " +
		"Check out the source code at this [link.](https://github.com/EvilMuffinHa/hypixel-online)",
		False)
	await stext(msg, embed)


@client.command(name="help")
async def help(msg):
	if len(msg.message.content.split(" ")) == 1:
		embed = EmbedSystem.SimpleEmbed(e_help)
		embed.add_field("", "", False)
		embed.add_field("Commands", "`" + await prefix_writing(msg) + "help commands`", True)
		embed.add_field("Moderator Settings", "`" + await prefix_writing(msg) + "help mod`", True)
		embed.add_field("Info", "`" + await prefix_writing(msg) + "info`", True)
		embed.set_thumbnail(
			"https://cdn.discordapp.com/avatars/694645515983519794/9d425f6f93006a03dfa32b060a8449ee.png?size=128")
		await stext(msg, embed)
	elif len(msg.message.content.split(" ")) == 2:
		if msg.message.content.split(" ")[1] == "commands":
			embed = EmbedSystem.SimpleEmbed(e_help)
			embed.add_field("`" + await prefix_writing(msg) + "bw [playername] [gamemode]`",
							'Gives bedwars stats on a player. Usage: .bw playername gamemode. Gamemodes - level, overall, solo, doubles, 3v3v3v3, 4v4v4v4.',
							False)
			embed.add_field("`" + await prefix_writing(msg) + "info`", "Info about the bot. ", False)
			embed.add_field("`" + await prefix_writing(msg) + "ping`", "Pong! ", False)
			embed.add_field("`" + await prefix_writing(msg) + "link [IGN]`",
							"Links your discord account with your minecraft account. ", False)
			embed.add_field("`" + await prefix_writing(msg) + "unlink`",
							"Unlinks your account with a minecraft account. ", False)
			embed.add_field("`" + await prefix_writing(msg) + "online [IGN]`",
							"Checks if a player is on hypixel or not. ", False)
			await stext(msg, embed)
		if msg.message.content.split(" ")[1] == "mod":
			embed = EmbedSystem.SimpleEmbed(e_help)
			embed.add_field("`" + await prefix_writing(msg) + "mod prefix [prefix]`",
							'Changes the prefix on the discord server.', False)
			await stext(msg, embed)
	else:
		embed = EmbedSystem.SimpleEmbed(e_help)
		embed.add_field("", "", False)
		embed.add_field("Commands", "`" + await prefix_writing(msg) + "help commands`", True)
		embed.add_field("Moderator Settings", "`" + await prefix_writing(msg) + "help mod`", True)
		embed.add_field("Info", "`" + await prefix_writing(msg) + "info`", True)
		embed.set_thumbnail(
			"https://cdn.discordapp.com/avatars/694645515983519794/9d425f6f93006a03dfa32b060a8449ee.png?size=128")
		await stext(msg, embed)

@client.command(name="online")
async def online(msg):
	if len(msg.message.content.split(" ")) != 2:
		embed = EmbedSystem.SimpleEmbed(e_online)
		embed.add_field("Please enter the right arguments! ", "Usage: `.online IGN`", False)
		embed.add_field("", "", False)
		await stext(msg, embed)
		return
	playername = msg.message.content.split(" ")[1]
	async with aiohttp.ClientSession() as s:
		async with s.get('https://sk1er.club/online-status/' + playername) as r:
			if r.status == 200:
				html = await r.text()
				try:
					status = html.split("<h2>")[2].split("</h2>")[0].split(">")[1].split("<")[0]
					last_updated = html.split("<h2>")[2].split("</strong>")[1].split(" seconds ago!")[0]
					embed = EmbedSystem.SimpleEmbed(e_online)
					embed.add_field(playername + " is " + status.lower() + ". ", "", False)
					await stext(msg, embed)
				except IndexError:
					if "Online status not available for staff members." in html:
						embed = EmbedSystem.SimpleEmbed(e_online)
						embed.add_field(playername + " is a youtuber! Youtuber online status is not available! ", "",
										False)
						await stext(msg, embed)
					else:
						embed = EmbedSystem.SimpleEmbed(e_online)
						embed.add_field(playername + " is not found. ", "", False)
						await stext(msg, embed)
			else:
				embed = EmbedSystem.SimpleEmbed(e_err)
				embed.add_field("Connection error: ERROR " + str(r.status), "", False)
				await stext(msg, embed)

async def stext(msg, embedsys):
	await msg.send(embed=embedsys.getEmbed())
	gn = msg.message.guild.name
	if not (msg.message.guild.name):
		gn = " the DM "
	print(
		msg.message.author.name + ' sent "' + msg.message.content + '" to ' + gn + ' and recieved "' + embedsys.toString() + '"')


# Starting up the bot
@client.event
async def on_ready():
	# check_if_prestiged_bw.start()

	await client.change_presence(activity=discord.Game(name="The Hypixel Bedwar"))
	for guild in client.guilds:
		print(
			client.user.name + ' is connected to the following guild:\n'
			+ guild.name + '(id: ' + str(guild.id) + ')'
		)


@client.event
async def on_command_error(msg, error):
	if isinstance(error, discord.ext.commands.errors.CommandNotFound):
		embed = EmbedSystem.SimpleEmbed(e_ukc)
		embed.add_field("", "Do `" + await prefix_writing(msg) + "help` for more.", False)
		await stext(msg, embed)


client.run(os.getenv('HYPIXELONLINETOKEN'))
