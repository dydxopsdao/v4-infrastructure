import random
import urllib

from datadog_checks.base import AgentCheck

__version__ = "1.0.0"


class MyClass(AgentCheck):
    def check(self, instance):
        status = 0

        try:
            response = urllib.urlopen(
                instance["openmetrics_endpoint"],
                timeout=10,
            )
            if len(response.read()) > 0:
                status = 1
        except Exception as e:
            print(f"Error ({instance['name']}): {str(e)}")

        # "dydxopsservices.validator_endpoint_active",
        self.gauge(
            "example_metric.gauge",
            status,
            tags=[
                f"validator_name:{instance['name']}",
            ],
        )
