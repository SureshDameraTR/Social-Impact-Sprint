# AWS MVP Deployment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deploy PashuRaksha ERP to a single EC2 t3.micro instance with Caddy reverse proxy, automatic HTTPS, and daily S3 backups — all managed by Terraform.

**Architecture:** Single EC2 instance in ap-south-1 (Mumbai). Caddy on the host serves static frontend builds and proxies API requests to docker-compose (FastAPI + PostgreSQL + mocks). GoDaddy DNS points subdomains at an Elastic IP. See `docs/plans/2026-04-27-aws-deployment-design.md` for full design.

**Tech Stack:** Terraform ~> 5.0 AWS provider, Ubuntu 24.04 EC2, Caddy 2, Docker Compose, PostgreSQL 16, FastAPI, Next.js (static export), Vite.

---

## Task 1: Modify Next.js Admin for Static Export

The admin app must produce static HTML/JS/CSS files instead of requiring a Node.js runtime. Currently it uses `output: "standalone"` and `dynamic = "force-dynamic"`.

**Files:**
- Modify: `packages/admin/next.config.js` (lines 6-7)
- Modify: `packages/admin/src/app/layout.tsx` (line 3)

**Step 1: Remove `dynamic = "force-dynamic"` from layout.tsx**

In `packages/admin/src/app/layout.tsx`, delete line 3:

```typescript
// DELETE this line:
export const dynamic = "force-dynamic";
```

The file should go from:
```typescript
import Providers from "./providers";

export const dynamic = "force-dynamic";

export const metadata = {
```

To:
```typescript
import Providers from "./providers";

export const metadata = {
```

**Step 2: Change next.config.js to static export**

In `packages/admin/next.config.js`, make these changes:

a) Change `output: "standalone"` to `output: "export"` (line 7)

b) Remove the `images` block (Next.js image optimizer is incompatible with static export — but the app doesn't use `next/image` so this is just cleanup)

c) Remove the `async headers()` function entirely (lines 12-43) — security headers will be served by Caddy in production. In dev, Next.js will serve without them (acceptable for local dev).

The file should become:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  transpilePackages: ["react-leaflet", "@react-leaflet/core", "leaflet"],
};

module.exports = nextConfig;
```

**Step 3: Verify the static export builds**

Run:
```bash
cd pashu-erp/packages/admin
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
pnpm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npx next build
```

Expected: Build succeeds and creates an `out/` directory with static HTML files.

Run:
```bash
ls out/
ls out/index.html
```

Expected: `index.html` exists along with `_next/` directory containing JS/CSS bundles.

**Step 4: Commit**

```bash
git add packages/admin/next.config.js packages/admin/src/app/layout.tsx
git commit -m "feat(admin): switch to static export for Caddy deployment"
```

---

## Task 2: Create Terraform Variables and Provider Config

**Files:**
- Create: `pashu-erp/infra/terraform/variables.tf`
- Create: `pashu-erp/infra/terraform/main.tf`
- Create: `pashu-erp/infra/terraform/terraform.tfvars.example`

**Step 1: Create the infra directory structure**

```bash
mkdir -p pashu-erp/infra/terraform
```

**Step 2: Create variables.tf**

Write `pashu-erp/infra/terraform/variables.tf`:

```hcl
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

