import requests
from lxml import html
import pickle
import re
from datetime import date
import csv

class FlowEntry:
    def __init__(self):
        self.name = None
        self.flow = 0.0
        self.min = 0.0
        self.max = 0.0
        self.highwater = 0.0
        self.flood = 0.0
        self.highp = 0.0
        self.floodp = 0.0

    def __repr__(self):
        hiprep = "to" if self.highp < 100.0 else "above"
        floodprep = "to " if self.floodp < 100.0 else ""
        return f'{self.name:<45} Flow {self.flow} ({self.min} / {self.max}), ({self.highp:.1f}% {hiprep} high, {self.floodp:.1f}% {floodprep}flooding)'

class FlowSensor:
    def __init__(self):
        self.name = None
        self.site_id = None
        self.site = None
        self.device_id = None
        self.device = None
        self.uri = None

    def __repr__(self):
        print(f'Sensor: {self.name}')
        print(f'  Site ID   = {self.site_id}')
        print(f'  Site      = {self.site}')
        print(f'  Device ID = {self.device_id}')
        print(f'  Device    = {self.device}')
        print(f'  URI       = {self.uri}')
        print('')
        return ""

def GenerateSensor(name, uri):
    #print(F'GenerateSensor: {name}, {uri}')
    fs = FlowSensor()
    fs.name = name
    fs.uri = uri
    tokens = uri.split('/?')[1].split('&')
    fs.site_id = tokens[0].split('=')[1]
    fs.site = tokens[1].split('=')[1]
    fs.device_id = tokens[2].split('=')[1]
    fs.device = tokens[3].split('=')[1]
    return fs

def GenerateFlowEntry(FS):
    fe = FlowEntry()
    fe.name = FS.name
    r = requests.get(FS.uri)
    if r:
        doc = html.fromstring(r.text)
        if doc is not None or len(doc) > 0:
            h4s = doc.xpath('//h4[@class="mb-0"]')
            if h4s:
                fe.flow = ExtractFloat(h4s[0].text)
                fe.max  = ExtractFloat(h4s[1].text)
                fe.min  = ExtractFloat(h4s[2].text)
            spans = doc.xpath('//span[@class="badge badge-inline"]')
            if spans is not None:
                if len(spans) > 1:
                    fe.flood = ExtractFloat(spans[0].text)
                    fe.highwater = ExtractFloat(spans[1].text)
                    if fe.highwater != 0.0:
                        fe.highp = (fe.flow / fe.highwater) * 100
                    if fe.flood != 0.0:
                        fe.floodp = (fe.flow / fe.flood) * 100
            return fe
    return None

def ExtractFloat(s):
    if s == 0.0:
        return 0.0
    number = re.findall("\d+\.\d+", s)
    if number is None or len(number) < 1:
        return 0.0
    return float(number[0])

def FloodReport(FlowTable):
    print ()
    print (f"Flood Report for {date.today().strftime('%B %d, %Y')}")
    print()

    Flooded = []
    High = []
    for f in FlowTable:
        if f.floodp > 100.0:
            Flooded.append(f)
        if f.highp > 100.0:
            High.append(f)
    Flooded = sorted(Flooded, key=lambda x: x.floodp, reverse=True)
    High = sorted(High, key=lambda x: x.floodp, reverse=True)

    FloodCount = len(Flooded)
    HighCount = len(High)
    print(f"  There are {FloodCount} flooded streams and {HighCount} streams above the high water mark today")
    print()

    if FloodCount > 0:
        print("  Flooded Streams")
        print("  ---------------")
        for f in Flooded:
            print(f"  {f}")
        print()

    if HighCount > 0:
        print("  Streams at or above the high water mark")
        print("  ---------------------------------------")
        for f in High:
            print(f"  {f}")
        print()

    ft = new_list = sorted(FlowTable, key=lambda x: x.floodp, reverse=True)
    print("  All Streams")
    print("  -----------")
    for f in ft:
        print(f"  {f}")
    print()

def RecordSensorReadings(FlowEntries):
    Filename = f"Reports/Sensors {date.today()}.csv"
    with open(Filename, 'w', newline='') as f:
        writer = csv.writer(f)
        for flow in FlowEntries:
            writer.writerow([str(date.today()), flow.name, flow.flow, flow.min, flow.max, flow.highwater, flow.flood, flow.highp, flow.floodp])

