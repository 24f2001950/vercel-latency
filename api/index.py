import json

with open("q-vercel-latency.json") as f:
    DATA = json.load(f)

def mean(values):
    return sum(values) / len(values) if values else 0

def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    k = int(len(values) * p / 100)
    return values[min(k, len(values)-1)]

def handler(request):

    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }

    body = json.loads(request.body)
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    result = {}

    for r in regions:
        rows = [x for x in DATA if x["region"] == r]

        latencies = [x["latency_ms"] for x in rows]
        uptimes = [x["uptime"] for x in rows]

        result[r] = {
            "avg_latency": mean(latencies),
            "p95_latency": percentile(latencies, 95),
            "avg_uptime": mean(uptimes),
            "breaches": len([x for x in latencies if x > threshold])
        }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(result)
    }