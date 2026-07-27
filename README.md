# rivetops-agent

> Open-source onboarding modules, Lambda execution shell, and SRE plugin for [RivetOps](https://rivetops.pro) — AI cloud monitoring for AWS, Azure, and GCP.

MIT licensed. Fully auditable. Community contributions welcome.

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

**`infra/`** contains the infrastructure glue: how customers grant RivetOps read-only access to their cloud account, and the Lambda runtime that executes plugins.

**`plugins/`** contains the intelligence layer. Each plugin is a self-contained Pi extension that tells the agent what to look for and how to reason about it. New RivetOps capabilities ship as new plugin folders here.

---

## How it works

```
Customer Cloud Account          RivetOps SaaS (closed)
┌──────────────────────┐        ┌─────────────────────────────┐
│  IAM Role (AWS)      │◄───────│  infra/agent-lambda         │
│  Service Principal   │ cross  │    loads plugins/sre        │
│  Service Account     │ account│  EventBridge Scheduler      │
│  (read-only trust)   │        │  Control Plane + Dashboard  │
└──────────────────────┘        └─────────────────────────────┘
          ▲
          │ applied via
   infra/terraform  or  infra/cdk
```

1. Customer applies `infra/terraform` or `infra/cdk` to create a read-only cross-account role.
2. Customer pastes the output role identifier into the RivetOps dashboard.
3. RivetOps schedules `infra/agent-lambda` to run on a timer, loading `plugins/sre`.
4. The plugin assumes the customer role, reads cloud telemetry, and posts findings to the dashboard.

---

## Getting started

See the README in each package:

- [`infra/terraform`](./infra/terraform/README.md) — Terraform modules for AWS, Azure, GCP
- [`infra/cdk`](./infra/cdk/README.md) — AWS CDK construct
- [`infra/agent-lambda`](./infra/agent-lambda/README.md) — Lambda shell
- [`plugins/sre`](./plugins/sre/README.md) — SRE intelligence plugin

---

## Contributing

Issues and PRs are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## License

[MIT](./LICENSE)
