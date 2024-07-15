import random
import requests
from datadog_checks.base import AgentCheck

__version__ = "1.0.0"


class MyClass(AgentCheck):
    def check(self, init_config, instance):
        status = 0
        try:
            response = requests.get(
                instance["openmetrics_endpoint"],
                timeout=int(init_config.get("timeout", 5)),
            )
            if response.status_code == 200 and response.text:
                status = 1
        except Exception as e:
            print(f"Error ({instance['name']}): {str(e)}")

        self.gauge(
            "dydxopsservices.validator_endpoint_active",
            status,
            tags=[
                f"env:{init_config['env']}",
                f"validator_name:{instance['name']}",
            ],
        )
