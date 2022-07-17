import pymongo

# import webbrowser
import pymongo
import os
import time
import sys
from flask import Flask


def connect_mongo() -> pymongo.MongoClient:
    mongo_line = os.environ.get("MONGO", None)
    if mongo_line:
        print("Mongo validators positive. Connecting to MongoDB")
        for attempt in range(3):
            print(f"Connecting to MongoDB. Attempt {attempt +1}")
            try:
                mongo_client = pymongo.MongoClient(mongo_line)
                print("MongoDB connected successfully")
                return mongo_client
            except Exception:
                time.sleep(2)
                print("MongoDB connect failed")

    else:
        print("No credentials for mongodb found. Exiting")
        sys.exit(1)
    print("MongoDB connect failed")


def machines_info(mdata) -> dict:
    for machine in mdata:
        data = {"cluster_count": 0, "primary_count": 0, "total_balance": 0}
        if machine["cluster"]:
            data["cluster_count"] += 1
        else:
            data["primary_count"] += 1
            data["total_balance"] += machine["total_balance"]
    return data


def main():
    client = connect_mongo()
    mdb = client.Abel
    mdata = mdb.mining.find()
    data = machines_info(mdata)

    total = data["total_balance"]
    return f"<p>Total balance:</p><p>{total}</p>"

    contents = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
    <meta content="text/html; charset=ISO-8859-1"
    http-equiv="content-type">
    <title>Python Webbrowser</title>
    </head>
    <body>
    %s
    </body>
    </html>
    """ % (
        total
    )
    return contents


app = Flask(__name__)


@app.route("/")
def hello_world():
    return main()


# filename = "webbrowser.html"


# def main(contents, filename):
#     output = open(filename, "w")
#     output.write(contents)
#     output.close()


# main(contents, filename)
# webbrowser.open(filename)
