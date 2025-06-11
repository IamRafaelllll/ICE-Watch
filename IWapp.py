from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta
from geopy.distance import geodesic

app = Flask(__name__)
DB = "sightings.db"
UCI_COORDS = (33.6405, -117.8443)

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY,
            city TEXT,
            count INTEGER,
            detained TEXT,
            lat REAL,
            lon REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        city = request.form["city"]
        count = request.form["count"]
        detained = request.form["detained"]
        lat = float(request.form["lat"])
        lon = float(request.form["lon"])

        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO reports (city, count, detained, lat, lon) VALUES (?, ?, ?, ?, ?)",
                         (city, count, detained, lat, lon))
        return redirect("/reports")
    return render_template("index.html")

@app.route("/reports")
def reports():
    recent = datetime.now() - timedelta(days=5)
    with sqlite3.connect(DB) as conn:
        cursor = conn.execute("SELECT city, count, detained, lat, lon, timestamp FROM reports WHERE timestamp >= ? ORDER BY timestamp DESC", (recent,))
        rows = cursor.fetchall()

    reports = []
    for row in rows:
        city, count, detained, lat, lon, timestamp = row
        dist = round(geodesic(UCI_COORDS, (lat, lon)).miles, 2)
        reports.append({"city": city, "count": count, "detained": detained, "lat": lat, "lon": lon, "timestamp": timestamp, "distance": dist})

    return render_template("reports.html", reports=reports)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
