<div align="center">

<img src="https://rivetops.pro/rivet-mascot.webp" alt="Rivet - the RivetOps mascot" width="140" />

# rivetops-agent

**The full RivetOps agent stack - runs entirely in your own cloud account.**

AI cloud monitoring for AWS, Azure, and GCP — autonomous, 24/7.

[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](./LICENSE)
[![Website](https://img.shields.io/badge/website-rivetops.pro-orange)](https://rivetops.pro)
[![Join Waitlist](https://img.shields.io/badge/join-waitlist-orange)](https://rivetops.pro/#waitlist)

</div>

---

## What's in here

```
infra/
├── terraform/         Full agent stack via Terraform (aws/, azure/, gcp/)
└── cdk/               AWS CDK TypeScript alternative

runtime/
└── aws/               Lambda handler code (packaged by infra/terraform/aws)

plugins/
└── sre/               SRE intelligence — anomaly detection, incident correlation
```

**`infra/`** — what you run once to deploy the agent into your account. Deploys the Lambda, EventBridge scheduler, IAM execution role, and notification topic.

**`runtime/`** — the Lambda handler. Boots a [pi.dev](https://pi.dev/) SDK session in headless mode, loads the plugin skill files, and runs the agent to completion. Packaged by `infra/` — not deployed standalone.

**`plugins/`** — intelligence layer. Each plugin is a directory of **pi.dev skill files** (markdown). The agent uses `bash` + AWS CLI to read your infrastructure — no custom tool wrappers to write or maintain. New RivetOps capabilities ship as new plugin folders with zero changes to `infra/` or `runtime/`.

---

## How it works

The entire agent runs **in your own cloud account**. Findings are delivered via a cloud-native notification topic in your account — no RivetOps dependency required. Connecting the dashboard is optional and adds historical view, cross-account aggregation, and richer alerting.

```
Your AWS account
┌──────────────────────────────────────────────────────────────┐
│  EventBridge Scheduler (every 5 min)                         │
│        ↓                                                     │
│  Lambda ── runtime/aws + plugins/sre                         │
│    │  ↕ check/update                                         │
│    │  DynamoDB (alert suppression)                           │
│    │                                                         │
│    ↓ reads own account                                       │
│  CloudWatch / CloudTrail / EC2 / ECS / EKS                   │
│    │                                                         │
│    ↓ publish on first occurrence or after suppression window │
│  SNS Topic ──→ PagerDuty / Email / SQS / AWS Chatbot→Slack  │
└──────────────────────────────────────────────────────────────┘
         │
         ↓ optional HTTPS POST
  RivetOps Dashboard (historical view, multi-account, richer UI)
```

| Cloud | Notification service |
|-------|---------------------|
| AWS | SNS |
| Azure | Event Grid |
| GCP | Pub/Sub |

1. Run `infra/terraform` or `infra/cdk` — deploys Lambda, EventBridge scheduler, SNS topic, DynamoDB suppression table, and IAM execution role into your account.
2. Subscribe PagerDuty, email, or SQS to the SNS topic ARN that is output. Use [AWS Chatbot](https://docs.aws.amazon.com/chatbot/latest/adminguide/what-is.html) for Slack.
3. Optionally paste the connection token into the [RivetOps dashboard](https://rivetops.pro) for historical view and richer UI.
4. The Lambda runs on a schedule, loads `plugins/sre`, reads your CloudWatch / CloudTrail / EC2, and publishes findings to SNS — suppressing re-alerts for the same finding within the configured window.

---

## Quick start (AWS)

```hcl
module "rivetops" {
  source    = "github.com/TheAdamLabs/rivetops-agent//infra/terraform/aws"
  plugin_id = "sre"

  # Tailor the agent to your environment - injected as system prompt on every run
  custom_instructions = <<-EOT
    Focus on our EKS clusters: prod-cluster, staging-cluster (us-east-1).
    Ignore CPU spikes on instances tagged Role=batch-worker - expected behavior.
  EOT

  # Optional: add pi packages from https://pi.dev/packages or your private registry
  # extra_plugins = ["@your-org/custom-runbook-skill"]

  # Optional: connect the RivetOps managed dashboard
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
# Subscribe PagerDuty, email, or SQS to that ARN. Use AWS Chatbot for Slack.
```

See [`infra/terraform/`](./infra/terraform/README.md) for all providers and options.

---

## Security model

| Concern | Mechanism |
|---------|-----------|
| No RivetOps access to your infra | Agent runs in your account - RivetOps never touches it directly |
| Read-only | IAM execution role has `ReadOnlyAccess` scoped to your own account only |
| Instant revocation | `terraform destroy` removes everything; access ends immediately |
| Auditable | This entire repo is open source - review every line before deploying |

---

## Roadmap

| | AWS | Azure | GCP |
|---|---|---|---|
| **SRE monitoring** | In Development | Planned | Planned |
| **FinOps** | Planned | Planned | Planned |
| **Security Auditor** | Planned | Planned | Planned |
| **Compliance** | Planned | Planned | Planned |

New capability = new plugin folder. Zero changes to `infra/` or `runtime/`.

---

## Contributing

Issues and PRs are welcome. Highest-value contributions right now:

- `infra/terraform/azure/` and `infra/terraform/gcp/` — these stubs need real Terraform
- `runtime/azure/` and `runtime/gcp/` — Function/Cloud Run handler equivalents
- `plugins/sre/` — expanding coverage to ECS, EKS, RDS, VPC Flow Logs

See [CONTRIBUTING.md](./CONTRIBUTING.md) to get started.

---

## License

[MIT](./LICENSE) — free to use, audit, fork, and contribute.

<div align="center">
<br />
<a href="https://rivetops.pro">
  <img src="https://rivetops.pro/rivet-head.webp" alt="RivetOps" width="48" />
</a>
<br />
<sub>Built by <a href="https://rivetops.pro">RivetOps</a></sub>
</div>
