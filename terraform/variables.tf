variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "inventoryops"
}

variable "azure_location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "vm_size" {
  description = "Azure VM size"
  type        = string
  default     = "Standard_DS1_v2"
}

variable "admin_username" {
  description = "Admin username for the Azure Linux VM"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key" {
  description = "SSH public key used to access the Azure VM"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to access SSH, Jenkins, Prometheus, and Grafana"
  type        = string
}

