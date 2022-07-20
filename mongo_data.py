import os
import sys
import datetime
import humanize
import pymongo
import pandas as pd


def load_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
    return [x.strip() for x in lines]


def load_lost_machines():
    lost_machines = []
    lost_machines_file = "lost_machines.txt"
    lost_machines = load_file(lost_machines_file)
    return lost_machines


def load_safe_machines():
    safe_machines = []
    safe_machines_file = "safe_machines.txt"
    safe_machines = load_file(safe_machines_file)
    return safe_machines


def connect_mongodb():
    mongo_uri = os.environ.get("MONGO", None)
    if not mongo_uri:
        print("Missing MONGO environment variable")
        sys.exit(1)
    print("Connecting to mongodb...", end="")
    client = pymongo.MongoClient(mongo_uri)
    print("done")
    return client


def get_mongo_data():
    client = connect_mongodb()
    db = client.Abel
    data = db.mining.find()
    return data


def data_to_walletworkers(data):
    wallets = []
    workers = []
    found_machines = []
    unsafe_machines = []
    lost_machines = load_lost_machines()
    safe_machines = load_safe_machines()
    for item in data:
        machine = item["_id"]
        current_time = datetime.datetime.utcnow()
        last_update = item.get("update_time", None)
        timedelta = (
            humanize.naturaldelta(current_time - last_update) if last_update else ""
        )
        # block_height = str(item.get("block_height", " "))
        version = item.get("version", " ")
        is_worker = item.get("cluster", None)
        entry = {
            "Machine": machine,
            "Balance": item["total_balance"],
            "Programmatic": item.get("programmatic"),
            "Since last update": str(timedelta),
            "Version": version,
        }
        if is_worker or is_worker == None:
            workers.append(entry)
        else:
            if machine in safe_machines:
                wallets.append(entry)
            else:
                unsafe_machines.append(entry)
        if machine in lost_machines and item["programmatic"]:
            found_machines.append(machine)

    return wallets


def total_machines(*args):
    total = 0
    for arg in args:
        total += len(arg)
    return total
    # total_machines = df_wallets["Machine"].count() + df_workers["Machine"].count()


def get_df_wallet_workers():
    data = get_mongo_data()
    wallets = data_to_walletworkers(data)
    df_wallets = pd.DataFrame(wallets)
    return df_wallets


def get_wallets_total():
    df_wallets, _ = get_df_wallet_workers()
    return df_wallets["Balance"].sum()


def get_wallets_nr():
    df_wallets, _ = get_df_wallet_workers()
    return total_machines(df_wallets)


# def get_total_machines():
#     df_wallets = get_df_wallet_workers()
#     return total_machines(df_wallets, df_workers)
