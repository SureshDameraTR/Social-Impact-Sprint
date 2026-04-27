variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "volume_size" {
  description = "EBS root volume size in GB"
  type        = number
  default     = 20
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key for EC2 access"
  type        = string
}

variable "operator_ip" {
  description = "Your IP for SSH access (CIDR, e.g. 1.2.3.4/32)"
  type        = string
}

variable "domain" {
  description = "Root domain name"
  type        = string
  default     = "maxsocial.co.in"
}

variable "github_repo" {
  description = "GitHub repository URL"
  type        = string
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT signing secret"
  type        = string
  sensitive   = true
}

variable "subdomain_prefix" {
  description = "Prefix for subdomains (e.g. 'dev.' for dev.api.maxsocial.co.in, or '' for production)"
  type        = string
  default     = "dev."
}

variable "backup_bucket_name" {
  description = "S3 bucket name for database backups"
  type        = string
  default     = "pashuraksha-backups"
}
