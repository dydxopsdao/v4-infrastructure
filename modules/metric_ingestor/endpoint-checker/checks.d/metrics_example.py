import random
import urllib2

from datadog_checks.base import AgentCheck

__version__ = "1.0.0"


class MyClass(AgentCheck):
    def check(self, instance):
        status = 0

        try:
            response = urllib2.urlopen(
                instance["openmetrics_endpoint"],
                timeout=10,
            )
            if len(response.read()) > 0:
                status = 1
        except Exception as e:
            print(f"Error ({instance['name']}): {str(e)}")

        self.gauge(
            # "dydxopsservices.validator_endpoint_active",
            "example_metric.gauge",
            status,
            tags=[
                f"validator_name:{instance['name']}",
            ],
        )
