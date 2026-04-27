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
