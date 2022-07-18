import os
import sys
import datetime
import humanize
import pymongo
import pandas as pd


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
    for item in data:
        current_time = datetime.datetime.utcnow()
        last_update = item.get("update_time", None)
        timedelta = (
            humanize.naturaldelta(current_time - last_update) if last_update else ""
        )
        is_worker = item.get("cluster", None)
        if is_worker or is_worker == None:
            workers.append(
                {
                    "Machine": item["_id"],
                    "Since last update": str(timedelta),
                }
            )
        else:
            wallets.append(
                {
                    "Machine": item["_id"],
                    "Balance": item["total_balance"],
                    "Programmatic": item["programmatic"],
                    "Since last update": str(timedelta),
                }
            )
    return wallets, workers


def total_machines(*args):
    total = 0
    for arg in args:
        total += len(arg)
    return total
    # total_machines = df_wallets["Machine"].count() + df_workers["Machine"].count()


def get_df_wallet_workers():
    data = get_mongo_data()
    wallets, workers = data_to_walletworkers(data)
    df_wallets = pd.DataFrame(wallets)
    df_workers = pd.DataFrame(workers)
    return df_wallets, df_workers


def get_wallets_total():
    df_wallets, _ = get_df_wallet_workers()
    return df_wallets["Balance"].sum()


def get_wallets_nr():
    df_wallets, _ = get_df_wallet_workers()
    return total_machines(df_wallets)


def get_workers_nr():
    _, df_workers = get_df_wallet_workers()
    return total_machines(df_workers)


def get_total_machines():
    df_wallets, df_workers = get_df_wallet_workers()
    return total_machines(df_wallets, df_workers)
