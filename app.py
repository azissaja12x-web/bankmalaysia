import os
from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
from datetime import datetime

app = Flask(__name__)

# Mengambil kredensial Supabase dari Environment Variables (agar aman)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Membuat koneksi ke klien Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/verifikasi", methods=["POST"])
def verifikasi():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request harus berupa JSON."}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Data JSON tidak valid."}), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    image_data = data.get("image")

    if latitude is None or longitude is None or not image_data:
        return jsonify({"status": "error", "message": "Lokasi atau foto tidak lengkap."}), 400

    try:
        if "," not in image_data:
            return jsonify({"status": "error", "message": "Format foto tidak valid."}), 400

        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        filename = f"verifikasi_{now.strftime('%Y%m%d_%H%M%S_%f')}.jpg"

        # Menyimpan data langsung ke tabel Supabase
        # image_data (Base64) disimpan langsung sesuai struktur tabelmu
        response = supabase.table("verifikasi_log").insert({
            "timestamp": timestamp_str,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "image_name": filename,
            "image_base64": image_data 
        }).execute()

        print("=" * 60)
        print("[SERVER] Verifikasi berhasil disimpan ke Supabase")
        print(f"[SERVER] Lokasi: {latitude}, {longitude}")
        print("=" * 60)

        return jsonify({
            "status": "success",
            "message": "Verifikasi berhasil. Lokasi dan foto sudah dicatat di database.",
            "filename": filename
        }), 200

    except Exception as e:
        print(f"[SERVER] Gagal memproses data: {e}")
        return jsonify({
            "status": "error",
            "message": "Gagal menyimpan data ke server."
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
