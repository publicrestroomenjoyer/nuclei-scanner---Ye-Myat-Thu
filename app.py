from flask import Flask, request, render_template
import subprocess
import os
import threading

app = Flask(__name__)
# Ensure a results directory exists
if not os.path.exists("results"):
    os.makedirs("results")

def run_nuclei(target, scan_id):
    # Using a list for command arguments prevents shell injection
    cmd = ["nuclei", "-u", target, "-json-export", f"results/{scan_id}.json"]
    subprocess.run(cmd)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    target = request.form.get("target", "").strip()
    
    # Basic validation: ensure it's not empty and starts with http
    if not target or not target.startswith("http"):
        return "Invalid target URL", 400

    # Create a unique ID for the scan to prevent file overwriting
    scan_id = "scan_" + os.urandom(4).hex()
    
    # Run in a thread so the app remains responsive
    thread = threading.Thread(target=run_nuclei, args=(target, scan_id))
    thread.start()

    return f"Scan started for {target}. ID: {scan_id}. Results will appear in results/{scan_id}.json"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
