variable "azure" {
  type = object({
    location = string
    credentials = object({
      client_id       = string
      client_secret   = string
      tenant_id       = string
      subscription_id = string
    })
  })
}

variable "auth" {
  type = object({
    tenant_id = string
  })
}

variable "resource_prefix" {
  type = object({
    project     = string
    environment = string
  })
  default = {
    project     = "fhirtasker"
    environment = "dev"
  }
}