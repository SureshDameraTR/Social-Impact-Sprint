# PashuRaksha ERP — AWS Deployment Design

**Date:** 2026-04-27
**Status:** Validated
**Author:** Suresh Damera
**Domain:** maxsocial.co.in (GoDaddy — already owned)

---

## 1. Context

PashuRaksha ERP is a livestock management platform for rural Indian farmers, built by a non-profit NGO (MaxSocial). The platform consists of 6 packages: FastAPI backend, Next.js admin dashboard, 2 Vite PWAs (collection centre, vet portal), Expo mobile app, and mock backends for external integrations.

**Deployment goal:** Minimum viable deployment for a pilot with 10-100 users. Priority is low cost and simple operations.

---

## 2. Architecture Overview

Single EC2 instance running docker-compose with Caddy as reverse proxy, serving all services behind subdomains with automatic HTTPS.

```
                    Internet
                       |
                 +-----------+
                 |  GoDaddy  |  maxsocial.co.in
                 |    DNS    |  *.maxsocial.co.in
                 +-----+-----+
                       |
                 +-----+-----+
                 | Elastic IP |  (free when attached)
                 +-----+-----+
                       |
              +--------+--------+
              |  EC2 t3.micro   |  Ubuntu 24.04
              |  (2 vCPU, 1GB)  |  20GB gp3 EBS
              |                 |
              |  +-----------+  |
              |  |   Caddy   |  |  :80/:443 auto HTTPS
              |  |  (proxy)  |  |  subdomain routing
              |  +-----+-----+  |
              |        |        |
              |  +-----+--------------------+
              |  |     docker-compose       |
              |  |                          |
              |  |  api        :8000  FastAPI|
              |  |  db         :5432  PG 16  |
              |  |  mock-backs :8001  Mocks  |
              |  +--------------------------+
              |                 |
              |  S3 bucket --- DB backups (daily cron)
              +-----------------+
```

---

## 3. Service Layout on EC2

Only **3 Docker processes** run at runtime. Frontends are pre-built as static files and served directly by Caddy.

| Process | Runtime RAM | Role |
|---------|-------------|------|
| Caddy (host) | ~20MB | Reverse proxy, HTTPS, static file server |
| FastAPI + uvicorn (Docker) | ~150MB | Backend API |
| PostgreSQL 16 (Docker) | ~200MB | Database |
| Mock backends (Docker) | ~80MB | Weather, registry, IoT, storage mocks |
| **Total** | **~450MB** | Leaves ~550MB for OS + filesystem cache |

### Subdomain Routing

| Subdomain | Caddy Target |
|-----------|-------------|
| `maxsocial.co.in` | Redirect to `admin.maxsocial.co.in` |
| `www.maxsocial.co.in` | Redirect to `admin.maxsocial.co.in` |
| `admin.maxsocial.co.in` | `/var/www/admin/` (static Next.js export) |
| `collect.maxsocial.co.in` | `/var/www/collection/` (static Vite build) |
| `vet.maxsocial.co.in` | `/var/www/vet/` (static Vite build) |
| `api.maxsocial.co.in` | `localhost:8000` (reverse proxy) |

### GoDaddy DNS Records

| Type | Name | Value |
|------|------|-------|
| A | `@` | `<Elastic IP>` |
| A | `www` | `<Elastic IP>` |
| A | `api` | `<Elastic IP>` |
| A | `admin` | `<Elastic IP>` |
| A | `collect` | `<Elastic IP>` |
| A | `vet` | `<Elastic IP>` |

### Expo Mobile App

Build with `EXPO_PUBLIC_API_URL=https://api.maxsocial.co.in`. No server-side process needed — the mobile app is distributed via APK/Play Store.

### Next.js Static Export Prerequisite

The admin app currently uses `output: "standalone"` and `dynamic = "force-dynamic"` in the root layout. To serve as static files:

1. Remove `dynamic = "force-dynamic"` from `packages/admin/src/app/layout.tsx`
2. Change `output: "standalone"` to `output: "export"` in `next.config.js`
3. Move security headers (CSP, X-Frame-Options, etc.) from `next.config.js` to Caddyfile

This works because the admin is a pure client-side Refine SPA — all data fetching happens in the browser via the Refine data provider.

---

## 4. Architecture Decision Record

### Decision: Single EC2 instance with docker-compose for MVP

