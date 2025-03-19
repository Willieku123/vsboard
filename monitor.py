from flask import Flask, render_template, jsonify
import os
import json

app = Flask(__name__)
DATA_DIR = "data"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gpu_data")
def gpu_data():
    server_data = {}

    categories = {"All": None,
               "1080 and Above": ["NVIDIA GeForce RTX 1080", "NVIDIA GeForce RTX 2080", "NVIDIA GeForce RTX 2080 Ti", "NVIDIA GeForce RTX 3090", "NVIDIA GeForce RTX 4090", "NVIDIA RTX A6000"],
               "3090 and Above": ["NVIDIA GeForce RTX 3090", "NVIDIA GeForce RTX 4090", "NVIDIA RTX A6000"],
               "A6000 and Above": ["NVIDIA RTX A6000"]}
    
    gpu_info_by_category = {k: [] for k, v in categories.items()}

    if os.path.exists(DATA_DIR):
        for server_name in os.listdir(DATA_DIR):
            server_path = os.path.join(DATA_DIR, server_name, "gpu_stats.json")
            if os.path.exists(server_path):
                with open(server_path, "r") as f:
                    gpu_stats = json.load(f)
                    server_data[server_name] = gpu_stats

                    # Categorize GPUs by type
                    for gpu in gpu_stats:
                        for category_name, category_content in categories.items():
                            if category_content is None or gpu['name'] in category_content:
                                gpu_data = gpu
                                gpu_data["server"] = server_name

                                gpu_info_by_category[category_name].append(gpu_data)
    
   #print(gpu_info_by_category)

    return jsonify({"servers": server_data, "gpu_types": gpu_info_by_category})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3333, debug=True)
