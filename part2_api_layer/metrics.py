from datetime import datetime
from typing import Dict
import time

class SimpleMetrics:
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, list] = {}
        self.start_time = time.time()

    def inc_counter(self, name: str, labels: Dict = None, value: int = 1):
        key = self._make_key(name, labels)
        self.counters[key] = self.counters.get(key, 0) + value

    def set_gauge(self, name: str, value: float, labels: Dict = None):
        key = self._make_key(name, labels)
        self.gauges[key] = value

    def observe_histogram(self, name: str, value: float, labels: Dict = None):
        key = self._make_key(name, labels)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)

    def _make_key(self, name: str, labels: Dict = None) -> str:
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_metrics_text(self) -> str:
        lines = []
        lines.append(f"# Librarian Agent Metrics")
        lines.append(f"# Generated at {datetime.utcnow().isoformat()}")
        lines.append(f"")
        lines.append(f"# HELP uptime_seconds Time since service started")
        lines.append(f"uptime_seconds {time.time() - self.start_time:.2f}")

        for key, value in self.counters.items():
            lines.append(f"{key} {value}")

        for key, value in self.gauges.items():
            lines.append(f"{key} {value}")

        for key, values in self.histograms.items():
            if values:
                avg = sum(values) / len(values)
                lines.append(f"{key}_avg {avg:.4f}")
                lines.append(f"{key}_count {len(values)}")

        return "\n".join(lines)

metrics = SimpleMetrics()
