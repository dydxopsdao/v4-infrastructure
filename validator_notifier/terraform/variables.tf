variable "rsa_private_key" {
  type        = string
  description = "RSA private key in PEM format. It should start with: -----BEGIN PRIVATE KEY-----"
}

variable "recipients" {
  type        = string
  description = "Comma-separated list of recipient email addresses."
}

variable "authorization_token" {
  type        = string
  description = "A secret that has to be passed as bearer token."
}

variable "codebuild_github_repo" {
  type        = string
  description = "URL of the source GitHub repository for AWS CodeBuild. It should end with '.git'."
}

variable "codebuild_github_branch" {
  type        = string
  description = "Repository branch that should be used by CodeBuild."
}
