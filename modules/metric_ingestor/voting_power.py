# For Datadog custom check API see:
# - https://docs.datadoghq.com/developers/custom_checks/write_agent_check/
# - https://github.com/DataDog/datadog-agent/blob/main/docs/dev/checks/README.md

import requests
import json
from decimal import Decimal

from datadog_checks.base import AgentCheck


class VotingPowerCheck(AgentCheck):
    def check(self, instance):
        # Get configuration
        base_api_url = instance.get("base_api_url")

        # Fetch validator data
        response = requests.get(
            f"{base_api_url}/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED&pagination.limit=100"
        )
        data = response.json()

        # Calculate total power
        total_power = sum(
            Decimal(v["tokens"]) for v in data["validators"] if not v["jailed"]
        )
        total_power_normalized = total_power / Decimal("1000000000000000000")

        # Submit total voting power
        self.gauge("dydxopsservices.voting_power.total_tokens", float(total_power_normalized))

        # Process validators
        validators = []
        for validator in data["validators"]:
            if validator["jailed"]:
                continue

            voting_power = Decimal(validator["tokens"]) / Decimal("1000000000000000000")
            percentage = (voting_power / total_power_normalized) * Decimal("100")

            validators.append({
                "validator_address": validator["operator_address"],
                "moniker": validator["description"]["moniker"],
                "voting_power": voting_power,
                "percentage": percentage,
            })

        # Sort validators by voting power (descending)
        validators.sort(key=lambda x: x["voting_power"], reverse=True)

        # Calculate cumulative share and limit to top 60
        cumulative_sum = Decimal("0")
        for validator in validators[:60]:
            cumulative_sum += validator["percentage"]
            
            tags = [
                f"validator_address:{validator['validator_address']}",
                f"moniker:{validator['moniker']}",
            ]

            # Submit metrics with all values
            self.gauge(
                "dydxopsservices.voting_power.tokens",
                float(validator["voting_power"]),
                tags=tags
            )
            self.gauge(
                "dydxopsservices.voting_power.percentage",
                float(validator["percentage"]),
                tags=tags
            )
            self.gauge(
                "dydxopsservices.voting_power.cumulative_share",
                float(cumulative_sum),
                tags=tags
            )
