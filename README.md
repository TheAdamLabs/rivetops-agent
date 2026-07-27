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

**`runtime/`** — the Lambda handler code. Packaged by `infra/` during deployment. Not deployed standalone.

**`plugins/`** — intelligence layer. Self-contained Pi extensions. New RivetOps capabilities ship as new folders here, with zero changes to `infra/` or `runtime/`.

---

## How it works

The entire agent runs **in your own cloud account**. Findings are delivered via a cloud-native notification topic in your account — no RivetOps dependency required. Connecting the dashboard is optional and adds historical view, cross-account aggregation, and richer alerting.

```
Your AWS account (everything runs here)
┌────────────────────────────────────────────────────────────┐
│  EventBridge Scheduler (every 5 minutes)                   │
│        ↓                                                   │
│  Lambda  ←  runtime/aws  +  plugins/sre                    │
│        ↓ reads your own account data                       │
│  CloudWatch / CloudTrail / EC2 / ECS / EKS                 │
│        ↓                                                   │
│  SNS Topic  ──→  Slack / PagerDuty / email / webhook       │
└────────────────────────────────────────────────────────────┘
          ↓ also posts findings via HTTPS (optional)
┌─────────────────────────────────────────────┐
│  RivetOps Dashboard — rivetops.pro          │
│  historical view, multi-account, richer UI  │
└─────────────────────────────────────────────┘
```

| Cloud | Notification service |
|-------|---------------------|
| AWS | SNS |
| Azure | Event Grid |
| GCP | Pub/Sub |

1. Run `infra/terraform` or `infra/cdk` — deploys Lambda, EventBridge scheduler, SNS topic, and IAM execution role into your account.
2. Subscribe your Slack webhook, PagerDuty endpoint, or email address to the SNS topic.
3. Optionally paste the connection token into the [RivetOps dashboard](https://rivetops.pro) for historical view and richer UI.
4. The Lambda runs on a schedule, loads `plugins/sre`, reads your CloudWatch / CloudTrail / EC2, and publishes findings to SNS.

---

## Quick start (AWS)

```hcl
module "rivetops" {
  source             = "github.com/TheAdamLabs/rivetops-agent//infra/terraform/aws"
  plugin_id          = "sre"
  sns_subscribers    = ["https://hooks.slack.com/..."]   # Slack, PagerDuty, email, or any HTTPS endpoint

  # Optional: connect the RivetOps managed dashboard
  dashboard_endpoint = "https://api.rivetops.pro"
  connection_token   = var.rivetops_token
}
```

```bash
terraform apply
# Agent is running. Findings arrive in Slack within minutes.
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

| Plugin | Capability | Status |
|--------|------------|--------|
| `plugins/sre` | Anomaly detection, incident correlation | Live |
| `plugins/finops` | Cost anomaly, rightsizing | Q3 2026 |
| `plugins/security` | IAM drift, misconfiguration | Q4 2026 |
| `plugins/compliance` | CIS benchmarks, audit trails | 2027 |

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
