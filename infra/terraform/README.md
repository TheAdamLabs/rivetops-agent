# infra/terraform

Terraform modules that deploy the full RivetOps agent stack **into your own cloud account**. This includes the Lambda function, EventBridge scheduler, and IAM execution role. Nothing runs on RivetOps infrastructure.

## Cloud providers

| Subfolder | Status |
|-----------|--------|
| [`aws/`](./aws/) | Available |
| [`azure/`](./azure/) | Coming soon |
| [`gcp/`](./gcp/) | Coming soon |

## What gets deployed (AWS)

- **Lambda function** — packages and runs `runtime/aws` + the specified plugin
- **EventBridge rule** — triggers Lambda on a schedule (default: every 5 minutes)
- **IAM execution role** — read-only access to your own account; no cross-account permissions

## Usage (AWS)

```hcl
module "rivetops" {
  source             = "github.com/TheAdamLabs/rivetops-agent//infra/terraform/aws"
  plugin_id          = "sre"
  dashboard_endpoint = "https://api.rivetops.pro"
  connection_token   = var.rivetops_token   # from rivetops.pro dashboard
}
```

Run `terraform apply`. That's it - the agent starts monitoring your account immediately.

## Security

- Lambda reads your own account data — no cross-account role, no credentials handed to RivetOps
- IAM execution role has `ReadOnlyAccess` scoped to your own account only
- Revoke access instantly by running `terraform destroy`
- All code is open source — review before you apply
