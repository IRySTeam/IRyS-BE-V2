# Declaring main provider
provider "google" {
  project = "irys" # TODO: Change according to project name
  region  = "asia-southeast2"
}

# Declaring Terraform specific config
terraform {
  backend "gcs" {
    bucket = "tf-state" # TODO: Make sure bucket is created in project
    prefix = "terraform/state"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}