from bot import bot, discord, tasks, pymongo
from utils.constants import LINK, GUILD_ID, FORCED_MUTE_ROLE, MODLOG_CHANNEL_ID
import time
import traceback
from utils.data import AUTO_SLOWMODE_CHANNELS, helper_roles
from schemas.redis import Session, Question, View
from commands.practice.ui import MCQButtonsView
from commands.practice import close_session
import datetime
from utils.mongodb import smdb, gpdb


async def togglechannellock(channel_id, guild_id, unlock, *, unlocktime=0):
    everyone = bot.get_guild(guild_id).default_role
    mod_log_channel = bot.get_channel(gpdb.get_pref("modlog_channel", guild_id)) 
    timern = int(time.time()) + 1
    channel = bot.get_channel(channel_id)
    overwrite = channel.overwrites_for(everyone)
    overwrite.send_messages_in_threads = unlock
    overwrite.send_messages = unlock
    try:
        await channel.set_permissions(everyone, overwrite=overwrite)
        if unlock:
            embed = discord.Embed(
                description="Channel Unlocked", colour=discord.Colour.green()
            )
            embed.set_author(
                name="MongoDB#0082",
                icon_url="https://cdn.discordapp.com/attachments/947859228649992213/1196753678342819933/mongodb.png?ex=65b8c6b7&is=65a651b7&hm=db7fdb12435ba54299497dfb26f65dac5993caa8b48b976cf01238233c54a508&",
            )
            embed.add_field(name="Channel", value=f"<#{channel_id}>", inline=False)
            embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
            embed.add_field(
                name="ID",
                value=f"```py\nUser = {bot.user.id}\nChannel = {channel_id}```",
                inline=False,
            )
            embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
            if mod_log_channel:
                await mod_log_channel.send(embed=embed)
            await channel.send("Channel has been unlocked.")
        else:
            embed = discord.Embed(
                description="Channel Locked", colour=discord.Colour.red()
            )
            embed.set_author(
                name="MongoDB#0082",
                icon_url="https://cdn.discordapp.com/attachments/947859228649992213/1196753678342819933/mongodb.png?ex=65b8c6b7&is=65a651b7&hm=db7fdb12435ba54299497dfb26f65dac5993caa8b48b976cf01238233c54a508&",
            )
            embed.add_field(name="Channel", value=f"<#{channel_id}>", inline=False)
            embed.add_field(
                name="Unlock time", value=f"<t:{unlocktime}:R>", inline=False
            )
            embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
            embed.add_field(
                name="ID",
                value=f"```py\nUser = {bot.user.id}\nChannel = {channel_id}```",
                inline=False,
            )
            embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
            if mod_log_channel:
                await mod_log_channel.send(embed=embed)
            await channel.send("Channel has been locked.")
            time.sleep(1)
            await channel.send(f"Unlocking channel <t:{unlocktime}:R>.")

    except Exception:
        print(traceback.format_exc())
        print("failed to set permissions")


async def toggleforumlock(thread_id, guild_id, unlock, unlocktime):
    mod_log_channel = bot.get_channel(gpdb.get_pref("modlog_channel", guild_id)) 
    timern = int(time.time()) + 1
    thread = bot.get_channel(thread_id)
    try:
        thread = await thread.edit(locked=not unlock)
        if unlock:
            embed = discord.Embed(
                description="Thread Unlocked", colour=discord.Colour.green()
            )
            embed.set_author(
                name="MongoDB#0082",
                icon_url="https://cdn.discordapp.com/attachments/947859228649992213/1196753678342819933/mongodb.png?ex=65b8c6b7&is=65a651b7&hm=db7fdb12435ba54299497dfb26f65dac5993caa8b48b976cf01238233c54a508&",
            )
            embed.add_field(name="Channel", value=f"<#{thread_id}>", inline=False)
            embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
            embed.add_field(
                name="ID",
                value=f"```py\nUser = {bot.user.id}\nThread = {thread_id}```",
                inline=False,
            )
            embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
            if mod_log_channel:
                await mod_log_channel.send(embed=embed)
            await thread.send("Thread has been unlocked.")
        else:
            embed = discord.Embed(
                description="Thread Locked", colour=discord.Colour.red()
            )
            embed.set_author(
                name="MongoDB#0082",
                icon_url="https://cdn.discordapp.com/attachments/947859228649992213/1196753678342819933/mongodb.png?ex=65b8c6b7&is=65a651b7&hm=db7fdb12435ba54299497dfb26f65dac5993caa8b48b976cf01238233c54a508&",
            )
            embed.add_field(name="Thread", value=f"<#{thread_id}>", inline=False)
            embed.add_field(
                name="Unlock time", value=f"<t:{unlocktime}:R>", inline=False
            )
            embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
            embed.add_field(
                name="ID",
                value=f"```py\nUser = {bot.user.id}\nThread = {thread_id}```",
                inline=False,
            )
            embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
            if mod_log_channel:
                await mod_log_channel.send(embed=embed)
            await thread.send("Thread has been locked.")
            time.sleep(1)
            await thread.send(f"Unlocking thread <t:{unlocktime}:R>.")

    except Exception as e:
        print(traceback.format_exc())
        print(e)


