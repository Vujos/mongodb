from transliterate import translit
from pymongo import MongoClient
import json


def getAllBy(document, search, searchVal):
    return document.find({search: searchVal})


def findStreetsInCity(document, city):
    city = getAllBy(document, 'tags.addr:city', city)
    streets = set()
    for item in city:
        street = item['tags'].get('addr:street')
        if street:
            street = translit(street, 'sr', reversed=True)
            streets.add(street)
    return streets


client = MongoClient(port=27017)
db = client.osm

streets = findStreetsInCity(db.nodes, 'Bar')
with open('streets.json', 'w') as file:
    json.dump(list(streets), file, indent=4, ensure_ascii=False)
