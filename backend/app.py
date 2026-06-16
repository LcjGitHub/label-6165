"""家庭盆栽换盆历史 — Flask API 服务。"""

from flask import Flask
from flask_cors import CORS

from db import init_db
from seed import seed_if_empty
from routes.plants import plants_bp
from routes.repotting import repotting_bp
from routes.watering import watering_bp
from routes.overview import overview_bp

app = Flask(__name__)
CORS(app, origins=[
    r"http://localhost:*",
    r"http://127.0.0.1:*",
])

app.register_blueprint(plants_bp)
app.register_blueprint(repotting_bp)
app.register_blueprint(watering_bp)
app.register_blueprint(overview_bp)

if __name__ == "__main__":
    init_db()
    seed_if_empty()
    app.run(host="0.0.0.0", port=7000, debug=True)
