import discord
from discord.ext import tasks
import schedule
import time
import os
import datetime
import notion
from threading import Thread
from keep_alive import keep_alive

#bot initialization
intents=discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

#checks if any of the scheduled functions is to be run
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)

#restarts the system
def restart():
    print("RESTARTING THE SYSTEM\n\n\n")
    os.system("python3 restarter.py")
    os.system('kill 1')

#sends the schedule for the specific date
async def sendSchedule(date, spec, channel):
    trains = notion.getEventsDate(date, 'trains')
    accomodations = notion.getEventsDate(date, 'accomodations')

    trainsSorted = []

    if trains == {}:
        if spec != 'date':
            await channel.send(f"You have no trains to take for {spec}!")
        else:
            await channel.send(f"You have no trains to take for the day {date.date()}!")
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
                        await channel.send(f"Remember to check out {spec} from {name}, the check-out times are: {checkOut}")
                    else:
                        await channel.send(f"Remember to check out on the day {date.date()} from {name}, the check-out times are: {checkOut}")


#sends the reminder of the activities of the next day
@tasks.loop(time=datetime.time(hour=21, minute=0, second=0, microsecond=0, tzinfo=datetime.datetime.now().astimezone().tzinfo))
async def sendReminder():
    CHAT_ID = int(os.environ['CHAT_ID'])
    channel = client.get_channel(CHAT_ID)
    tomorrow = (datetime.datetime.now() + datetime.timedelta(1))
    await sendSchedule(tomorrow, 'tomorrow', channel)
    
#bot wakeup
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    #schedules the message of the daily schedule
    sendReminder.start()

#here are all the bot's command and features
@client.event
async def on_message(message):
    if ".today" in message.content:
        await message.channel.send("Here's today's planning")
        today = datetime.datetime.now()
        await sendSchedule(today, 'today', message.channel)

    if ".date" in message.content:
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

if __name__ == "__main__":
    TOKEN = os.environ['TOKEN']
    schedule.every().day.at("02:00").do(restart)
    Thread(target=schedule_checker).start() 
    try:
        keep_alive()
        client.run(TOKEN)
    except discord.errors.HTTPException:
        print("\n\n\nBLOCKED BY RATE LIMITS\n")
        restart()