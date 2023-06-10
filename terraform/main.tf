terraform {
  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "=2.39.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.59.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }
  }
}

provider "azurerm" {
  features {}

  client_id       = var.azure.credentials.client_id
  client_secret   = var.azure.credentials.client_secret
  tenant_id       = var.azure.credentials.tenant_id
  subscription_id = var.azure.credentials.subscription_id
}

provider "azuread" {
  tenant_id = var.auth.tenant_id
}

locals {
  fhir_service = {
    name = "main"
  }
}

resource "azurerm_resource_group" "default" {
  name     = "${var.resource_prefix.project}-${var.resource_prefix.environment}"
  location = var.azure.location
}

# AUTHN/AUTHZ
resource "random_uuid" "app_role_uuid_smartUser" {}
resource "random_uuid" "app_role_uuid_globalAdmin" {}
resource "random_uuid" "app_role_uuid_globalWriter" {}
resource "random_uuid" "app_role_uuid_globalImporter" {}
resource "random_uuid" "app_role_uuid_globalConverter" {}
resource "random_uuid" "app_role_uuid_globalExporter" {}
resource "random_uuid" "app_role_uuid_globalReader" {}
resource "random_uuid" "oauth2_permission_scope_uuid_default" {}

data "azuread_client_config" "current" {}

resource "azuread_application" "postman_tf" {
  display_name    = "${var.resource_prefix.project}-${var.resource_prefix.environment}-postman"
  identifier_uris = ["api://${var.resource_prefix.project}-${var.resource_prefix.environment}-postman"]
  owners = [
    data.azuread_client_config.current.object_id
  ]

  api {
    oauth2_permission_scope {
      admin_consent_description  = "Allows access to FHIR API service"
      admin_consent_display_name = "FHIR API Default"
      type                       = "Admin"
      value                      = "default"
      id                         = random_uuid.oauth2_permission_scope_uuid_default.result
    }
  }

  public_client {
    redirect_uris = [
      "https://www.getpostman.com/oauth2/callback"
    ]
  }

  # Az Health Services FHIR Service App Roles
  app_role {
    display_name         = "smartUser"
    description          = "FHIR SMART User"
    allowed_member_types = ["User", "Application"]
    value                = "smartUser"
    id                   = random_uuid.app_role_uuid_smartUser.result
  }

  app_role {
    display_name         = "globalAdmin"
    description          = "FHIR Global Admin"
    allowed_member_types = ["User", "Application"]
    value                = "globalAdmin"
    id                   = random_uuid.app_role_uuid_globalAdmin.result
  }

  app_role {
    display_name         = "globalWriter"
    description          = "FHIR Global Writer"
    allowed_member_types = ["User", "Application"]
    value                = "globalWriter"
    id                   = random_uuid.app_role_uuid_globalWriter.result
  }

  app_role {
    display_name         = "globalImporter"
    description          = "FHIR Global Importer"
    allowed_member_types = ["User", "Application"]
    value                = "globalImporter"
    id                   = random_uuid.app_role_uuid_globalImporter.result
  }

  app_role {
    display_name         = "globalConverter"
    description          = "FHIR Global Converter"
    allowed_member_types = ["User", "Application"]
    value                = "globalConverter"
    id                   = random_uuid.app_role_uuid_globalConverter.result
  }

  app_role {
    display_name         = "globalExporter"
    description          = "FHIR Global Exporter"
    allowed_member_types = ["User", "Application"]
    value                = "globalExporter"
    id                   = random_uuid.app_role_uuid_globalExporter.result
  }

  app_role {
    display_name         = "globalReader"
    description          = "FHIR Global Reader"
    allowed_member_types = ["User", "Application"]
    value                = "globalReader"
    id                   = random_uuid.app_role_uuid_globalReader.result
  }
}

resource "azuread_application_password" "postman_client_secret" {
  application_object_id = azuread_application.postman_tf.object_id
  display_name          = "Client Secret"
}

resource "azuread_service_principal" "postman" {
  application_id = azuread_application.postman_tf.application_id
}

resource "azurerm_role_assignment" "postman_access" {
  scope                = azurerm_healthcare_fhir_service.default.id
  role_definition_name = "FHIR Data Contributor"
  principal_id         = azuread_service_principal.postman.id
}

# FHIR SERVICE
resource "azurerm_healthcare_workspace" "default" {
  name                = "${var.resource_prefix.project}${var.resource_prefix.environment}"
  location            = var.azure.location
  resource_group_name = azurerm_resource_group.default.name
}

resource "azurerm_healthcare_fhir_service" "default" {
  name                = local.fhir_service.name
  location            = var.azure.location
  resource_group_name = azurerm_resource_group.default.name
  workspace_id        = azurerm_healthcare_workspace.default.id
  kind                = "fhir-R4"

  authentication {
    authority = "https://login.microsoftonline.com/${var.auth.tenant_id}"
    audience  = "https://${azurerm_healthcare_workspace.default.name}-${local.fhir_service.name}.fhir.azurehealthcareapis.com"
  }
}