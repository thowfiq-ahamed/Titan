# HashiCorp Vault Policy: TITAN Workload Access Control
# Restricts secret read permissions strictly to application paths

path "secret/data/titan/inventory-api/*" {
  capabilities = ["read"]
}

path "secret/data/titan/platform-api/*" {
  capabilities = ["read"]
}

# Deny root and administrative engine mutations
path "sys/*" {
  capabilities = ["deny"]
}
