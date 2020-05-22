from pymongo import MongoClient
import xml.etree.ElementTree as ET
import json

context = ET.iterparse('montenegro-latest.osm', events=("start", "end"))

nodes = []
ways = []
relations = []
node = None
way = -1
relation = -1


for event, elem in context:
    if event == "start":
        if relation >= 0:
            if elem.tag == "tag":
                relations[relation]['tags'][elem.attrib['k']
                                            ] = elem.attrib['v']
            elif elem.tag == "member":
                attrs = elem.attrib
                relations[relation]['members'].append({
                    "type": attrs['type'],
                    "role": attrs['role'],
                    'ref': attrs['ref']
                })
            elif elem.tag == "relation":
                attrs = elem.attrib
                relation = len(relations)
                relations.append({
                    "id": attrs["id"],
                    "members": [],
                    "tags": {}
                })
        elif way >= 0:
            if elem.tag == "nd":
                ways[way]['refs'].append(elem.attrib['ref'])
            elif elem.tag == "tag":
                ways[way]['tags'][elem.attrib['k']] = elem.attrib['v']
            elif elem.tag == "way":
                way = len(ways)
                ways.append({
                    "id": elem.attrib['id'],
                    "tags": {},
                    "refs": []
                })
            elif elem.tag == "relation":
                relation = len(relations)
                attrs = elem.attrib
                relations.append({
                    "id": attrs["id"],
                    "members": [],
                    "tags": {}
                })
        else:
            if elem.tag == "tag":
                key = elem.attrib['k']
                if '.' in key:
                    key = key.replace('.', ',')
                nodes[node]['tags'][key] = elem.attrib['v']
            elif elem.tag == "node":
                attrs = elem.attrib
                node = len(nodes)
                nodes.append({
                    "id": attrs["id"],
                    "lat": attrs['lat'],
                    "lon": attrs['lon'],
                    "tags": {}
                })
            elif elem.tag == "way":
                way = len(ways)
                ways.append({
                    "id": elem.attrib['id'],
                    "tags": {},
                    "refs": []
                })
    if event == "end" and elem.tag in ['node', 'way', 'relation']:
        elem.clear()

client = MongoClient(port=27017)
db = client.osm

db.nodes.insert_many(nodes)
db.ways.insert_many(ways)
db.relations.insert_many(relations)

# with open('data/relations.json', 'w') as file:
#     json.dump(relations, file, indent=4, ensure_ascii=False)

# with open('data/ways.json', 'w') as file:
#     json.dump(ways, file, indent=4, ensure_ascii=False)

# with open('data/nodes.json', 'w') as file:
#     json.dump(nodes, file, indent=4, ensure_ascii=False)
