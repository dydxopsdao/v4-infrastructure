module "datadog_agent" {
  source = "../datadog_agent"

  env             = var.environment
  datadog_api_key = var.datadog_api_key
  dd_site         = var.datadog_site
  service_name    = "metric-ingestor"

  docker_labels = {
    "com.datadoghq.ad.instances" = jsonencode(
      []
    ),
    "com.datadoghq.ad.check_names" = jsonencode(
      ["openmetrics"]
    ),
    "com.datadoghq.ad.init_configs" = jsonencode(
      [{}]
    )
  }

  # docker_labels = {
  #   "com.datadoghq.ad.instances" = jsonencode(
  #     [
  #       for validator in var.validators : {
  #         "openmetrics_endpoint" : validator.endpoint_dydx,
  #         "namespace" : var.metrics_namespace,
  #         "metrics" : var.metrics,
  #         "tags" : [
  #           "validator_address:${validator.address}",
  #           "validator_name:${validator.name}",
  #           "is_full_node:false",
  #           "source:openmetrics_integration",
  #         ],
  #         "max_returned_metrics" : var.max_returned_metrics
  #       }
  #     ]
  #   ),
  #   "com.datadoghq.ad.check_names" = jsonencode(
  #     [
  #       for validator in var.validators : "openmetrics"
  #     ]
  #   ),
  #   "com.datadoghq.ad.init_configs" = jsonencode(
  #     [
  #       for validator in var.validators : {}
  #     ]
  #   )
  # }

  # https://docs.datadoghq.com/containers/docker/prometheus/?tabs=standard#configuration
  # docker_labels = {
  #   "com.datadoghq.ad.instances" = jsonencode(
  #     [
  #       for validator in var.validators : {
  #         "openmetrics_endpoint" : validator.openmetrics_endpoint,
  #         "namespace" : var.metrics_namespace,
  #         "metrics" : var.metrics,
  #         "tags" : [
  #           "validator_address:${validator.address}",
  #           "validator_name:${validator.name}",
  #           "is_full_node:false",
  #         ],
  #         "max_returned_metrics" : var.max_returned_metrics
  #       }
  #     ]
  #   ),
  #   "com.datadoghq.ad.check_names" = jsonencode(
  #     [
  #       for validator in var.validators : "openmetrics"
  #     ]
  #   ),
  #   "com.datadoghq.ad.init_configs" = jsonencode(
  #     [
  #       for validator in var.validators : {}
  #     ]
  #   )
  # }
}
