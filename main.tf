provider "aws" {
  region     = var.region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

# Security Group for the EC2 Instance
resource "aws_security_group" "app_sg" {
  name        = "app_sg"
  description = "Allow HTTP and SSH traffic"
  vpc_id      = var.vpc_id

  # Ingress rule to allow HTTP traffic on port 8081
  ingress {
    from_port   = 8081
    to_port     = 8081
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow HTTP traffic from anywhere
  }

  # Ingress rule to allow SSH traffic on port 22
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow SSH traffic from anywhere
  }

  # Egress rules to allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Reference the existing Internet Gateway
data "aws_internet_gateway" "existing_igw" {
  filter {
    name   = "attachment.vpc-id"
    values = [var.vpc_id]
  }
}

# Route Table for public subnets
resource "aws_route_table" "public_rt" {
  vpc_id = var.vpc_id

  # Route to allow internet access via the Internet Gateway
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = data.aws_internet_gateway.existing_igw.id
  }
}

# Associate the Route Table with the first subnet
resource "aws_route_table_association" "public_rt_assoc" {
  subnet_id      = var.subnet_ids[0]
  route_table_id = aws_route_table.public_rt.id
}

# DynamoDB Table for storing meetings
resource "aws_dynamodb_table" "meetings_table" {
  name           = "meetings_table"
  billing_mode   = "PROVISIONED" # Use provisioned capacity
  hash_key       = "id"

  # Define the primary key attribute
  attribute {
    name = "id"
    type = "S" # String type
  }

  read_capacity  = 5  # Set read capacity (within free tier limits)
  write_capacity = 5  # Set write capacity (within free tier limits)

  tags = {
    Environment = "Development"
    Name        = "MeetingsTable"
  }
}

# IAM Role for EC2 to access DynamoDB
resource "aws_iam_role" "ec2_dynamodb_role" {
  name = "ec2_dynamodb_role"

  # Trust policy to allow EC2 instances to assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Get the current AWS account ID
data "aws_caller_identity" "current" {}

# IAM Policy for DynamoDB Access
resource "aws_iam_policy" "dynamodb_access_policy" {
  name        = "dynamodb_access_policy"
  description = "Policy to allow EC2 to access DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem"
        ]
        Resource = "arn:aws:dynamodb:${var.region}:${data.aws_caller_identity.current.account_id}:table/meetings_table"
      }
    ]
  })
}

# Attach the Policy to the Role
resource "aws_iam_role_policy_attachment" "ec2_dynamodb_policy_attachment" {
  role       = aws_iam_role.ec2_dynamodb_role.name
  policy_arn = aws_iam_policy.dynamodb_access_policy.arn
}

# Create an Instance Profile for the IAM Role
resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2_instance_profile"
  role = aws_iam_role.ec2_dynamodb_role.name
}

####RDS MySQL Database Configuration, not used anymore####

# Security Group for the RDS Database
resource "aws_security_group" "db_sg" {
  name        = "db_sg"
  description = "Allow MySQL traffic"
  vpc_id      = var.vpc_id

  # Ingress rules for MySQL traffic
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id] # Allow traffic from the EC2 instance's security group
    cidr_blocks     = var.subnet_cidrs # Allow traffic from the subnets
  }

  # Egress rules to allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS Database Instance
resource "aws_db_instance" "db" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  db_name              = var.db_name
  username             = var.db_username
  password             = var.db_password
  publicly_accessible  = true
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  skip_final_snapshot  = true
  db_subnet_group_name = aws_db_subnet_group.db_subnet_group.name
}

# Subnet Group for RDS
resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "db-subnet-group"
  subnet_ids = var.subnet_ids
}

# EC2 Instance for the Application
resource "aws_instance" "app_server" {
  ami                  = var.ami_id
  instance_type        = var.instance_type
  subnet_id            = var.subnet_ids[0] # Use the first subnet
  security_groups      = [aws_security_group.app_sg.id]
  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name

  # User data script to install Python, deploy main.py, and run the application
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y python3 git
              yum install -y python3-pip
              yum install -y mysql
              yum install -y httpd.x86_64
              systemctl start httpd.service
              systemctl enable httpd.service
          
              # Create the application directory
              mkdir -p /home/ec2-user/app
              chmod 777 /home/ec2-user/app

              # Copy the main.py file to the application directory
              git clone https://github.com/vasilebelmega/Python.git /home/ec2-user/app
              chmod 777 /home/ec2-user/app/main.py

              # Install Python dependencies from requirements.txt
              pip3 install -r /home/ec2-user/app/requirements.txt

              # Run the Python application
              python3 /home/ec2-user/app/main.py &
              EOF

  tags = {
    Name = "AppServer"
  }
}