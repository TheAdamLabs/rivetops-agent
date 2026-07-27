# infra/terraform

Terraform modules that deploy the full RivetOps agent stack **into your own cloud account**. This includes the Lambda function, EventBridge scheduler, cloud-native notification topic, and IAM execution role. Nothing runs on RivetOps infrastructure.

## Cloud providers

| Subfolder | Status | Notification service |
|-----------|--------|----------------------|
| [`aws/`](./aws/) | Available | SNS |
| [`azure/`](./azure/) | Coming soon | Event Grid |
| [`gcp/`](./gcp/) | Coming soon | Pub/Sub |

## What gets deployed (AWS)

- **Lambda function** — packages and runs `runtime/aws` + the specified plugin
- **EventBridge rule** — triggers Lambda on a schedule (default: every 5 minutes)
- **SNS topic** — receives structured findings; you subscribe Slack, PagerDuty, email, or any HTTPS endpoint
- **IAM execution role** — read-only access to your own account; no cross-account permissions

## Usage (AWS)

```hcl
module "rivetops" {
  source          = "github.com/TheAdamLabs/rivetops-agent//infra/terraform/aws"
  plugin_id       = "sre"
  sns_subscribers = ["https://hooks.slack.com/..."]   # one or more HTTPS endpoints

  # Optional: connect to the RivetOps managed dashboard
  dashboard_endpoint = "https://api.rivetops.pro"
  connection_token   = var.rivetops_token
}
```

```bash
terraform apply
# Findings arrive in Slack within minutes
```

## Security

- Lambda reads your own account data — no cross-account role, no credentials handed to RivetOps
- IAM execution role has `ReadOnlyAccess` scoped to your own account only
- SNS topic is private — subscribers are HTTPS endpoints or email addresses you control
- Revoke access instantly by running `terraform destroy`
- All code is open source — review before you apply