@tasks.loop(hours=720)
async def autorefreshhelpers():
    changed = []
    mod_log_channel = bot.get_channel(gpdb.get_pref("modlog_channel", GUILD_ID)) 
    timenow = int(time.time()) + 1
    for chnl, role in helper_roles.items():
        try:
            helper_role = discord.utils.get(bot.get_guild(GUILD_ID).roles, id=role)
            no_of_users = len(helper_role.members)
            channel = bot.get_channel(chnl)
            new_topic = None
            for line in channel.topic.split("\n"):
                if "No. of helpers" in line:
                    new_topic = channel.topic.replace(
                        line, f"No. of helpers: {no_of_users}"
                    )
                    break
            else:
                new_topic = f"{channel.topic}\nNo. of helpers: {no_of_users}"
            if channel.topic != new_topic:
                await channel.edit(topic=new_topic)
                changed.append(channel.mention)
        except Exception:
            continue
    if changed:
        embed = discord.Embed(description="Helpers Refreshed !!", color=0x51ADBB)
        embed.set_author(name=str(bot.user), icon_url=bot.user.display_avatar.url)
        embed.add_field(name="Channels", value=", ".join(changed), inline=False)
        embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
        embed.add_field(
            name="ID",
            value=f"```py\nBot = {bot.user.id}\nChannel = 697072778553065542```",
            inline=False,
        )
        embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
        if mod_log_channel:
            await mod_log_channel.send(embed=embed)
    else:
        embed = discord.Embed(description="Helpers Refreshed !!", color=0x51ADBB)
        embed.set_author(name=str(bot.user), icon_url=bot.user.display_avatar.url)
        embed.add_field(name="Channels", value="no changes were made.", inline=False)
        embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
        embed.add_field(
            name="ID",
            value=f"```py\nBot = {bot.user.id}\nChannel = 697072778553065542```",
            inline=False,
        )
        embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
        if mod_log_channel:
            await mod_log_channel.send(embed=embed)


@tasks.loop(seconds=20)
async def checklock():
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    clocks = db["channellock"]
    flocks = db["forumlock"]
    try:
        results = clocks.find({"resolved": False})
        for result in results:
            if result["time"] <= time.time():
                ult = clocks.find_one({"_id": "u" + result["_id"][1:]})["time"]
                await togglechannellock(
                    result["channel_id"], result["guild_id"], result["unlock"], unlocktime=ult
                )

                clocks.delete_one({"_id": result["_id"]})

        results = flocks.find({"resolved": False})
        for result in results:
            if result["time"] <= time.time():
                ult = flocks.find_one({"_id": "u" + result["_id"][1:]})["time"]
                await toggleforumlock(
                    result["thread_id"], result["guild_id"], result["unlock"], unlocktime=ult
                )
                flocks.delete_one({"_id": result["_id"]})

    except Exception:
        print(traceback.format_exc())

@tasks.loop(hours=24)
async def resetdmprefs():
    timern = int(time.time()) + 1
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    dmservers = db["dm_server_prefs"]
    results = dmservers.find({"resolved": False})
    for result in results:
        if result["deleted_time"] <= timern:
            dmservers.delete_one({"_id": result["_id"]})

@tasks.loop(seconds=20)
async def checkmute():
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    mute = db["mute"]
    timern = int(time.time()) + 1
    results = mute.find({"muted": True})
    for result in results:
        try:
            if int(result["unmute_time"]) <= timern:
                user_id = int(result["user_id"])
                guild_id = int(result["guild_id"])
                mod_log_channel = bot.get_channel(gpdb.get_pref("modlog_channel", guild_id)) 
                guild = bot.get_guild(guild_id)
                # The user ID may not be present in cache.
                try:
                    user = guild.get_member(user_id)
                    if user is None:
                        mute.delete_many({"user_id": str(user_id)})
                        return
                    forced_mute_role = guild.get_role(FORCED_MUTE_ROLE)
                    if forced_mute_role not in user.roles:
                        mute.delete_many({"user_id": str(user_id)})
                        return
                    await user.remove_roles(forced_mute_role)
                    # mute.update_one({"_id": result["_id"]}, {"$set": {"muted": False}})
                    embed = discord.Embed(
                        description="Go Study Mode Deactivated",
                        colour=discord.Colour.green(),
                    )
                    embed.set_author(
                        name="MongoDB#0082",
                        icon_url="https://cdn.discordapp.com/attachments/947859228649992213/1196753678342819933/mongodb.png?ex=65b8c6b7&is=65a651b7&hm=db7fdb12435ba54299497dfb26f65dac5993caa8b48b976cf01238233c54a508&",
                    )
                    embed.add_field(name="User", value=f"{user.mention}", inline=False)
                    embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
                    embed.add_field(
                        name="ID",
                        value=f"```py\nUser = {bot.user.id}\nRole = {FORCED_MUTE_ROLE}```",
                        inline=False,
                    )
                    embed.set_footer(
                        text=f"{bot.user}", icon_url=bot.user.display_avatar.url
                    )
                    if mod_log_channel:
                        await mod_log_channel.send(embed=embed)
                    mute.delete_one({"_id": result["_id"]})
                except Exception:
                    print(traceback.format_exc())
        except Exception:
            print(traceback.format_exc())


