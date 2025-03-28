# For Datadog custom check API see:
# - https://docs.datadoghq.com/developers/custom_checks/write_agent_check/
# - https://github.com/DataDog/datadog-agent/blob/main/docs/dev/checks/README.md

import re
import requests
from itertools import chain

from datadog_checks.base import OpenMetricsBaseCheckV2
from prometheus_client.parser import text_string_to_metric_families

__version__ = "1.0.0"
REACHABILITY_METRIC_NAME = "dydxopsservices.validator_endpoint_reachability"


class ValidatorMetricsCheck(OpenMetricsBaseCheckV2):
    def __init__(self, name, init_config, instances):
        super(ValidatorMetricsCheck, self).__init__(name, init_config, instances)

    # def set_dynamic_tags(self, *tags):
    #     self.tags = tuple(chain(self.static_tags, tags))
        
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


# class ValidatorMetricsCheck(OpenMetricsBaseCheck):
#     def __init__(self, name, init_config, instances):
#         self.log.info("Initializing ValidatorMetricsCheck")

#         # Initialize with parent class but capture original parameters
#         super().__init__(name, init_config, instances)
        
#         # Store our custom parameters from init_config
#         self.env = self.init_config.get("env")
#         self.metrics_namespace = self.init_config.get("metrics_namespace")
#         self.metrics = self.init_config.get("metrics")
#         self.max_returned_metrics = self.init_config.get("max_returned_metrics")
        
#     def check(self, instance):
#         self.log.info("Starting ValidatorMetricsCheck for %s", instance)
        
#         validator_address = instance.get("address")
#         validator_name = instance.get("name")
        
#         # Process each endpoint
#         self._process_endpoint(
#             instance.get("endpoint_dydx"),
#             validator_address,
#             validator_name,
#             "dydx"
#         )
        
#         self._process_endpoint(
#             instance.get("endpoint_slinky"),
#             validator_address,
#             validator_name,
#             "slinky"
#         )
        
#         self.log.info("Finished ValidatorMetricsCheck")
    
#     def _process_endpoint(self, endpoint_url, validator_address, validator_name, metric_source):
#         """Process a single metrics endpoint with error handling"""
#         if endpoint_url is None:
#             return
            
#         try:
#             scraper_config = self._create_scraper_config(
#                 endpoint_url, 
#                 validator_address, 
#                 validator_name, 
#                 metric_source
#             )
#             self.process(scraper_config)
#         except Exception as e:
#             self.log.error(f"Error processing {metric_source} endpoint {endpoint_url}: {str(e)}")
#             self.log.exception("Exception details")
            
#     def _create_scraper_config(self, endpoint, validator_address, validator_name, metric_source):
#         """Create a scraper configuration dictionary for OpenMetricsBaseCheck"""
#         return {
#             'prometheus_url': endpoint,
#             'namespace': self.metrics_namespace,
#             'metrics': self.metrics,
#             'prometheus_metrics_prefix': '',
#             'health_service_check': True,
#             'extra_headers': {},
#             'tags': [
#                 f"env:{self.env}",
#                 f"validator_address:{validator_address}",
#                 f"validator_name:{validator_name}",
#                 f"metric_source:{metric_source}",
#                 f"source:custom_check"
#             ],
#             'max_returned_metrics': self.max_returned_metrics,
#             'send_histogram_buckets': True,  # Include histogram buckets
#             'send_monotonic_counter': True   # Send counters as monotonic_count
#         }

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
