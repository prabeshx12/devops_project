output "resource_group_name" {
  description = "Azure resource group name"
  value       = azurerm_resource_group.main.name
}

output "vm_public_ip" {
  description = "Public IP address of the Azure VM"
  value       = azurerm_public_ip.main.ip_address
}

output "app_url" {
  description = "InventoryOps application URL"
  value       = "http://${azurerm_public_ip.main.ip_address}:8000"
}

output "jenkins_url" {
  description = "Jenkins URL after Jenkins is installed"
  value       = "http://${azurerm_public_ip.main.ip_address}:8080"
}

output "prometheus_url" {
  description = "Prometheus URL"
  value       = "http://${azurerm_public_ip.main.ip_address}:9090"
}

output "grafana_url" {
  description = "Grafana URL"
  value       = "http://${azurerm_public_ip.main.ip_address}:3000"
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = azurerm_container_registry.app.login_server
}

output "acr_name" {
  description = "Azure Container Registry name"
  value       = azurerm_container_registry.app.name
}

