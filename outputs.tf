output "app_server_ip" {
  description = "Public IP of the application server"
  value       = aws_instance.app_server.public_ip
}

output "app_server_id" {
  description = "ID of the application server instance"
  value       = aws_instance.app_server.id
}

output "db_endpoint" {
  description = "Endpoint of the RDS database"
  value       = aws_db_instance.db.endpoint
}

output "dynamodb_table_arn" {
  description = "The ARN of the DynamoDB table"
  value       = aws_dynamodb_table.meetings_table.arn
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.meetings_table.name
}