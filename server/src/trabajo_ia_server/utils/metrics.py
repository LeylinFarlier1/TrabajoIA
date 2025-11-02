"""Lightweight in-process metrics registry for observability."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Tuple

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)

LabelTuple = Tuple[Tuple[str, str], ...]


def _normalize_labels(labels: Optional[Mapping[str, object]]) -> LabelTuple:
    if not labels:
        return ()
    normalized = tuple(sorted((str(key), str(value)) for key, value in labels.items()))
    return normalized


@dataclass
class HistogramState:
    count: int = 0
    total: float = 0.0
    minimum: Optional[float] = None
    maximum: Optional[float] = None

    def observe(self, value: float) -> None:
        self.count += 1
        self.total += value
        self.minimum = value if self.minimum is None else min(self.minimum, value)
        self.maximum = value if self.maximum is None else max(self.maximum, value)

    def as_dict(self) -> Dict[str, float]:
        average = self.total / self.count if self.count else 0.0
        return {
            "count": float(self.count),
            "sum": float(self.total),
            "avg": float(average),
            "min": float(self.minimum if self.minimum is not None else 0.0),
            "max": float(self.maximum if self.maximum is not None else 0.0),
        }


class MetricsRegistry:
    """Thread-safe registry that tracks counters, gauges, and histograms."""

    def __init__(self, *, enabled: bool = True) -> None:
        self.enabled = enabled
        self._lock = threading.RLock()
        self._counters: Dict[str, Dict[LabelTuple, float]] = {}
        self._gauges: Dict[str, Dict[LabelTuple, float]] = {}
        self._histograms: Dict[str, Dict[LabelTuple, HistogramState]] = {}

    def increment(self, name: str, amount: float = 1.0, *, labels: Optional[Mapping[str, object]] = None) -> None:
        if not self.enabled:
            return
        label_key = _normalize_labels(labels)
        with self._lock:
            bucket = self._counters.setdefault(name, {})
            bucket[label_key] = bucket.get(label_key, 0.0) + float(amount)

    def set_gauge(self, name: str, value: float, *, labels: Optional[Mapping[str, object]] = None) -> None:
        if not self.enabled:
            return
        label_key = _normalize_labels(labels)
        with self._lock:
            bucket = self._gauges.setdefault(name, {})
            bucket[label_key] = float(value)

    def observe(self, name: str, value: float, *, labels: Optional[Mapping[str, object]] = None) -> None:
        if not self.enabled:
            return
        label_key = _normalize_labels(labels)
        with self._lock:
            bucket = self._histograms.setdefault(name, {})
            state = bucket.setdefault(label_key, HistogramState())
            state.observe(float(value))

    def export(self) -> Dict[str, Dict[str, float]]:
        """Export the current metrics snapshot as dictionaries."""

        with self._lock:
            counters = {
                name: {str(labels): value for labels, value in bucket.items()}
                for name, bucket in self._counters.items()
            }
            gauges = {
                name: {str(labels): value for labels, value in bucket.items()}
                for name, bucket in self._gauges.items()
            }
            histograms = {
                name: {str(labels): state.as_dict() for labels, state in bucket.items()}
                for name, bucket in self._histograms.items()
            }

        return {"counters": counters, "gauges": gauges, "histograms": histograms}

    def list_metrics(self) -> Dict[str, Iterable[str]]:
        with self._lock:
            return {
                "counters": list(self._counters.keys()),
                "gauges": list(self._gauges.keys()),
                "histograms": list(self._histograms.keys()),
            }

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


metrics = MetricsRegistry(enabled=config.METRICS_ENABLED)

if metrics.enabled:
    logger.info("Metrics registry initialised with exporter '%s'", config.METRICS_EXPORT_FORMAT)
else:
    logger.info("Metrics registry disabled via configuration")

__all__ = ["MetricsRegistry", "metrics"]