variable "backup_bucket_name" {
  description = "S3 bucket name for database backups"
  type        = string
  default     = "pashuraksha-backups"
}
```

**Step 3: Create main.tf**

Write `pashu-erp/infra/terraform/main.tf`:

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

**Step 4: Create terraform.tfvars.example**

Write `pashu-erp/infra/terraform/terraform.tfvars.example`:

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

**Step 5: Commit**

```bash
git add pashu-erp/infra/terraform/variables.tf pashu-erp/infra/terraform/main.tf pashu-erp/infra/terraform/terraform.tfvars.example
git commit -m "feat(infra): add Terraform provider config and variables"
```

---

## Task 3: Create Terraform Network Resources

**Files:**
- Create: `pashu-erp/infra/terraform/network.tf`

**Step 1: Create network.tf**

Write `pashu-erp/infra/terraform/network.tf`:

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

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP (Caddy redirect)"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

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

**Step 2: Commit**

```bash
git add pashu-erp/infra/terraform/network.tf
git commit -m "feat(infra): add VPC, subnet, and security group"
```

---

## Task 4: Create Terraform Storage and IAM Resources

**Files:**
- Create: `pashu-erp/infra/terraform/storage.tf`

**Step 1: Create storage.tf**

Write `pashu-erp/infra/terraform/storage.tf`:

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

**Step 2: Commit**

```bash
git add pashu-erp/infra/terraform/storage.tf
git commit -m "feat(infra): add S3 backup bucket and EC2 IAM role"
```

---

## Task 5: Create Cloud-Init Template

This is the user data script that bootstraps the entire stack when the EC2 instance first boots.

**Files:**
- Create: `pashu-erp/infra/terraform/cloud-init.yml`

**Step 1: Create cloud-init.yml**

Write `pashu-erp/infra/terraform/cloud-init.yml`:

```yaml
#cloud-config

package_update: true
package_upgrade: true
packages:
  - docker.io
  - docker-compose-v2
  - curl
  - unzip
  - jq

groups:
  - docker
users:
  - default

