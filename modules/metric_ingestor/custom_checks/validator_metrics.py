# For docs on custom OpenMetrics check see:
# - https://docs.datadoghq.com/developers/custom_checks/prometheus/

import os
import json

from datadog_checks.base import OpenMetricsBaseCheckV2
from datadog_checks.base.checks.openmetrics.v2.transform import get_native_dynamic_transformer

__version__ = "1.0.0"
REACHABILITY_METRIC_NAME = "dydxopsservices.validator_endpoint_reachability"
MONIKERS_FILE = "/tmp/monikers.json"

class ValidatorMetricsCheck(OpenMetricsBaseCheckV2):
    def __init__(self, name, init_config, instances):
        super(ValidatorMetricsCheck, self).__init__(name, init_config, instances)

    def configure_scrapers(self):
        super().configure_scrapers()
        for scraper in self.scrapers.values():
            global_options = scraper.metric_transformer.global_options
            scraper.metric_transformer.add_custom_transformer(
                r".*",
                # we need the global_options for the scraper to be available in the transformer
                lambda metric, sample_data, runtime_data, global_options=global_options: self.custom_metric_transformer(
                    metric, sample_data, runtime_data, global_options
                ),
                pattern=True
            )

    def custom_metric_transformer(self, metric, sample_data, runtime_data, global_options):
        if metric.name.startswith("tendermint_"):
            metric.name = "cometbft_" + metric.name[len("tendermint_"):]
        # Always submit the metric, using the native transformer
        transformer = get_native_dynamic_transformer(self, metric.name, {}, global_options)
        transformer(metric, sample_data, runtime_data)

    def check(self, instance):
        monikers = self._get_monikers()
        if not monikers:
            self.log.warning("No monikers found")
            return

        dynamic_tags = self._get_dynamic_tags(instance, monikers)
        all_tags = instance["tags"] + dynamic_tags
        self.set_dynamic_tags(*dynamic_tags)

        try:
            super().check(instance)
        except Exception as e:
            self.log.error("Error checking instance: %s", e)
            is_reachable = 0
        else:
            is_reachable = 1

        self.gauge(
            REACHABILITY_METRIC_NAME,
            is_reachable,
            tags=all_tags,
        )

    def _get_dynamic_tags(self, instance, monikers):
        address = instance["address"]
        machine_id = instance["machine_id"] or "1"

        moniker = monikers.get(address)
        if moniker:
            return [
                f"moniker:{moniker}",
                f"n:{machine_id}",
            ]
        else:
            self.log.warning(f"No moniker found for address: {address}")
            return []

    def _get_monikers(self):
        if not os.path.exists(MONIKERS_FILE):
            return {}

        with open(MONIKERS_FILE, "r") as f:
            return json.load(f)
