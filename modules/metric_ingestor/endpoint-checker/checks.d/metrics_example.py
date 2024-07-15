import random

from datadog_checks.base import AgentCheck

__version__ = "1.0.0"

class MyClass(AgentCheck):
    def check(self, instance):
        self.gauge(
            "example_metric.gauge",
            random.randint(0, 10),
            tags=[
                "env:testnet",
                "metric_submission_type:gauge",
                f"validator_name:{instance['name']}",
            ],
        )