runcmd:
  # Docker
  - usermod -aG docker ubuntu
  - systemctl enable docker
  - systemctl start docker

  # Caddy
  - curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy.gpg
  - echo 'deb [signed-by=/usr/share/keyrings/caddy.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main' > /etc/apt/sources.list.d/caddy.list
  - apt-get update
  - apt-get install -y caddy

  # Node.js 22 (build-time only)
  - curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  - apt-get install -y nodejs
  - npm install -g pnpm

  # AWS CLI v2
  - curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
  - unzip -q /tmp/awscliv2.zip -d /tmp
  - /tmp/aws/install
  - rm -rf /tmp/aws /tmp/awscliv2.zip

  # Directories
  - mkdir -p /opt/pashuraksha
  - mkdir -p /var/www/{admin,collection,vet}
  - mkdir -p /var/log/caddy
  - chown -R ubuntu:ubuntu /opt/pashuraksha /var/www

  # Clone repo
  - su - ubuntu -c "git clone ${github_repo} /opt/pashuraksha/repo"

  # Write .env
  - |
    cat > /opt/pashuraksha/repo/pashu-erp/.env << 'ENVEOF'
    POSTGRES_PASSWORD=${db_password}
    DATABASE_URL=postgresql+asyncpg://pashu:${db_password}@db:5432/pashuraksha
    JWT_SECRET=${jwt_secret}
    ENVIRONMENT=production
    CORS_ORIGINS=https://admin.${domain},https://collect.${domain},https://vet.${domain}
    WEATHER_API_URL=http://mock-backends:8001/api/weather
    BHARAT_PASHUDHAN_API_URL=http://mock-backends:8001/api/registry
    IOT_GATEWAY_URL=http://mock-backends:8001/api/iot
    STORAGE_API_URL=http://mock-backends:8001/api/storage
    ENVEOF
  - chmod 600 /opt/pashuraksha/repo/pashu-erp/.env
  - chown ubuntu:ubuntu /opt/pashuraksha/repo/pashu-erp/.env

  # Build admin (static export)
  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp/packages/admin && pnpm install && NEXT_PUBLIC_API_URL=https://api.${domain} npx next build"
  - cp -r /opt/pashuraksha/repo/pashu-erp/packages/admin/out/* /var/www/admin/

  # Build collection centre (Vite)
  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp/packages/collection && pnpm install && VITE_API_URL=https://api.${domain} npx vite build"
  - cp -r /opt/pashuraksha/repo/pashu-erp/packages/collection/dist/* /var/www/collection/

  # Build vet portal (Vite)
  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp/packages/vet && pnpm install && VITE_API_URL=https://api.${domain} npx vite build"
  - cp -r /opt/pashuraksha/repo/pashu-erp/packages/vet/dist/* /var/www/vet/

  # Start backend containers
  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp && docker compose up -d db mock-backends api"

  # Wait for DB + run migrations
  - sleep 20
  - su - ubuntu -c "cd /opt/pashuraksha/repo/pashu-erp && docker compose exec -T api alembic upgrade head"

  # Caddyfile
  - |
    cat > /etc/caddy/Caddyfile << 'CADDYEOF'
    api.${domain} {
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

    admin.${domain} {
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
            Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; img-src 'self' data: blob: https://*.tile.openstreetmap.org https://unpkg.com; font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; connect-src 'self' https://api.${domain}; frame-ancestors 'none'"
            -Server
        }
        log {
            output file /var/log/caddy/admin.log
            format json
        }
    }

    collect.${domain} {
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

    vet.${domain} {
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

    ${domain} {
        redir https://admin.${domain}{uri} permanent
    }

    www.${domain} {
        redir https://admin.${domain}{uri} permanent
    }
    CADDYEOF
  - systemctl restart caddy
  - systemctl enable caddy

  # Backup script
  - |
    cat > /opt/pashuraksha/backup.sh << 'BACKUPEOF'
    #!/bin/bash
    set -euo pipefail
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="/tmp/db-backups"
    S3_BUCKET="${backup_bucket}"
    mkdir -p "$BACKUP_DIR"
    docker exec pashu-erp-db-1 pg_dump -U pashu -d pashuraksha --format=custom --compress=9 > "$BACKUP_DIR/pashuraksha_$TIMESTAMP.dump"
    aws s3 cp "$BACKUP_DIR/pashuraksha_$TIMESTAMP.dump" "s3://$S3_BUCKET/daily/pashuraksha_$TIMESTAMP.dump"
    rm -f "$BACKUP_DIR/pashuraksha_$TIMESTAMP.dump"
    echo "[$(date)] Backup uploaded: s3://$S3_BUCKET/daily/pashuraksha_$TIMESTAMP.dump"
    BACKUPEOF
  - chmod +x /opt/pashuraksha/backup.sh
  - chown ubuntu:ubuntu /opt/pashuraksha/backup.sh

  # Daily backup cron — 2:30 AM IST = 21:00 UTC
  - echo "0 21 * * * ubuntu /opt/pashuraksha/backup.sh >> /var/log/backup.log 2>&1" > /etc/cron.d/db-backup
  - chmod 644 /etc/cron.d/db-backup

  # Deploy script
  - |
    cat > /opt/pashuraksha/deploy.sh << 'DEPLOYEOF'
    #!/bin/bash
    set -euo pipefail
    REPO_DIR="/opt/pashuraksha/repo"
    API_URL="https://api.${domain}"
    echo "=== Pulling latest code ==="
    cd "$REPO_DIR" && git pull origin main
    echo "=== Rebuilding admin ==="
    cd "$REPO_DIR/pashu-erp/packages/admin"
    pnpm install --frozen-lockfile
    NEXT_PUBLIC_API_URL=$API_URL npx next build
    cp -r out/* /var/www/admin/
    echo "=== Rebuilding collection ==="
    cd "$REPO_DIR/pashu-erp/packages/collection"
    pnpm install --frozen-lockfile
    VITE_API_URL=$API_URL npx vite build
    cp -r dist/* /var/www/collection/
    echo "=== Rebuilding vet ==="
    cd "$REPO_DIR/pashu-erp/packages/vet"
    pnpm install --frozen-lockfile
    VITE_API_URL=$API_URL npx vite build
    cp -r dist/* /var/www/vet/
    echo "=== Rebuilding API container ==="
    cd "$REPO_DIR/pashu-erp"
    docker compose up -d --build api
    echo "=== Running migrations ==="
    docker compose exec -T api alembic upgrade head
    echo "=== Done ==="
    echo "Verify: curl -s https://api.${domain}/health | jq"
    DEPLOYEOF
  - chmod +x /opt/pashuraksha/deploy.sh
  - chown ubuntu:ubuntu /opt/pashuraksha/deploy.sh
```

**Step 2: Commit**

```bash
git add pashu-erp/infra/terraform/cloud-init.yml
git commit -m "feat(infra): add cloud-init template for EC2 bootstrap"
```

---

## Task 6: Create Terraform Compute and Outputs

**Files:**
- Create: `pashu-erp/infra/terraform/compute.tf`
- Create: `pashu-erp/infra/terraform/outputs.tf`

**Step 1: Create compute.tf**

Write `pashu-erp/infra/terraform/compute.tf`:

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

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
    ignore_changes = [ami]
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

**Step 2: Create outputs.tf**

Write `pashu-erp/infra/terraform/outputs.tf`:

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

**Step 3: Commit**

```bash
git add pashu-erp/infra/terraform/compute.tf pashu-erp/infra/terraform/outputs.tf
git commit -m "feat(infra): add EC2 instance, Elastic IP, and outputs"
```

---

## Task 7: Add .gitignore for Terraform and Production Docker Compose Tweaks

**Files:**
- Create: `pashu-erp/infra/terraform/.gitignore`
- Modify: `pashu-erp/docker-compose.yml` (remove host port bindings for production safety)

**Step 1: Create Terraform .gitignore**

Write `pashu-erp/infra/terraform/.gitignore`:

```
.terraform/
*.tfstate
*.tfstate.backup
*.tfvars
!terraform.tfvars.example
.terraform.lock.hcl
```

**Step 2: Update docker-compose.yml to not expose DB on host**

In `pashu-erp/docker-compose.yml`, change the PostgreSQL port binding from exposing on localhost to only internal Docker network. Change line:

```yaml
    ports:
      - "127.0.0.1:5432:5432"
```

To:

```yaml
    ports:
      - "${DB_PORT:-127.0.0.1:5432}:5432"
```

This allows production to set `DB_PORT=5432` (internal only) while keeping local dev working as-is.

**NOTE:** Actually, the current binding `127.0.0.1:5432:5432` is already safe — it only exposes on localhost, not to the internet. The security group blocks port 5432 anyway. Leave docker-compose.yml as-is. No change needed.

**Step 3: Commit**

```bash
git add pashu-erp/infra/terraform/.gitignore
git commit -m "feat(infra): add Terraform gitignore"
```

---

## Task 8: Validate Terraform Config

**Step 1: Verify Terraform is installed**

```bash
terraform version
```

Expected: Terraform v1.5+ output.

If not installed:
```bash
# On Ubuntu/WSL:
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install terraform
```

**Step 2: Run terraform validate (syntax check only)**

Since we can't `terraform init` without AWS credentials, validate syntax:

```bash
cd pashu-erp/infra/terraform
terraform fmt -check -recursive
terraform validate
```

Note: `terraform validate` requires `terraform init` first. If no AWS credentials are configured, you can temporarily comment out the `backend "s3"` block and use local state for validation:

```bash
cd pashu-erp/infra/terraform
# Temporarily use local backend for validation
terraform init -backend=false
terraform validate
terraform fmt -recursive
```

Expected: `Success! The configuration is valid.`

**Step 3: Fix any formatting issues**

```bash
terraform fmt -recursive
```

**Step 4: Commit any formatting fixes**

```bash
git add -A pashu-erp/infra/terraform/
git commit -m "style(infra): terraform fmt"
```

---

## Task 9: Update CORS in FastAPI for Production Domains

The API needs to accept requests from the production subdomains.

**Files:**
- Verify: `pashu-erp/packages/api/app/main.py` (CORS config)
- Verify: `pashu-erp/packages/api/app/config.py` (CORS_ORIGINS env var)

**Step 1: Check current CORS config**

Read `packages/api/app/main.py` and find the CORS middleware setup. Also read `packages/api/app/config.py` to see how `CORS_ORIGINS` is consumed.

The docker-compose.yml already passes `CORS_ORIGINS` as an env var, and the cloud-init sets it to the production domains. Verify this is working correctly by checking that the FastAPI app reads `CORS_ORIGINS` from the environment and splits it into a list.

**Step 2: Verify no changes needed**

If `CORS_ORIGINS` is already read from env and split by comma, no code changes are needed — the cloud-init `.env` file handles it:

```
CORS_ORIGINS=https://admin.maxsocial.co.in,https://collect.maxsocial.co.in,https://vet.maxsocial.co.in
```

If the app hardcodes CORS origins, update it to read from `settings.cors_origins`.

---

## Task 10: Pre-Deployment Checklist (Manual Steps)

These steps require human action with AWS credentials:

**Step 1: Generate SSH key pair**

```bash
ssh-keygen -t ed25519 -f ~/.ssh/pashuraksha -C "pashuraksha-deployer"
```

**Step 2: Create Terraform state backend (one-time)**

```bash
# Create S3 bucket for TF state
aws s3api create-bucket \
  --bucket pashuraksha-tfstate \
  --region ap-south-1 \
  --create-bucket-configuration LocationConstraint=ap-south-1

aws s3api put-bucket-versioning \
  --bucket pashuraksha-tfstate \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name pashuraksha-tflock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-south-1
```

**Step 3: Create terraform.tfvars**

```bash
cd pashu-erp/infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with real values
```

**Step 4: Deploy**

```bash
cd pashu-erp/infra/terraform
terraform init
terraform plan
terraform apply
```

**Step 5: Configure GoDaddy DNS**

After `terraform apply` outputs the Elastic IP, go to GoDaddy DNS management for maxsocial.co.in and create 6 A records all pointing to the Elastic IP:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | <elastic_ip> | 600 |
| A | www | <elastic_ip> | 600 |
| A | api | <elastic_ip> | 600 |
| A | admin | <elastic_ip> | 600 |
| A | collect | <elastic_ip> | 600 |
| A | vet | <elastic_ip> | 600 |

**Step 6: Verify deployment**

Wait ~5-10 minutes for DNS propagation and cloud-init to complete, then:

```bash
# Check cloud-init status
ssh ubuntu@<elastic_ip> "cloud-init status --wait"

# Check services
ssh ubuntu@<elastic_ip> "cd /opt/pashuraksha/repo/pashu-erp && docker compose ps"

# Check API health
curl -s https://api.maxsocial.co.in/health | jq

# Check admin loads
curl -s -o /dev/null -w "%{http_code}" https://admin.maxsocial.co.in/

# Check collection loads
curl -s -o /dev/null -w "%{http_code}" https://collect.maxsocial.co.in/

# Check vet loads
curl -s -o /dev/null -w "%{http_code}" https://vet.maxsocial.co.in/
```

Expected: All return 200, API health returns JSON with status "ok".

---

## Summary

| Task | What | Files | Estimated Time |
|------|------|-------|----------------|
| 1 | Next.js static export | 2 modified | 5 min |
| 2 | TF variables + provider | 3 created | 3 min |
| 3 | TF network resources | 1 created | 3 min |
| 4 | TF storage + IAM | 1 created | 3 min |
| 5 | Cloud-init template | 1 created | 5 min |
| 6 | TF compute + outputs | 2 created | 3 min |
| 7 | TF gitignore | 1 created | 2 min |
| 8 | Validate TF config | 0 | 3 min |
| 9 | Verify CORS config | 0-1 | 3 min |
| 10 | Manual deployment | 0 | 15 min |
