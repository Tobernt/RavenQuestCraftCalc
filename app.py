from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
DATA_PATH = os.path.join("data", "market_data.json")

def load_market_data():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

@app.route("/")
def index():
    market_data = load_market_data()
    item_names = sorted(market_data.keys())
    return render_template("index.html", items=item_names, market_data=market_data)

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    recipe = data.get("recipe", {})
    market_data = load_market_data()
    total_sell_cost = 0
    total_buy_cost = 0

    for item, amount in recipe.items():
        prices = market_data.get(item, {})
        sell_price = prices.get("sell", 0) or 0
        buy_price = prices.get("buy", 0) or 0
        total_sell_cost += sell_price * amount
        total_buy_cost += buy_price * amount

    return jsonify({
        "sell_cost": total_sell_cost,
        "buy_cost": total_buy_cost
    })

@app.route("/statistics")
def statistics():
    market_data = load_market_data()
    loss_items = []

    for item, prices in market_data.items():
        buy = prices.get("buy")
        sell = prices.get("sell")
        if isinstance(buy, int) and isinstance(sell, int):
            margin = sell - buy
            if margin < 0:
                loss_items.append({
                    "item": item,
                    "buy": buy,
                    "sell": sell,
                    "loss": margin
                })

    loss_items.sort(key=lambda x: x["loss"])  # Most negative margin first
    return render_template("statistics.html", items=loss_items)

# This is the key part for hosting!
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render will set $PORT
    app.run(host="0.0.0.0", port=port)
