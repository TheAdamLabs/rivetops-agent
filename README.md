<div align="center">

<img src="https://rivetops.pro/rivet-mascot.webp" alt="Rivet - the RivetOps mascot" width="140" />

# rivetops-agent

**Open-source onboarding modules, Lambda execution shell, and SRE plugin for [RivetOps](https://rivetops.pro).**

AI cloud monitoring for AWS, Azure, and GCP — autonomous, 24/7, no dashboards.

[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](./LICENSE)
[![Website](https://img.shields.io/badge/website-rivetops.pro-orange)](https://rivetops.pro)
[![Join Waitlist](https://img.shields.io/badge/join-waitlist-orange)](https://rivetops.pro/#waitlist)

</div>

---

## What's in here

```
infra/
├── terraform/         Cross-account role setup (aws/, azure/, gcp/)
├── cdk/               AWS CDK TypeScript construct (equivalent to terraform/aws/)
└── agent-lambda/      Agnostic Lambda shell that loads any plugin at runtime

plugins/
└── sre/               SRE intelligence — anomaly detection, incident correlation
```

**`infra/`** — infrastructure glue. Customers apply one of these to their cloud account to grant RivetOps read-only access. No credentials are stored. Access is revoked by deleting the role.

**`plugins/`** — intelligence layer. Each plugin is a self-contained Pi extension that tells the agent what to look for and how to reason about it. New RivetOps capabilities ship as new folders here.

---

## How it works

```
Customer Cloud Account          RivetOps SaaS
┌──────────────────────┐        ┌──────────────────────────────┐
│  IAM Role (AWS)      │◄───────│  infra/agent-lambda          │
│  Service Principal   │ cross  │    loads plugins/sre         │
│  Service Account     │ account│  EventBridge Scheduler       │
│  (read-only trust)   │        │  Control Plane + Dashboard   │
└──────────────────────┘        └──────────────────────────────┘
          ▲
          │ applied once via
   infra/terraform  or  infra/cdk
```

1. Apply `infra/terraform` or `infra/cdk` — creates a read-only cross-account role in your cloud account.
2. Paste the output role identifier into the [RivetOps dashboard](https://rivetops.pro).
3. RivetOps runs `infra/agent-lambda` on a schedule, loading `plugins/sre`.
4. The plugin assumes your role, reads cloud telemetry, and posts findings.

Everything in this repo runs **in your cloud account** — you pay pennies for Lambda execution, RivetOps never touches your infrastructure directly.

---

## Quick start (AWS)

```hcl
module "rivetops" {
  source          = "rivetops/onboarding/aws"
  saas_account_id = "123456789012"
}

output "role_arn" {
  value = module.rivetops.role_arn
}
```

```bash
terraform apply
# Copy the role_arn output → paste into rivetops.pro dashboard
```

That is the entire setup. See [`infra/terraform/`](./infra/terraform/README.md) for all providers.

---

## Security model

| Concern | Mechanism |
|---------|-----------|
| No credential storage | STS temp credentials only, 1h TTL, never persisted |
| Blast radius | `ReadOnlyAccess` policy — no write permissions |
| Instant revocation | Delete the IAM role and access ends immediately |
| Auditable | This entire repo is open source — review before you apply |

---

## Contributing

Issues and PRs are welcome. The highest-value contributions right now:

- `infra/terraform/azure/` and `infra/terraform/gcp/` — these stubs need real Terraform
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
