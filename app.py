from flask import Flask, render_template, request, jsonify
import openai, os, json, sqlite3
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

DB_PATH = "results.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            image_url TEXT,
            created_at TEXT
        )""")
init_db()

preset_prompts = {
    "polynesien": "Motif tribal inspiré des tatouages polynésiens, symétrique, noir et blanc",
    "celtique": "Motif tribal celtique, complexe et en style gravure",
    "mandala": "Motif tribal mandala, circulaire et finement détaillé",
    "viking": "Symbole viking tribal, inspiré des runes, noir et blanc"
}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", presets=preset_prompts)

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.json
    prompt = data.get("prompt")
    count = int(data.get("count", 1))
    urls = []
    try:
        for _ in range(count):
            response = openai.Image.create(
                prompt=prompt,
                model="dall-e-3",
                n=1,
                size="1024x1024"
            )
            image_url = response["data"][0]["url"]
            urls.append(image_url)

            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT INTO generations (prompt, image_url, created_at) VALUES (?, ?, ?)",
                             (prompt, image_url, datetime.now().isoformat()))
        return jsonify({"urls": urls})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/auto_prompt", methods=["POST"])
def auto_prompt():
    theme = request.json.get("theme", "")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un artiste spécialisé dans les motifs tribaux."},
                {"role": "user", "content": f"Crée une description artistique d’un motif tribal dans le style '{theme}'."}
            ]
        )
        prompt = response["choices"][0]["message"]["content"]
        return jsonify({"prompt": prompt.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def history():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT prompt, image_url, created_at FROM generations ORDER BY id DESC LIMIT 20").fetchall()
        return jsonify([{"prompt": r[0], "url": r[1], "date": r[2]} for r in rows])

@app.route("/capcut_json", methods=["POST"])
def capcut_export():
    data = request.json
    image_url = data.get("url", "")
    export_json = {
        "type": "CapCutProject",
        "version": "1.0",
        "media": [
            {"type": "image", "src": image_url, "style": "centered", "duration": 5}
        ]
    }
    return jsonify(export_json)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
