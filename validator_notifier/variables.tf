variable "rsa_private_key" {
  type        = string
  description = "RSA private key in PEM format. It should start with: -----BEGIN PRIVATE KEY-----"
}

variable "recipients" {
  type        = string
  description = "Comma-separated list of recipient email addresses."
}
