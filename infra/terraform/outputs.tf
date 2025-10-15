output "ecr_backend_uri" {
  description = "ECR repository URI for backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_uri" {
  description = "ECR repository URI for frontend"
  value       = aws_ecr_repository.frontend.repository_url
}
