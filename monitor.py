from flask import Flask, render_template, jsonify
import os
import json
from collections import OrderedDict

app = Flask(__name__)
DATA_DIR = "data"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gpu_data")
def gpu_data():

    """
    categories = OrderedDict({"All": None,
                  "1080, 2080 and Titan": ["NVIDIA GeForce RTX 1080", "NVIDIA GeForce GTX 1080", "NVIDIA GeForce GTX 1080 Ti", "NVIDIA GeForce RTX 2080", "NVIDIA GeForce RTX 2080 Ti", "NVIDIA GeForce RTX TITAN X"],
                  "3090 and 4090": ["NVIDIA GeForce RTX 3090", "NVIDIA GeForce RTX 4090"],
                  "A6000": ["NVIDIA RTX A6000"]
                 })
    """
    categories = OrderedDict({"All": None,
                  "1080, 2080 and Titan": ["1080", "2080", "TITAN"],
                  "3090 and 4090": ["3090", "4090"],
                  "A6000": ["A6000"]
                 })
    categories["1080 and Above"] = categories["1080, 2080 and Titan"] + categories["3090 and 4090"] + categories["A6000"]
    categories["3090 and Above"] = categories["3090 and 4090"] + categories["A6000"]
    categories["A6000 and Above"] = categories["A6000"]

    
    gpu_info_by_category = {k: [] for k, v in categories.items()}

    if os.path.exists(DATA_DIR):
        for server_name in os.listdir(DATA_DIR):
            server_path = os.path.join(DATA_DIR, server_name, "gpu_stats.json")
            if os.path.exists(server_path):
                with open(server_path, "r") as f:
                    gpu_stats = json.load(f)

                    # Categorize GPUs by type
                    for gpu in gpu_stats:
                        for category_name, category_keyword in categories.items():
                            if category_keyword is None or any([keyword in gpu['name'] for keyword in category_keyword]):
                                gpu_data = gpu
                                gpu_data["server"] = server_name

                                gpu_info_by_category[category_name].append(gpu_data)
    
    #print(gpu_info_by_category)
    categories = [k for k in categories.keys()]

    return jsonify({"categories": categories, "gpu_types": gpu_info_by_category})


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=3333)

    #app.run(host="0.0.0.0", port=3333, debug=True)