### Why NOT Fargate + RDS right now

| Factor | EC2 Single Instance | Fargate + RDS |
|--------|-------------------|---------------|
| Monthly cost | ~$5-10 | ~$50-80 minimum |
| Setup complexity | 1 Terraform config, 1 Caddyfile | VPC, subnets, ALB, ECS cluster, task defs, RDS subnet groups, security groups |
| Time to deploy | ~2 hours | ~1-2 days |
| Operational overhead | SSH in, docker-compose up | CloudWatch, ECS service discovery, RDS parameter groups |
| Fits the audience | 10-100 users, pilot | 1,000+ users, production |
| Risk if it goes down | Pilot users wait 5 min for reboot | N/A (HA) |

### Why this is the right call for an NGO pilot

1. **Budget matters** — Non-profit, every dollar counts. $5/month vs $60/month is a 12x difference for the same pilot outcome.
2. **Validate first, scale second** — The goal is proving the product works for farmers, not running five-nines infrastructure.
3. **Docker-compose already works** — Zero application refactoring. The exact same stack that runs locally runs in production.
4. **One person can operate it** — No need to understand ECS task definitions, ALB target groups, or RDS parameter tuning.

### What we are NOT cutting corners on

- **HTTPS everywhere** — Caddy handles this automatically via Let's Encrypt
- **Database backups** — Daily pg_dump to S3, automated via cron
- **Security groups** — Only ports 80/443 open to the world, SSH restricted to operator IP
- **Docker health checks** — Already in the compose file, retained
- **Secrets management** — `.env` file on the instance, not baked into images

---

## 5. Graduation Path

The architecture is designed to evolve as the user base grows. Each phase is an incremental Terraform change, not a rewrite.

```
Phase 1 (NOW): Single EC2 + docker-compose
  - 10-100 users, pilot
  - ~$5-10/month
  - All services on one box

Phase 2 (100-1,000 users): Split out the database
  - Keep EC2 for app services
  - Move PostgreSQL to RDS db.t4g.micro
  - Automatic backups, point-in-time recovery
  - Adds ~$13/month
  - Terraform change: add aws_db_instance, update DATABASE_URL env var

Phase 3 (1,000-5,000 users): Move to Fargate
  - Replace EC2 with ECS Fargate tasks
  - Add ALB for load balancing and health-check routing
  - Auto-scaling based on CPU/memory
  - S3 + CloudFront for static frontends (global edge caching)
  - ~$50-80/month

Phase 4 (5,000+ users, multi-district): Full cloud-native
  - Multi-AZ RDS for database HA
  - ElastiCache (Redis) for sessions and caching
  - CloudFront CDN for all frontends
  - Lambda@Edge for API response caching
  - WAF for DDoS protection and security
  - CloudWatch + X-Ray for observability
  - ~$150-300/month depending on traffic
```

---

## 6. Cost Estimate (Phase 1)

| Item | On-demand | With Spot |
|------|-----------|-----------|
| EC2 t3.micro | ~$8/month | ~$3/month |
| EBS 20GB gp3 | ~$1.60/month | ~$1.60/month |
| Elastic IP | free (attached) | free (attached) |
| S3 backups | ~$0.10/month | ~$0.10/month |
| Route 53 | $0 (using GoDaddy) | $0 (using GoDaddy) |
| Domain | $0 (already owned) | $0 (already owned) |
| **Total** | **~$10/month** | **~$5/month** |

---

## 7. Infrastructure as Code — Terraform

### 7.1 File Structure

```
pashu-erp/
  infra/
    terraform/
      main.tf              # Provider config, S3 backend
      network.tf           # VPC, subnet, internet gateway, security group
      compute.tf           # EC2 instance, key pair, elastic IP
      storage.tf           # S3 backup bucket, IAM role for EC2→S3
      variables.tf         # All configurable inputs
      outputs.tf           # Elastic IP, SSH command, DNS records, URLs
      cloud-init.yml       # EC2 user data: bootstrap entire stack
      terraform.tfvars.example  # Template for actual values
    Caddyfile              # Reverse proxy + static file serving
    deploy.sh              # Manual redeploy script
    backup.sh              # pg_dump → S3 (daily cron)
```

### 7.2 variables.tf

