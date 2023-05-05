from flask import Flask
from rainflows import Sensors, GenerateFlowEntry, FloodReport, RecordSensorReadings

app = Flask(__name__)

@app.route("/")
def hello():
    FlowTable = []
    for S in Sensors:
        Flow = GenerateFlowEntry(S)
        print(Flow)
        FlowTable.append(Flow)
    return FloodReport(FlowTable)

if __name__ == "__main__":
    app.run()
