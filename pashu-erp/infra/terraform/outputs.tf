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
    "@"                              = aws_eip.app.public_ip
    "www"                            = aws_eip.app.public_ip
    "${var.subdomain_prefix}api"     = aws_eip.app.public_ip
    "${var.subdomain_prefix}admin"   = aws_eip.app.public_ip
    "${var.subdomain_prefix}collect" = aws_eip.app.public_ip
    "${var.subdomain_prefix}vet"     = aws_eip.app.public_ip
  }
}

output "urls" {
  description = "Service URLs (available after DNS propagation)"
  value = {
    api        = "https://${var.subdomain_prefix}api.${var.domain}"
    admin      = "https://${var.subdomain_prefix}admin.${var.domain}"
    collection = "https://${var.subdomain_prefix}collect.${var.domain}"
    vet        = "https://${var.subdomain_prefix}vet.${var.domain}"
  }
}

output "backup_bucket" {
  description = "S3 bucket for database backups"
  value       = aws_s3_bucket.backups.id
}
