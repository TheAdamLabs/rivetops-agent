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
- **SNS topic** — receives findings on state transitions only (new, re-alert, resolved); you subscribe your own endpoints
- **DynamoDB table** — finding state store for deduplication; on-demand billing, TTL-managed, negligible cost
- **IAM execution role** — read-only access to your own account + `sns:Publish` + scoped DynamoDB access

## Usage (AWS)

```hcl
module "rivetops" {
  source                   = "github.com/TheAdamLabs/rivetops-agent//infra/terraform/aws"
  plugin_id                = "sre"
  suppression_window_hours = 4    # how long to suppress re-alerts for the same finding

  # Injected as additional system prompt on every agent run
  custom_instructions = <<-EOT
    Focus on our EKS clusters: prod-cluster, staging-cluster (us-east-1).
    Ignore CPU spikes on instances tagged Role=batch-worker - expected behavior.
    For any RDS finding, include the current replica lag from CloudWatch.
  EOT

  # Pi packages bundled into the Lambda at deploy time (from https://pi.dev/packages or private registry)
  # extra_plugins = ["@your-org/custom-runbook-skill"]

  # Optional: connect to the RivetOps managed dashboard
  dashboard_endpoint = "https://api.rivetops.pro"
  connection_token   = var.rivetops_token
}

output "findings_topic_arn" {
  value = module.rivetops.findings_topic_arn
}
```

```bash
terraform apply
# Outputs: findings_topic_arn = arn:aws:sns:us-east-1:123456789012:rivetops-findings
```

The module creates an SNS topic and outputs its ARN. Subscribe your notification endpoints to it however you prefer:

```bash
# PagerDuty (supports auto-confirmation)
aws sns subscribe \
  --topic-arn <findings_topic_arn> \
  --protocol https \
  --notification-endpoint https://events.pagerduty.com/integration/.../enqueue

# Email (requires clicking a confirmation link AWS sends)
aws sns subscribe \
  --topic-arn <findings_topic_arn> \
  --protocol email \
  --notification-endpoint oncall@yourcompany.com

# SQS (no confirmation required - recommended for custom integrations)
aws sns subscribe \
  --topic-arn <findings_topic_arn> \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:123456789012:my-queue
```

**Slack** — use [AWS Chatbot](https://docs.aws.amazon.com/chatbot/latest/adminguide/what-is.html) (configure it in the console to bridge your SNS topic to a Slack channel — no custom Lambda needed).

**PagerDuty** — supports SNS auto-confirmation natively; see [PagerDuty SNS integration docs](https://support.pagerduty.com/docs/aws-cloudwatch-integration-guide).

**Custom webhook** — subscribe an SQS queue to the SNS topic and consume from SQS in your own service.

## Security

- Lambda reads your own account data — no cross-account role, no credentials handed to RivetOps
- IAM execution role has `ReadOnlyAccess` scoped to your own account only
- SNS topic is in your account — you control all subscriptions and access policies
- Revoke access instantly by running `terraform destroy`
- All code is open source — review before you apply
