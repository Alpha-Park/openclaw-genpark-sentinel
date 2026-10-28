# -*- coding: utf-8 -*-
"""
OpenClaw GenPark Sentinel MCP Server
Exposes rate anomaly detection and threat mitigation tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import OpenClawGenParkSentinel

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "openclaw-genpark-sentinel", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "evaluate_traffic_window",
                        "description": "Evaluates real-time agent telemetry for DDoS, token depletion spikes, and calculates throttling.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "current_token_rate_per_sec": {"type": "number"},
                                "request_latency_p99_ms": {"type": "number"},
                                "recent_token_rate_history": {"type": "array", "items": {"type": "number"}}
                            },
                            "required": ["current_token_rate_per_sec", "request_latency_p99_ms"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "evaluate_traffic_window":
            sentinel = OpenClawGenParkSentinel()
            res = sentinel.evaluate_traffic_window(
                current_token_rate_per_sec=args.get("current_token_rate_per_sec", 150.0),
                request_latency_p99_ms=args.get("request_latency_p99_ms", 320.0),
                recent_token_rate_history=args.get("recent_token_rate_history")
            )
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        s = OpenClawGenParkSentinel()
        test_res = s.evaluate_traffic_window(500.0, 950.0, [100.0, 110.0, 105.0])
        print(f"Test Action: {test_res['mitigation_action']}")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
