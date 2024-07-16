import random
import urllib.request

from datadog_checks.base import AgentCheck

__version__ = "1.0.0"


class MyClass(AgentCheck):
    def check(self, instance):
        status = 0

        try:
            response = urllib.request.urlopen(
                instance["openmetrics_endpoint"],
                timeout=int(self.init_config['timeout']),
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
                f"env:{self.init_config['env']}",
                f"validator_name:{instance['name']}",
            ],
        )
