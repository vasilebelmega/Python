variable "region" {
  description = "AWS region to deploy resources"
  default     = "eu-north-1"
}

variable "aws_access_key" {
    description = "AWS access key"
    default     = "AKIASTTKJXC7KGZQHQFK"
}

variable "aws_secret_key" {
  description = "AWS secret key"
  default     = "8qD3ZiV917b3pKGFhJ2NtX0zOYSmVKsjscmirA27"
}

variable "vpc_id" {
  description = "VPC ID for the existing VPC"
  default     = "vpc-0c03bcdf4e86d1b23"
}

variable "vpc_cidr" {
  description = "CIDR block for the existing VPC"
  default     = "172.31.0.0/16"
}

variable "subnet_ids" {
  description = "List of subnet IDs for the existing subnets"
  default     = ["subnet-023db39fc26875cee", "subnet-074d13a7c1a1cbc3e", "subnet-039ac87236bcb602f"]
}

variable "subnet_cidrs" {
  description = "List of CIDR blocks for the existing subnets"
  default     = ["172.31.16.0/20", "172.31.0.0/20", "172.31.32.0/20"]
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  default     = "ami-0274f4b62b6ae3bd5" 
}

variable "instance_type" {
  description = "Instance type for the EC2 instance"
  default     = "t3.micro"
}
variable "db_name" {
  description = "Name of the database"
  default     = "meetings_db" 
}

variable "db_username" {
  description = "Database username"
  default     = "admin"
}

variable "db_password" {
  description = "Database password"
  default     = "dummypass" # Replace with a secure password
}