@tasks.loop(seconds=20)
async def handle_slowmode():
    for channel_id in AUTO_SLOWMODE_CHANNELS:
        slowmode = 3
        current_time = datetime.datetime.now()
        time_15s_ago = current_time - datetime.timedelta(seconds=15)
        channel = bot.get_channel(channel_id)
        if not channel:
            continue

        if channel.last_message:
            last_msg_time = channel.last_message.created_at
            if last_msg_time.timestamp() < time_15s_ago.timestamp():
                slowmode = 0
                if channel.slowmode_delay != 0:
                    await channel.edit(slowmode_delay=slowmode)
                continue

        messages_in15s = await channel.history(after=time_15s_ago, limit=300).flatten()
        number_of_messages = len(messages_in15s)
        if number_of_messages <= 9:
            slowmode = 0
            if channel.slowmode_delay != 0:
                await channel.edit(slowmode_delay=slowmode)
            continue

        user_messages = {}

        for message in messages_in15s:
            if message.author.bot:
                continue
            if message.author.id not in user_messages:
                user_messages[message.author.id] = 1
            else:
                user_messages[message.author.id] += 1

        sorted_user_messages = dict(
            sorted(user_messages.items(), key=lambda x: x[1], reverse=True)
        )
        for user_id, message_count in sorted_user_messages.items():
            if message_count >= 12:
                message = await channel.send(
                    f"<@{user_id}> You are sending too many messages. Please slow down."
                )
                await message.delete(delay=10)

        if number_of_messages >= 60:
            # 4 messages per second, will likely never happen
            slowmode = 120
        elif number_of_messages >= 45:
            # chat is absolute chaos
            slowmode = 60
        elif number_of_messages >= 30:
            slowmode = 45
        elif number_of_messages >= 20:
            slowmode = 12
        elif number_of_messages >= 15:
            slowmode = 6

        if channel.slowmode_delay != slowmode:
            await channel.edit(slowmode_delay=slowmode)


@tasks.loop(seconds=5)
async def send_questions():
    sessions = Session.find(
        Session.paused == 0 and Session.currently_solving == "none"
    ).all()
    for session in sessions:
        thread = bot.get_channel(int(session["thread_id"]))
        if not thread:
            continue

        questions = list(
            filter(
                lambda x: x["solved"] == 0,
                Question.find(Question.session_id == session.session_id).all(),
            )
        )

        if len(questions) == 0 or not questions:
            await close_session(
                session, "No more questions left! Ending the session..."
            )
            continue

        question = questions[0]

        session["currently_solving"] = question.question_name
        session.save()

        question_number = (session["limit"] - len(questions)) + 1
        embeds = []
        for qs in question["questions"]:
            embed = discord.Embed()
            if len(embeds) == 0:
                embed.title = f"{question['question_name']}".replace(
                    f"_{session['session_id']}", ""
                )
                embed.set_footer(text=f"Question {question_number}/{session['limit']}")
            embed.set_image(
                url=f"https://pub-8153dcb2290449f2924ed014b10896ee.r2.dev/{qs}"
            )
            embeds.append(embed)

        mcq = MCQButtonsView(question["question_name"])
        mcq_msg = await thread.send(embeds=embeds, view=mcq)
        bot.add_view(mcq, message_id=mcq_msg.id)
        view = View(view_id=question["question_name"], message_id=mcq_msg.id)
        view.save()


@tasks.loop(minutes=2)
async def expire_sessions():
    sessions = Session.find(Session.expire_time <= int(time.time()) + 600).all()
    for session in sessions:
        if session.expire_time <= int(time.time()):
            await close_session(session, "Session expired...")
        else:
            thread = bot.get_channel(int(session["thread_id"]))
            if not thread:
                Session.delete(session["session_id"])
                continue
            await thread.send(
                f"This session will expire in <t:{session['expire_time']}:R>."
            )


@tasks.loop(minutes=1)
async def populate_cache():
    await smdb.populate_cache()
