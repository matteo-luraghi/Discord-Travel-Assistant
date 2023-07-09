import discord
from discord.ext import tasks
import os
import random
import datetime
import notion
from keep_alive import keep_alive

#bot initialization
intents=discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

#restarts the system
def restart():
    print("RESTARTING THE SYSTEM\n\n\n")
    os.system("python3 restarter.py")
    os.system('kill 1')

#sends the schedule for the specific date
async def sendSchedule(date, spec, channel):
    trains = notion.getEventsDate(date, 'trains')
    accomodations = notion.getEventsDate(date, 'accomodations')

    if trains == {} and accomodations == {} and spec=='tomorrow':
        return

    trainsSorted = []

    if trains == {}:
        if spec != 'date':
            await channel.send(f"You have no trains to take for {spec}!")
        else:
            await channel.send(f"You have no trains to take on the day {date.date()}!")
    else:
        hours = []
        for train in trains:
            hour = (datetime.datetime.strptime(trains[train]['hour'], '%Y-%m-%dT%H:%M:%S.%f%z')).time()
            hours.append(hour)
        hours.sort()
        for time in hours:
            for train in trains:
                if (datetime.datetime.strptime(trains[train]['hour'], '%Y-%m-%dT%H:%M:%S.%f%z')).time() == time:
                    trainsSorted.append(trains[train])

        for train in trainsSorted:
            name = train['name']
            address = train['address']
            hour = (datetime.datetime.strptime(train['hour'], '%Y-%m-%dT%H:%M:%S.%f%z')).time()
            url = train['url']
            if spec != 'date':
                await channel.send(f"{spec.capitalize()} at {hour} you'll have to go to {address} to take the train: {name}")
            else:
                await channel.send(f"On the day {date.date()} at {hour} you'll have to go to {address} to take the train: {name}")
            if url != None:
                await channel.send(f"You'll find your tickets here: {url}")

    if accomodations == {}:
        if spec != 'date':
            await channel.send(f"You have no accomodations to reach for {spec}!")
        else:
            await channel.send(f"You have no accomodations to reach on the day {date.date()}!")
    else:
        for accomodation in accomodations:
            name = accomodations[accomodation]['name']
            address = accomodations[accomodation]['address']
            if 'check-in' in accomodations[accomodation]:
                checkIn = accomodations[accomodation]['check-in']
                if spec != 'date':
                    await channel.send(f"{spec.capitalize()} you'll have to check in at {name}, the address is: {address}")
                else:
                    await channel.send(f"On the day {date.date()} you'll have to check in at {name}, the address is: {address}")
                if checkIn != None:
                    await channel.send(f"The check-in times are: {checkIn}")
            elif 'check-out' in accomodations[accomodation] and accomodations[accomodation]['check-out']!='Nothing':
                    checkOut = accomodations[accomodation]['check-out']
                    if spec != 'date':
                        await channel.send(f"Remember to check out {spec} from {name}, you can check out until: {checkOut}")
                    else:
                        await channel.send(f"Remember to check out on the day {date.date()} from {name}, you can check out until: {checkOut}")

#tells the randomly selected user to get a postcard from the selected city
async def userPostcard(member: discord.Member, city:str):
    channel = await member.create_dm()
    randPhrase = random.randint(0, 5)
    if randPhrase == 0:
        await channel.send(f"You better get a postcard from {city}, you wouldn't want to get lost in the crowd, would you?")
    elif randPhrase == 1:
        await channel.send(f"Hi there, you'll get a postcard from {city}, be senaky about it, cheerio! :  )")
    elif randPhrase == 2:
        await channel.send(f"{city}... what a beautiful city, so many doors to get lost in... get a postcard, you know, just in case...")
    elif randPhrase == 3:
        await channel.send(f"Howdy! How are we doing? It's still a long way to London I'm afraid, why don't you get a postcard from {city}? I'm sure Simon will love it!")
    elif randPhrase == 4:
        await channel.send(f"Ahahahah... so you think you can leave {city} without a postcard??? You'll better get one, just saying... :  )")
    elif randPhrase == 5:
        await channel.send(f"You know, I'm redecorating the walls of my corridors, do you think that a postcard of {city} will fit?")

#sends the reminder of the activities of the next day
@tasks.loop(time=datetime.time(
    hour=21, 
    minute=0, 
    second=0, 
    microsecond=0, 
    tzinfo=datetime.datetime.now().astimezone().tzinfo))
async def sendReminder():
    CHAT_ID = int(os.environ['CHAT_ID'])
    channel = client.get_channel(CHAT_ID)
    await channel.send("Schedule schedule working fine, delete this test")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(1))
    await sendSchedule(tomorrow, 'tomorrow', channel)

#bot wakeup
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

#here are all the bot's command and features
@client.event
async def on_message(message):
    if ".today" in message.content:
        today = datetime.datetime.now()
        await sendSchedule(today, 'today', message.channel)

    if ".sched" in message.content:
        date = message.content.split(' ')[1]
        try:
            date = datetime.datetime.strptime(date, '%Y/%m/%d')
        except:
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
            except:
                pass
        if date == message.content.split(' ')[1]:
            await message.channel.send("Error, remember to write the date as 'yyyy-mm-dd' or 'yyyy/mm/dd'")
        else:
            await sendSchedule(date, 'date', message.channel)

    if ".postcard" in message.content:
        members = client.guilds[0].members
        members_real = []
        for member in members:
            if member.bot == False:
                members_real.append(member)
        city = message.content.split(" ")[1]
        randNum = random.randint(0, len(members_real) - 1)
        await userPostcard(members_real[randNum], city)

if __name__ == "__main__":
    DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
    try:
        keep_alive()
        client.run(DISCORD_TOKEN)
    except discord.errors.HTTPException:
        print("\n\n\nBLOCKED BY RATE LIMITS\n")
        restart()