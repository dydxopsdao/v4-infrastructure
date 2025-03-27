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
validators = [
{
  address = "dydxvaloper1000000001",
  openmetrics_endpoint = "https://validator.figment.com:1317"
},
{
  address = "dydxvaloper1000000002",
  openmetrics_endpoint = "https://validator.frens.com:1317"
}]
```
(see: https://docs.datadoghq.com/metrics/custom_metrics/agent_metrics_submission/?tab=count):

Apart from the regular Datadog Agent operation, there are also a custom checks:

- `validator_metrics`: Extends the `OpenMetricsBaseCheck` class to scrape metrics from multiple
  endpoints and decorate them with additional tags.
- `voting_power`: Emits a custom metric that tracks the voting power of validators in the active set.