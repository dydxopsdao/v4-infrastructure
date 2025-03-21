module "datadog_agent" {
  source = "../datadog_agent"

  env             = var.environment
  datadog_api_key = var.datadog_api_key
  dd_site         = var.datadog_site
  service_name    = "metric-ingestor"

  # https://docs.datadoghq.com/containers/docker/prometheus/?tabs=standard#configuration
  docker_labels = {
    "com.datadoghq.ad.instances" = jsonencode([
      for validator in var.validators : {
        openmetrics_endpoint = validator.openmetrics_endpoint
        namespace            = var.metrics_namespace
        metrics              = validator.metrics
        tags                 = ["validator_address:${validator.address}", "is_full_node:false"]
      }
      if validator.openmetrics_endpoint != null
    ])
    "com.datadoghq.ad.check_names" = jsonencode(
      [
        for validator in jsondecode(data.external.merged_validators.result.instances) : "openmetrics"
      ]
    )
    "com.datadoghq.ad.init_configs" = jsonencode(
      [
        for validator in jsondecode(data.external.merged_validators.result.instances) : {}
      ]
    )
  }
}
