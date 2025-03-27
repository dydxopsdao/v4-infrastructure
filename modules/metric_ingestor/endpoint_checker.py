# For Datadog custom check API see:
# - https://docs.datadoghq.com/developers/custom_checks/write_agent_check/
# - https://github.com/DataDog/datadog-agent/blob/main/docs/dev/checks/README.md

import re
import requests

from datadog_checks.base import AgentCheck
from prometheus_client.parser import text_string_to_metric_families

__version__ = "1.0.0"
REACHABILITY_METRIC_NAME = "dydxopsservices.validator_endpoint_reachability"


# class EndpointChecker(AgentCheck):
#     def check(self, instance):
#         metric_value = 0

#         try:
#             response = requests.get(
#                 instance["openmetrics_endpoint"],
#                 timeout=int(self.init_config["timeout"]),
#             )
#             if response.ok and response.text:
#                 metric_value = 1
#         except Exception as e:
#             print(f"Error ({instance['name']}): {str(e)}")

#         metric_source = "slinky" if instance["name"].startswith("slinky:") else "dydx"

#         self.gauge(
#             REACHABILITY_METRIC_NAME,
#             metric_value,
#             tags=[
#                 f"env:{self.init_config['env']}",
#                 f"validator_address:{instance['address']}",
#                 f"metric_source:{metric_source}",
#                 f"name:{instance['name']}",
#             ],
#         )


class ValidatorMetricsCheck(AgentCheck):
    def __init__(self, name, init_config, instances):
        super().__init__(name, init_config, instances)

        self.env = self.init_config.get("env")
        self.metrics = self.init_config.get("metrics")
        self.metrics_namespace = self.init_config.get("metrics_namespace")
        self.max_returned_metrics = self.init_config.get("max_returned_metrics")

    def check(self, instance):
        return
    
        self.log.info("Starting ValidatorMetricsCheck for %s", instance)

        # Get configuration from the instance
        endpoint_dydx = instance.get("endpoint_dydx")
        endpoint_slinky = instance.get("endpoint_slinky")
        validator_address = instance.get("address")
        validator_name = instance.get("name")

        if endpoint_dydx is not None:
            self.fetch_metrics(endpoint_dydx, "dydx", validator_address, validator_name)

        if endpoint_slinky is not None:
            self.fetch_metrics(
                endpoint_slinky, "slinky", validator_address, validator_name
            )

    def fetch_metrics(self, endpoint, metric_source, validator_address, validator_name):
        try:
            # Fetch Prometheus metrics
            response = requests.get(endpoint)
            response.raise_for_status()
            metrics_text = response.text
            metric_counter = 0

            # Parse Prometheus format
            for family in text_string_to_metric_families(metrics_text):
                # The family type tells us what kind of metric it is
                metric_type = family.type
                
                for sample in family.samples:
                    # Check if sample name matches any of the regexp patterns in self.metrics
                    if self.metrics is not None and not any(
                        re.match(pattern, sample.name) for pattern in self.metrics
                    ):
                        continue

                    # Check if we've exceeded the max number of metrics to return
                    metric_counter += 1
                    if (
                        self.max_returned_metrics is not None
                        and metric_counter > self.max_returned_metrics
                    ):
                        self.log.warning(
                            f"Max metrics returned ({self.max_returned_metrics}) reached for {endpoint}"
                        )
                        return

                    # Get metric name and value
                    name_prefix = (
                        f"{self.metrics_namespace}." if self.metrics_namespace else ""
                    )
                    metric_name = f"{name_prefix}{sample.name}"
                    metric_value = sample.value

                    # TODO: Query your external source for dynamic data, nameley the voting power
                    # dynamic_data = self.get_external_data(validator_address)

                    # Combine static and dynamic tags
                    tags = [
                        f"env:{self.env}",
                        f"validator_address:{validator_address}",
                        f"validator_name:{validator_name}",
                        f"metric_source:{metric_source}",
                        # f"is_full_node:false",
                        # Add dynamic tags from external source
                        # f"dynamic_tag:{dynamic_data['some_field']}"
                    ]

                    # Add labels from sample as tags
                    for label_name, label_value in sample.labels.items():
                        tags.append(f"{label_name}:{label_value}")

                    # Submit the metric with the appropriate type
                    if metric_type == "counter":
                        # self.log.info("Counter metric: %s %s %s", metric_name, metric_value, tags)
                        self.monotonic_count(metric_name, metric_value, tags=tags)
                    elif metric_type == "gauge":
                        self.gauge(metric_name, metric_value, tags=tags)
                    elif metric_type == "histogram":
                        # For histograms, we need to calculate quantiles
                        if ".sum" in sample.name:
                            self.gauge(metric_name, metric_value, tags=tags)
                        elif ".count" in sample.name:
                            self.monotonic_count(metric_name, metric_value, tags=tags)
                        else:
                            self.gauge(metric_name, metric_value, tags=tags)
                    elif metric_type == "summary":
                        # Similar to histogram handling
                        if ".sum" in sample.name:
                            self.gauge(metric_name, metric_value, tags=tags)
                        elif ".count" in sample.name:
                            self.monotonic_count(metric_name, metric_value, tags=tags)
                        else:
                            self.gauge(metric_name, metric_value, tags=tags)
                    else:
                        # Default to gauge for unknown types
                        self.gauge(metric_name, metric_value, tags=tags)

        except Exception as e:
            self.log.error(f"Error collecting metrics from {endpoint}: {str(e)}")
            raise
        finally:
            self.log.info(
                "Finished ValidatorMetricsCheck for %s with %d metrics",
                endpoint,
                metric_counter,
            )

    # def get_external_data(self, validator_address):
    #     """
    #     Query external source for dynamic data.
    #     This could be an API call, database query, etc.
    #     """
    #     try:
    #         # Example: Make API call to external service
    #         response = requests.get(
    #             f"https://your-api.com/validator/{validator_address}"
    #         )
    #         return response.json()
    #     except Exception as e:
    #         self.log.error(f"Error fetching external data: {str(e)}")
    #         return {}
