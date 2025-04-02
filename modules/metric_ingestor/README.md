# Metric Ingestor

The Metric Ingestor module uses the Datadog Agent container running on ECS in daemon mode to
consume metrics from external hosts running prometheus endpoints. The Metric Ingestor does not
consume metrics for private/internal hosts such as validators or full nodes running on our
own infrastructure. (Those hosts have their own Datadog sidecars. See the `validator` module for
more information.)

Metric Ingestor runs in Daemon mode to take advantage of public EIP. This is useful if an external
party wishes to whitelist our IP.

Validators to scrape are configured via the `validators` variable, like this:

```hcl
[
  {
    address = "dydxvaloper1mscvgg4g6yqwsep4elhg8a8z874fyafyc9nn3r", 
    openmetrics_endpoint = "http://13.230.43.253:26660",
    endpoint_type = "dydx",
    machine_id = "lorem",
  },
  {
    address = "dydxvaloper1mscvgg4g6yqwsep4elhg8a8z874fyafyc9nn3r", 
    openmetrics_endpoint = "http://13.230.43.253:26660",
    endpoint_type = "dydx",
    machine_id = "ipsum",
  },
  {
    address = "dydxvaloper1mscvgg4g6yqwsep4elhg8a8z874fyafyc9nn3r", 
    openmetrics_endpoint = "http://13.230.43.253:8002",
    endpoint_type = "slinky",
  },
]
```

These validators are scraped by the Datadog Agent via two custom checks:

- `chain_metadata`: Emits metrics that track the voting power of all validators in the active set. Also it saves the monikers of all validators to a file that can be used by the `validator_metrics` check.

- `validator_metrics`: Extends the `OpenMetricsBaseCheck` class to scrape metrics from multiple endpoints and decorate them with additional tags.