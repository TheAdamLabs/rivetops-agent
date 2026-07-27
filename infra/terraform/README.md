# infra/terraform

Terraform modules that create a read-only cross-account role in your cloud account. RivetOps assumes this role on a schedule to read telemetry — it never stores credentials and never writes to your infrastructure.

## Cloud providers

| Subfolder | Status | Output |
|-----------|--------|--------|
| [`aws/`](./aws/) | Available | `role_arn` |
| [`azure/`](./azure/) | Coming soon | `app_registration_id` |
| [`gcp/`](./gcp/) | Coming soon | `service_account_email` |

## Usage (AWS)

```hcl
module "rivetops" {
  source          = "rivetops/onboarding/aws"
  saas_account_id = "123456789012"   # RivetOps AWS account ID
}

output "role_arn" {
  value = module.rivetops.role_arn
}
```

Run `terraform apply`, copy the `role_arn` output, paste it into the RivetOps dashboard. That is the entire setup.

## Security

- Creates an IAM Role with `ReadOnlyAccess` only — no write permissions
- Trust policy restricts assumption to the RivetOps AWS account ID you provide
- Revoke access instantly by deleting the role
