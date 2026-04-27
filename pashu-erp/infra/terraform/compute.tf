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
