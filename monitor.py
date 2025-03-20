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
    categories = OrderedDict({"All": None,
                  "1080, 2080 and Titan": ["1080", "2080", "TITAN"],
                  "3090 and 4090": ["3090", "4090"],
                  "A6000": ["A6000"]
                 })
    categories["1080 and Above"] = categories["1080, 2080 and Titan"] + categories["3090 and 4090"] + categories["A6000"]
    categories["3090 and Above"] = categories["3090 and 4090"] + categories["A6000"]
    categories["A6000 and Above"] = categories["A6000"]

    priority_list = ["woof", "QAQ", "mercury", "Neptune", "aniki", "Brandy", "sctech", "Rum", "nthuee1", "nthuee2", "Nemo", "Tequila", "Gin"]

    
    gpu_info_by_category = {k: [] for k, v in categories.items()}

    if os.path.exists(DATA_DIR):
        all_servers = os.listdir(DATA_DIR)
        # Sort servers based on whether they are in the priority list
        sorted_servers = sorted(all_servers, key=lambda x: (x not in priority_list, priority_list.index(x) if x in priority_list else len(priority_list)))

        for server_name in sorted_servers:
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
