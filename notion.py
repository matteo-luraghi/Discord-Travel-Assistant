import requests
import datetime
import cal
import json
import os

TOKEN = os.getenv['TOKEN']
TRAINS_DATABASE = os.getenv['TRAINS_DATABASE']
ACCOMODATIONS_DATABASE = os.getenv['ACCOMODATIONS_DATABASE']

class Train:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

class Accomodation:
    def __init__(self, name, start, end, address, checkIn, checkOut):
        self.name = name
        self.start = start
        self.end = end
        self.address = address
        self.checkIn = checkIn
        self.checkOut = checkOut

#creates the headers to access the notion API
def createHeaders(token):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    return headers

#makes the notion database request
def notionRequest(token, databaseId):
    headers = createHeaders(token)
    readUrl = f"https://api.notion.com/v1/databases/{databaseId}/query"
    res = requests.request("POST", readUrl, headers=headers)
    data = res.json()
    return data

#gets the events of the specific date
def getEventsDate(date, method):
    if method == 'trains':
        DATABASE = TRAINS_DATABASE
    if method == 'accomodations':
        DATABASE = ACCOMODATIONS_DATABASE
    data = notionRequest(TOKEN, DATABASE)
    results = {}
    for el in data['results']:
        start = el['properties']['Date']['date']['start']
        end = el['properties']['Date']['date']['end']
        startDate = datetime.datetime.strptime(start.split('T')[0], '%Y-%m-%d')
        endDate = datetime.datetime.strptime(end.split('T')[0], '%Y-%m-%d')
        if date.year == startDate.year and date.month == startDate.month and date.day == startDate.day or (method=='accomodations' and date.year == endDate.year and date.month == endDate.month and date.day == endDate.day):
            try:
                address = el['properties']['Address']['rich_text'][0]['text']['content']
            except:
                address = None
            results[el['properties']['Name']['title'][0]['plain_text']] = {'name': el['properties']['Name']['title'][0]['plain_text'], 'address': address}
            if method == 'trains':
                results[el['properties']['Name']['title'][0]['plain_text']]['hour'] = start
                results[el['properties']['Name']['title'][0]['plain_text']]['url'] = el['properties']['Url']['url']
            if method == 'accomodations':
                if date.year == endDate.year and date.month == endDate.month and date.day == endDate.day:
                    try:
                        checkOut = el['properties']['Check-Out']['rich_text'][0]['plain_text']
                    except:
                        checkOut = 'Nothing'
                    results[el['properties']['Name']['title'][0]['plain_text']]['check-out'] = checkOut
                else:
                    try:
                        checkIn = el['properties']['Check-In']['rich_text'][0]['plain_text']
                    except:
                        checkIn = None
                    results[el['properties']['Name']['title'][0]['plain_text']]['check-in'] = checkIn

    return results