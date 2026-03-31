provider "azurerm" {
  features {}
  resource_provider_registrations = "none"
}

# Existing RG
data "azurerm_resource_group" "rg" {
  name = "20251229-PWC-Azure"
}

# Random
resource "random_integer" "rand" {
  min = 10000
  max = 99999
}

# ACR
resource "azurerm_container_registry" "acr" {
  name                = "langdetectoracr${random_integer.rand.result}"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = false

  tags = {
    owner = "Nadi"
  }
}

# 🔥 ADD THIS HERE ↓↓↓

# Container Apps Environment
resource "azurerm_container_app_environment" "env" {
  name                = "lang-detector-env"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  tags = {
    owner = "Nadi"
  }
}

# Container App
resource "azurerm_container_app" "app" {
  name                         = "lang-detector-app-${random_integer.rand.result}"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = data.azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "lang-detector"
      image  = "${azurerm_container_registry.acr.login_server}/lang-detector:v2"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "LANGUAGE_KEY"
        value = var.language_key
      }

      env {
        name  = "LANGUAGE_ENDPOINT"
        value = var.language_endpoint
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 5000

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  # ✅ REQUIRED
  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password"
  }

  # ✅ REQUIRED
  secret {
    name  = "acr-password"
    value = azurerm_container_registry.acr.admin_password
  }

  # ✅ FIXES BUG
  lifecycle {
    ignore_changes = [
      registry,
      secret
    ]
  }

  tags = {
    owner = "Nadi"
  }
}