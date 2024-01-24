variable "recipients" {
  type        = string
  description = "Comma-separated list of recipient email addresses."
}

variable "codebuild_github_repo" {
  type        = string
  description = "URL of the source GitHub repository for AWS CodeBuild. It should end with '.git'."
}

variable "codebuild_github_branch" {
  type        = string
  description = "Repository branch that should be used by CodeBuild."
}
