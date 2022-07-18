from pydoc import render_doc
from flask import Flask, render_template
import mongo_data


app = Flask(__name__)


@app.route("/")
def index():
    total = mongo_data.get_wallets_total()
    return render_template("index.html", total=f"{total:,}")


if __name__ == "__main__":
    app.run(app.run(threaded=True, port=5000))
    # app.run(host="127.0.0.1", port=8080, debug=True)
