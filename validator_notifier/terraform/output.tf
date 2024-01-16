output "lambda_endpoint" {
  value = aws_lambda_function_url.notify_validators_url.function_url
}
