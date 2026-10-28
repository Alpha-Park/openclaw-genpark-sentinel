# -*- coding: utf-8 -*-
"""
OpenClaw GenPark Sentinel Client
Real-time sliding window token velocity anomaly detection and adaptive rate-limiting sentinel.
Zero external dependencies -- Python 3.9+ standard library only.
"""

import math
from typing import Dict, Any, List

class OpenClawGenParkSentinel:
    """
    Agent Infrastructure Sentinel:
    Detects abnormal token burn spikes, potential DDoS attacks, and implements
    adaptive token bucket rate throttling with statistical Z-score outlier detection.
    """

    def __init__(self, baseline_tps: float = 120.0, z_threshold: float = 2.58):
        self.base_tps = baseline_tps
        self.z_thresh = z_threshold

    def calculate_z_score(self, current_val: float, history: List[float]) -> float:
        """Calculates standard Z-score given historical metric window."""
        if len(history) < 3:
            return 0.0
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        std_dev = math.sqrt(variance)
        if std_dev == 0.0:
            return 0.0
        return round((current_val - mean) / std_dev, 2)

    def evaluate_traffic_window(
        self,
        current_token_rate_per_sec: float,
        request_latency_p99_ms: float,
        recent_token_rate_history: List[float] = None,
        token_bucket_capacity: float = 500.0,
        current_bucket_tokens: float = 350.0
    ) -> Dict[str, Any]:
        """
        Evaluates real-time agent telemetry for DDoS, token depletion spikes, and calculates throttling.
        """
        if recent_token_rate_history is None:
            recent_token_rate_history = [110.0, 115.0, 108.0, 122.0, 118.0, 125.0]

        z_score = self.calculate_z_score(current_token_rate_per_sec, recent_token_rate_history)
        is_anomaly = (z_score >= self.z_thresh) or (current_token_rate_per_sec > self.base_tps * 3.0)

        # Bucket fill ratio
        fill_ratio = round(current_bucket_tokens / max(1.0, token_bucket_capacity), 3)

        if is_anomaly and fill_ratio < 0.20:
            threat_level = "CRITICAL_ATTACK_MITIGATION"
            throttled_rate = round(self.base_tps * 0.25, 1)
            action = "ENFORCE_EXPONENTIAL_BACKOFF"
        elif is_anomaly:
            threat_level = "HIGH_SURGE_DETECTED"
            throttled_rate = round(self.base_tps * 0.60, 1)
            action = "APPLY_LEAKY_BUCKET_THROTTLE"
        elif fill_ratio < 0.15:
            threat_level = "CAPACITY_EXHAUSTION_WARNING"
            throttled_rate = round(self.base_tps * 0.80, 1)
            action = "SCALE_UP_REPLICA"
        else:
            threat_level = "NOMINAL_HEALTHY"
            throttled_rate = current_token_rate_per_sec
            action = "PASS_THROUGH"

        return {
            "current_token_rate_per_sec": current_token_rate_per_sec,
            "anomaly_z_score": z_score,
            "threat_level": threat_level,
            "mitigation_action": action,
            "throttled_allowance_tps": throttled_rate,
            "bucket_health": {
                "capacity": token_bucket_capacity,
                "available_tokens": current_bucket_tokens,
                "fill_ratio": fill_ratio
            },
            "p99_latency_ms": request_latency_p99_ms
        }
