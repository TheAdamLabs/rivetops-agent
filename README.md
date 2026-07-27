<div align="center">

<img src="https://rivetops.pro/rivet-mascot.webp" alt="Rivet - the RivetOps mascot" width="140" />

# rivetops-agent

**The full RivetOps agent stack - runs entirely in your own cloud account.**

AI cloud monitoring for AWS, Azure, and GCP — autonomous, 24/7, no dashboards.

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

**`infra/`** — what you run once to deploy the agent into your account. Deploys the Lambda, EventBridge scheduler, and IAM execution role.

**`runtime/`** — the Lambda handler code. Packaged by `infra/` during deployment. Not deployed standalone.

**`plugins/`** — intelligence layer. Self-contained Pi extensions. New RivetOps capabilities ship as new folders here, with zero changes to `infra/` or `runtime/`.

---

## How it works

The entire agent runs **in your own cloud account**. RivetOps hosts only the dashboard.

```
Your AWS account (everything runs here)
┌──────────────────────────────────────────────────────┐
│  EventBridge Scheduler (every 5 minutes)             │
│        ↓                                             │
│  Lambda  ←  runtime/aws  +  plugins/sre              │
│        ↓ reads your own account data                 │
│  CloudWatch / CloudTrail / EC2 / ECS / EKS           │
└──────────────────────────────────────────────────────┘
          ↓ posts findings via HTTPS
┌─────────────────────────────────┐
│  RivetOps Dashboard (private)   │
└─────────────────────────────────┘
```

1. Run `infra/terraform` or `infra/cdk` — deploys the full agent stack into your account.
2. Paste the connection token into the [RivetOps dashboard](https://rivetops.pro).
3. The Lambda runs on a schedule, loads `plugins/sre`, reads your CloudWatch / CloudTrail / EC2.
4. Findings appear in the dashboard. Your on-call team gets notified before the pager fires.

---

## Quick start (AWS)

```hcl
module "rivetops" {
  source             = "github.com/TheAdamLabs/rivetops-agent//infra/terraform/aws"
  plugin_id          = "sre"
  dashboard_endpoint = "https://api.rivetops.pro"
  connection_token   = var.rivetops_token
}
```

```bash
terraform apply
# Agent is running in your account
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
