output "postman_client_secret" {
  value     = azuread_application_password.postman_client_secret.value
  sensitive = true
}

output "postman_client_id" {
  value = azuread_application.postman_tf.application_id
}