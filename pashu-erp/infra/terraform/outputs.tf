output "elastic_ip" {
  description = "Public IP — point GoDaddy DNS A records here"
  value       = aws_eip.app.public_ip
}

output "ssh_command" {
  description = "SSH into the instance"
  value       = "ssh ubuntu@${aws_eip.app.public_ip}"
}

output "dns_records" {
  description = "A records to create in GoDaddy"
  value = {
    "@"       = aws_eip.app.public_ip
    "www"     = aws_eip.app.public_ip
    "api"     = aws_eip.app.public_ip
    "admin"   = aws_eip.app.public_ip
    "collect" = aws_eip.app.public_ip
    "vet"     = aws_eip.app.public_ip
  }
}

output "urls" {
  description = "Service URLs (available after DNS propagation)"
  value = {
    api        = "https://api.${var.domain}"
    admin      = "https://admin.${var.domain}"
    collection = "https://collect.${var.domain}"
    vet        = "https://vet.${var.domain}"
  }
}

output "backup_bucket" {
  description = "S3 bucket for database backups"
  value       = aws_s3_bucket.backups.id
}
