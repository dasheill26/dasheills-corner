import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.post("/")
def rewards_calc():
    """
    Input JSON:
      { "total_pence": 1234 }
    Output JSON:
      { "points_earned": 62 }
    Example policy: 5% of total (same as your app).
    """
    data = request.get_json(silent=True) or {}
    total = int(data.get("total_pence", 0) or 0)

    # Basic validation
    if total < 0:
        return jsonify({"error": "total_pence must be >= 0"}), 400

    points = int(round(total * 0.05))
    return jsonify({"points_earned": points}), 200
