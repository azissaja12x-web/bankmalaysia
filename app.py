import os
from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
from datetime import datetime

app = Flask(__name__)

def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Kredensial SUPABASE_URL atau SUPABASE_KEY tidak ditemukan di Environment Variables.")
    return create_client(url, key)

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

        # Memanggil klien Supabase secara aman di dalam fungsi runtime
        supabase_client = get_supabase_client()
        
        response = supabase_client.table("verifikasi_log").insert({
            "timestamp": timestamp_str,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "image_name": filename,
            "image_base64": image_data 
        }).execute()

        return jsonify({
            "status": "success",
            "message": "Verifikasi berhasil. Lokasi dan foto sudah dicatat di database.",
            "filename": filename
        }), 200

    except Exception as e:
        print(f"[SERVER ERROR] {e}")
        return jsonify({
            "status": "error",
            "message": f"Gagal menyimpan data ke server: {str(e)}"
        }), 500

# Penting untuk arsitektur serverless Vercel
# Jangan gunakan app.run(debug=True) di luar scope lokal jika dijalankan di Vercel
if __name__ == "__main__":
    app.run(debug=True)
