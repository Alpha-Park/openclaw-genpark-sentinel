# -*- coding: utf-8 -*-
"""
Example usage of OpenClawGenParkSentinel
Demonstrates token spike detection and automatic rate throttling.
"""

from client import OpenClawGenParkSentinel

def main():
    sentinel = OpenClawGenParkSentinel(baseline_tps=120.0)

    cases = [
        {
            "name": "Case 1: Normal Steady Traffic",
            "rate": 124.0, "p99": 210.0, "hist": [115.0, 118.0, 122.0, 120.0], "cap": 500.0, "tokens": 420.0
        },
        {
            "name": "Case 2: Sudden 5x Token Burn Spike (Anomaly Attack)",
            "rate": 620.0, "p99": 1450.0, "hist": [115.0, 118.0, 120.0, 122.0], "cap": 500.0, "tokens": 60.0
        }
    ]

    print("================================================================")
    print("OpenClaw GenPark Sentinel - Live Telemetry Monitoring")
    print("================================================================\n")

    for c in cases:
        res = sentinel.evaluate_traffic_window(
            current_token_rate_per_sec=c["rate"],
            request_latency_p99_ms=c["p99"],
            recent_token_rate_history=c["hist"],
            token_bucket_capacity=c["cap"],
            current_bucket_tokens=c["tokens"]
        )
        print(f"[{c['name']}]")
        print(f"  Current Token Rate    : {res['current_token_rate_per_sec']} TPS (Z-Score: {res['anomaly_z_score']})")
        print(f"  Threat Verdict        : {res['threat_level']}")
        print(f"  Mitigation Action     : {res['mitigation_action']}")
        print(f"  Throttled Allowance   : {res['throttled_allowance_tps']} TPS (Fill: {res['bucket_health']['fill_ratio']*100:.1f}%)\n")

if __name__ == "__main__":
    main()