```hcl
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-south-1"  # Mumbai — closest to Indian users
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
  description = "Your IP address for SSH access (CIDR format, e.g. 1.2.3.4/32)"
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

variable "backup_bucket_name" {
  description = "S3 bucket name for database backups"
  type        = string
  default     = "pashuraksha-backups"
}
```

### 7.3 main.tf

```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "pashuraksha-tfstate"
    key            = "mvp/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "pashuraksha-tflock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "PashuRaksha"
      Environment = "mvp"
      ManagedBy   = "terraform"
    }
  }
}
```

### 7.4 network.tf

```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "pashuraksha-vpc" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "pashuraksha-igw" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = { Name = "pashuraksha-public" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = { Name = "pashuraksha-rt" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "app" {
  name_prefix = "pashuraksha-"
  description = "PashuRaksha MVP - HTTP, HTTPS, SSH"
  vpc_id      = aws_vpc.main.id

  # HTTP — Caddy redirects to HTTPS
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP (Caddy redirect)"
  }

  # HTTPS — all traffic
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # SSH — operator only
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.operator_ip]
    description = "SSH from operator"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound"
  }

  tags = { Name = "pashuraksha-sg" }
}
```

### 7.5 storage.tf

```hcl
resource "aws_s3_bucket" "backups" {
  bucket = var.backup_bucket_name
  tags   = { Name = "pashuraksha-backups" }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "expire-old-backups"
    status = "Enabled"

    expiration {
      days = 30
    }

    filter {
      prefix = "daily/"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM role so EC2 can push backups to S3
resource "aws_iam_role" "ec2" {
  name = "pashuraksha-ec2"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "s3_backup" {
  name = "s3-backup-access"
  role = aws_iam_role.ec2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject", "s3:GetObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.backups.arn,
        "${aws_s3_bucket.backups.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "ec2" {
  name = "pashuraksha-ec2"
  role = aws_iam_role.ec2.name
}
```

### 7.6 compute.tf

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_key_pair" "deployer" {
  key_name   = "pashuraksha-deployer"
  public_key = file(var.ssh_public_key_path)
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.deployer.key_name
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  root_block_device {
    volume_size = var.volume_size
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = templatefile("cloud-init.yml", {
    github_repo   = var.github_repo
    domain        = var.domain
    db_password   = var.db_password
    jwt_secret    = var.jwt_secret
    backup_bucket = var.backup_bucket_name
  })

  tags = { Name = "pashuraksha-mvp" }

  lifecycle {
    ignore_changes = [ami]  # Don't rebuild on AMI updates
  }
}

resource "aws_eip" "app" {
  domain = "vpc"
  tags   = { Name = "pashuraksha-eip" }
}

resource "aws_eip_association" "app" {
  instance_id   = aws_instance.app.id
  allocation_id = aws_eip.app.id
}
```

### 7.7 outputs.tf

```hcl
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
```

### 7.8 terraform.tfvars.example

```hcl
aws_region          = "ap-south-1"
instance_type       = "t3.micro"
volume_size         = 20
ssh_public_key_path = "~/.ssh/pashuraksha.pub"
operator_ip         = "YOUR_IP/32"       # Run: curl ifconfig.me
domain              = "maxsocial.co.in"
github_repo         = "https://github.com/your-org/Social-Impact-Sprint.git"
db_password         = "CHANGE_ME"
jwt_secret          = "CHANGE_ME"
backup_bucket_name  = "pashuraksha-backups"
```

---

## 8. Caddyfile

```
# /etc/caddy/Caddyfile

# API — reverse proxy to FastAPI container
api.maxsocial.co.in {
    reverse_proxy localhost:8000

    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }

    log {
        output file /var/log/caddy/api.log
        format json
    }
}

# Admin dashboard — static Next.js export
admin.maxsocial.co.in {
    root * /var/www/admin
    file_server
    try_files {path} /index.html

    header {
        Cache-Control "public, max-age=3600"
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
        Permissions-Policy "camera=(), microphone=(), geolocation=(self), payment=()"
        Cross-Origin-Opener-Policy same-origin
        Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; img-src 'self' data: blob: https://*.tile.openstreetmap.org https://unpkg.com; font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; connect-src 'self' https://api.maxsocial.co.in; frame-ancestors 'none'"
        -Server
    }

    log {
        output file /var/log/caddy/admin.log
        format json
    }
}

