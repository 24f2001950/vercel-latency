from http.server import BaseHTTPRequestHandler
import json
import numpy as np

# Load telemetry data once
with open("q-vercel-latency.json") as f:
    DATA = json.load(f)

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):

        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        payload = json.loads(body)

        regions = payload.get("regions", [])
        threshold = payload.get("threshold_ms", 0)

        result = {}

        for r in regions:
            rows = [x for x in DATA if x["region"] == r]

            latencies = [x["latency_ms"] for x in rows]
            uptimes = [x["uptime"] for x in rows]

            result[r] = {
                "avg_latency": float(np.mean(latencies)) if latencies else 0,
                "p95_latency": float(np.percentile(latencies,95)) if latencies else 0,
                "avg_uptime": float(np.mean(uptimes)) if uptimes else 0,
                "breaches": len([x for x in latencies if x > threshold])
            }

        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()

        self.wfile.write(json.dumps(result).encode())