from flask import Flask, request, render_template, send_file, abort
import subprocess, os, time, json

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    target = request.form["target"]
    os.makedirs("results", exist_ok=True)
    output = f"results/output_{int(time.time())}.jsonl"
    cmd = [
        "nuclei",
        "-u", target,
        "-t", "/root/nuclei-templates/http/misconfiguration/http-missing-security-headers.yaml",
        "-jsonl",
        "-o", output,
        "-c", "1",
        "-rl", "1",
        "-timeout", "10",
        "-retries", "0",
        "-silent",
        "-duc"
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    except Exception as e:
        return f"Scan error: {e}"

    findings = []
    if os.path.exists(output):
        with open(output) as f:
            for line in f:
                if line.strip():
                    findings.append(json.loads(line))

    return render_template(
        "index.html",
        target=target,
        findings=findings,
        stderr=r.stderr,
        output_file=os.path.basename(output),
    )

@app.route("/download")          # ← must be BEFORE app.run()
def download():
    filename = request.args.get("file", "")
    safe_path = os.path.realpath(os.path.join("results", os.path.basename(filename)))
    results_dir = os.path.realpath("results")
    if not safe_path.startswith(results_dir) or not os.path.exists(safe_path):
        abort(404)
    return send_file(safe_path, as_attachment=True, download_name=os.path.basename(safe_path))

if __name__ == "__main__":       # ← app.run() always last
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