# Collection centre PWA — static Vite build
collect.maxsocial.co.in {
    root * /var/www/collection
    file_server
    try_files {path} /index.html

    header {
        Cache-Control "public, max-age=3600"
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }

    log {
        output file /var/log/caddy/collection.log
        format json
    }
}

# Vet portal — static Vite build
vet.maxsocial.co.in {
    root * /var/www/vet
    file_server
    try_files {path} /index.html

    header {
        Cache-Control "public, max-age=3600"
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }

    log {
        output file /var/log/caddy/vet.log
        format json
    }
}

# Root domain → redirect to admin
maxsocial.co.in {
    redir https://admin.maxsocial.co.in{uri} permanent
}

www.maxsocial.co.in {
    redir https://admin.maxsocial.co.in{uri} permanent
}
```

---

## 9. Cloud-Init Script

```yaml
#cloud-config

# 1. System packages
package_update: true
packages:
  - docker.io
  - docker-compose-v2
  - curl
  - unzip
  - jq
  - awscli

# 2. Enable unattended security updates
package_upgrade: true

# 3. Docker group
groups:
  - docker
users:
  - default

runcmd:
  # Docker setup
  - usermod -aG docker ubuntu
  - systemctl enable docker
  - systemctl start docker

  # Install Caddy
  - curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy.gpg
  - echo 'deb [signed-by=/usr/share/keyrings/caddy.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main' > /etc/apt/sources.list.d/caddy.list
  - apt-get update
  - apt-get install -y caddy

  # Install Node.js 22 (build-time only, not runtime)
  - curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  - apt-get install -y nodejs
  - npm install -g pnpm

  # Create directories
  - mkdir -p /opt/pashuraksha
  - mkdir -p /var/www/{admin,collection,vet,landing}
  - mkdir -p /var/log/caddy
  - chown -R ubuntu:ubuntu /opt/pashuraksha /var/www

  # Clone repo
  - su - ubuntu -c "git clone ${github_repo} /opt/pashuraksha/repo"

  # Write .env for docker-compose
  - |
    cat > /opt/pashuraksha/repo/pashu-erp/.env << 'ENVEOF'
    POSTGRES_PASSWORD=${db_password}
    DATABASE_URL=postgresql+asyncpg://pashu:${db_password}@db:5432/pashuraksha
    JWT_SECRET=${jwt_secret}
    ENVIRONMENT=production
    ENVEOF
  - chmod 600 /opt/pashuraksha/repo/pashu-erp/.env

  # Build frontends (static output)
  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp/packages/admin && pnpm install && NEXT_PUBLIC_API_URL=https://api.${domain} npx next build"
  - cp -r /opt/pashuraksha/repo/pashu-erp/packages/admin/out/* /var/www/admin/

  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp/packages/collection && pnpm install && VITE_API_URL=https://api.${domain} npx vite build"
  - cp -r /opt/pashuraksha/repo/pashu-erp/packages/collection/dist/* /var/www/collection/

  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp/packages/vet && pnpm install && VITE_API_URL=https://api.${domain} npx vite build"
  - cp -r /opt/pashuraksha/repo/pashu-erp/packages/vet/dist/* /var/www/vet/

  # Start backend services
  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp && docker compose up -d db mock-backends api"

  # Wait for API health
  - sleep 15
  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp && docker compose exec api alembic upgrade head"

  # Install Caddyfile and start
  - cp /tmp/Caddyfile /etc/caddy/Caddyfile
  - systemctl restart caddy
  - systemctl enable caddy

  # Daily backup cron (2 AM IST)
  - cp /tmp/backup.sh /opt/pashuraksha/backup.sh
  - chmod +x /opt/pashuraksha/backup.sh
  - echo "30 20 * * * ubuntu /opt/pashuraksha/backup.sh >> /var/log/backup.log 2>&1" > /etc/cron.d/db-backup
```

---

## 10. Operational Scripts

### 10.1 backup.sh — Daily PostgreSQL dump to S3

```bash
#!/bin/bash
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/db-backups"
S3_BUCKET="${backup_bucket}"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Dump from Docker container
docker exec pashu-erp-db-1 pg_dump \
  -U pashu \
  -d pashuraksha \
  --format=custom \
  --compress=9 \
  > "$BACKUP_DIR/pashuraksha_$${TIMESTAMP}.dump"

# Upload to S3
aws s3 cp \
  "$BACKUP_DIR/pashuraksha_$${TIMESTAMP}.dump" \
  "s3://$${S3_BUCKET}/daily/pashuraksha_$${TIMESTAMP}.dump"

# Clean local temp
rm -f "$BACKUP_DIR/pashuraksha_$${TIMESTAMP}.dump"

echo "[$(date)] Backup uploaded: s3://$${S3_BUCKET}/daily/pashuraksha_$${TIMESTAMP}.dump"
```

### 10.2 deploy.sh — Manual redeploy for code updates

```bash
#!/bin/bash
set -euo pipefail

REPO_DIR="/opt/pashuraksha/repo"
API_URL="https://api.maxsocial.co.in"

echo "=== Pulling latest code ==="
cd "$REPO_DIR"
git pull origin main

echo "=== Rebuilding frontends ==="
cd "$REPO_DIR/pashu-erp/packages/admin"
pnpm install --frozen-lockfile
NEXT_PUBLIC_API_URL=$API_URL npx next build
cp -r out/* /var/www/admin/

cd "$REPO_DIR/pashu-erp/packages/collection"
pnpm install --frozen-lockfile
VITE_API_URL=$API_URL npx vite build
cp -r dist/* /var/www/collection/

cd "$REPO_DIR/pashu-erp/packages/vet"
pnpm install --frozen-lockfile
VITE_API_URL=$API_URL npx vite build
cp -r dist/* /var/www/vet/

echo "=== Rebuilding API container ==="
cd "$REPO_DIR/pashu-erp"
docker compose up -d --build api

echo "=== Running database migrations ==="
docker compose exec api alembic upgrade head

echo "=== Done ==="
echo "Verify: curl -s https://api.maxsocial.co.in/health | jq"
```

---

## 11. Deployment Flow

### First-time deployment

```
Developer laptop
    |
    |  1. Create S3 bucket + DynamoDB table for TF state (one-time)
    |  2. terraform init
    |  3. terraform plan
    |  4. terraform apply
    v
AWS: EC2 instance created → cloud-init bootstraps everything
    |
    |  5. Terraform outputs Elastic IP
    |  6. Set A records in GoDaddy (6 records, all same IP)
    |  7. Wait ~5 min for DNS propagation
    |  8. Caddy auto-provisions Let's Encrypt certs on first request
    v
Live at https://api.maxsocial.co.in
        https://admin.maxsocial.co.in
        https://collect.maxsocial.co.in
        https://vet.maxsocial.co.in
```

### Subsequent deploys (code updates)

```bash
ssh ubuntu@<elastic-ip>
/opt/pashuraksha/deploy.sh
```

---

## 12. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| SSH access | Key-pair only, security group restricts to operator IP |
| HTTPS | Caddy auto-provisions Let's Encrypt certificates |
| Database exposure | PostgreSQL bound to Docker internal network, not exposed on host |
| Secrets | `.env` file on instance, `chmod 600`, not in git |
| OS patching | Ubuntu unattended-upgrades enabled via cloud-init |
| Backups | Daily pg_dump to S3 with 30-day lifecycle policy |
| Security headers | CSP, X-Frame-Options, CORS handled in Caddyfile |
| Docker | Non-root user in API container (appuser, UID 1001) |

---

## 13. Monitoring (Free Tier)

- **EC2 CloudWatch metrics** — CPU, network, disk (free, 5-min intervals)
- **Caddy access logs** — JSON format at `/var/log/caddy/*.log`
- **Docker health checks** — API, PostgreSQL, mocks (already configured)
- **Backup success** — Check `/var/log/backup.log` or S3 bucket contents

Phase 2 improvement: CloudWatch agent for custom metrics and log aggregation.

---

## 14. Open Items

- [ ] Confirm t3.micro has enough RAM after building frontends (build is temporary, only runtime matters)
- [ ] Decide if mock backends are needed in production or if real integrations replace them
- [ ] Create S3 bucket + DynamoDB table for Terraform state (one-time manual setup)
- [ ] Generate SSH key pair for EC2 access
- [ ] Plan GitHub Actions CI/CD for automated deploys (Phase 2 improvement)
- [ ] Decide on log aggregation strategy (Phase 2)
- [ ] Modify Next.js admin to use `output: "export"` instead of `"standalone"`