Sensors = [
    GenerateSensor('Mill Creek @ Canyon Mouth', 'https://rain-flow.slco.org/sensor/?site_id=76&site=3ea01878-b85b-497b-8db5-03654e886f0a&device_id=2&device=a070b1c1-1dd2-47af-b810-f5d5b0d6ba7f'),
    GenerateSensor('Mill Creek @ 460 West', 'https://rain-flow.slco.org/sensor/?site_id=82&site=07368bfd-e9e1-4d61-865b-11ac14719ba7&device_id=2&device=0c8aad55-53e1-41d8-bff2-97f37e281ebc'),
    GenerateSensor('Red Butte Creek @ Fort Douglas','https://rain-flow.slco.org/sensor/?site_id=106&site=78136973-f7c1-4659-909c-1f3a22cfcfcc&device_id=1&device=c4d6caba-0e0a-4ffc-b57b-a2c06a803182'),
    GenerateSensor('Red Butte Creek @ Miller Park', 'https://rain-flow.slco.org/sensor/?site_id=88&site=0f63146a-3f02-411a-b20e-f2aabfcffbf9&device_id=4&device=ecd6c378-486d-4a87-ac25-9ecc1de14541'),
    GenerateSensor('Big Cottonwood Creek @ 300 West', 'https://rain-flow.slco.org/sensor/?site_id=81&site=a81f0cf5-e702-4dab-a238-622d557f9465&device_id=2&device=154b557c-4ff7-4c57-b550-db185d9b3899'),
    GenerateSensor('Big Cottonwood Creek @ Canyon Mouth','https://rain-flow.slco.org/sensor/?site_id=67&site=7b550c74-37e9-4af7-8d6a-3b6afe73013c&device_id=2&device=a18d9df7-3902-40e4-b509-a5be73a0540f'),
    GenerateSensor('Big Cottonwood Creek @ Cottonwood Lane', 'https://rain-flow.slco.org/sensor/?site_id=73&site=58359497-613a-46e0-a3a4-8d13fa1da5d7&device_id=2&device=06060a22-2457-41b6-a482-c234c0d5a723'),
    GenerateSensor('Big Cottonwood Creek @ Creekside Park', 'https://rain-flow.slco.org/sensor/?site_id=79&site=cfa2f1cc-84be-4b70-b396-8bdc03969eb4&device_id=2&device=d104b73e-ddce-440e-92aa-e4ed4fb2ca30'),
    GenerateSensor('Little Cottonwood Creek @ 300 West', 'https://rain-flow.slco.org/sensor/?site_id=80&site=f4ca7320-4f72-4552-b822-cb53e0fde0eb&device_id=2&device=03cfc591-bccc-4253-8125-c666cc81ba01'),
    GenerateSensor('Little Cottonwood Creek @ Crestwood Park', 'https://rain-flow.slco.org/sensor/?site_id=68&site=13f042c2-8e64-4209-85b2-f9c2fb431045&device_id=2&device=9c18f370-4af5-49eb-b893-aafdad0572d4'),
    GenerateSensor('Little Cottonwood Creek @ Tanners Flat', 'https://rain-flow.slco.org/sensor/?site_id=111&site=356eff27-b9e1-4585-bb4f-cd946469a294&device_id=3&device=4ee002b8-afa2-4d83-ad9e-9ffee95ca81d'),
    GenerateSensor('Parleys Creek @ Canyon Mouth', 'https://rain-flow.slco.org/sensor/?site_id=77&site=c220db0d-a67d-4f0a-a04c-211d1ad0b7a3&device_id=2&device=9d7b0e6d-a81e-4800-a4a6-e972f6c1bf22'),
    GenerateSensor('Parleys Creek @ Hidden Hollow', 'https://rain-flow.slco.org/sensor/?site_id=114&site=6d720eee-8279-4e06-9841-a65b172f5e9f&device_id=2&device=5aa3e814-a23a-4553-9da0-5269295de45a'),
    GenerateSensor('Bingham Creek @ Jordan River', 'https://rain-flow.slco.org/sensor/?site_id=71&site=eaf7aa1d-41c6-46e8-9fcb-042180ca4285&device_id=2&device=eecb3725-bd20-4b0b-8dac-0b728381749d'),
    GenerateSensor('City Creek @ Memory Grove', 'https://rain-flow.slco.org/sensor/?site_id=91&site=2032a5a2-d405-4a30-a316-43d67817d0f6&device_id=2&device=093badfa-eba1-4997-a4a8-a12062b3fb8e'),
    GenerateSensor('Emigration Creek @ Canyon Mouth', 'https://rain-flow.slco.org/sensor/?site_id=86&site=0cad105f-39a4-42ba-ab1e-f43334c20428&device_id=2&device=1e4e2a0f-a6bc-4f9e-98d3-fe3afc3df01b'),
    GenerateSensor('Emigration Creek @ Westminster', 'https://rain-flow.slco.org/sensor/?site_id=112&site=893e2c83-b714-43b1-a371-34f43f1639dc&device_id=3&device=3efc26fc-38ee-486c-8506-7ed4c7117da4'),
    GenerateSensor('Midas Creek @ Jordan River ', 'https://rain-flow.slco.org/sensor/?site_id=62&site=6d346231-a49e-4fab-a923-e53bb15a2d5f&device_id=2&device=c468ac53-9995-4c1c-9964-2b152fcd1d51'),
    GenerateSensor('Jordan River Surplus Canal', 'https://rain-flow.slco.org/sensor/?site_id=104&site=95e8754c-f507-449a-80be-f9445f920c83&device_id=1&device=3d7ac51a-ea2d-436b-8582-9c2d63568ef9'),
    GenerateSensor('Jordan River @ 9000 South', 'https://rain-flow.slco.org/sensor/?site_id=92&site=a3b813d4-939e-4d08-bab3-3159107c833a&device_id=2&device=cacc90fd-9e26-418e-a401-0e746a2bb3a4'),
    GenerateSensor('Jordan River @ 4800 S ', 'https://rain-flow.slco.org/sensor/?site_id=113&site=5da40f55-6b89-49f3-b4ec-2e87c96105e8&device_id=3&device=0857c736-1991-45e5-9223-517ef8da1589'),
    GenerateSensor('Jordan River @ 1700 South', 'https://rain-flow.slco.org/sensor/?site_id=105&site=21afb147-64bc-4661-8f7a-fbe6fb964932&device_id=1&device=72d43427-9a29-4479-93d0-d2fa15acd6dc'),
    GenerateSensor('Jordan River @ 500 North', 'https://rain-flow.slco.org/sensor/?site_id=92&site=a3b813d4-939e-4d08-bab3-3159107c833a&device_id=2&device=cacc90fd-9e26-418e-a401-0e746a2bb3a4')
]

# Load in the Flow Table from cache for testing
#
#FlowTable = pickle.load(open("FlowTable.db", "rb"))
#pickle.dump(FlowTable, open("FlowTable.db", "wb"))

FlowTable = []
for S in Sensors:
    Flow = GenerateFlowEntry(S)
    print(Flow)
    FlowTable.append(Flow)
FloodReport(FlowTable)
RecordSensorReadings(FlowTable)







