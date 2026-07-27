# Contributing to rivetops-agent

Thanks for your interest in contributing. This repo is MIT licensed and community contributions are welcome.

---

## What lives here

```
infra/terraform/     Full agent stack via Terraform (aws/, azure/, gcp/)
infra/cdk/           AWS CDK TypeScript alternative
runtime/aws/         Lambda handler code (packaged by infra/terraform/aws)
plugins/sre/         SRE intelligence plugin
```

The highest-value contributions right now are:
- **`infra/terraform/azure/`** and **`infra/terraform/gcp/`** — these stubs need real Terraform
- **`runtime/azure/`** and **`runtime/gcp/`** — Function/Cloud Run handler equivalents
- **`plugins/sre/`** — expanding cloud service coverage (ECS, EKS, RDS, VPC)
- Bug fixes and documentation improvements anywhere

---

## Getting started

1. Fork the repo and clone your fork.
2. Create a branch: `git checkout -b feat/your-feature`.
3. Make your changes.
4. Open a pull request against `main` with a clear description of what and why.

---

## Pull request guidelines

- Keep PRs focused — one concern per PR.
- Include a short description of the change and its motivation.
- For new Terraform or CDK code, include a note on how you tested it (manual `terraform plan` output is fine).
- For plugin changes, describe what signals the change reads and why.

---

## Adding a new cloud provider

1. Create `infra/terraform/<provider>/` — module that deploys Lambda/Function + scheduler + execution identity.
2. Create `runtime/<provider>/` — the Function handler code packaged by the Terraform module.
3. Follow the pattern in `infra/terraform/aws/` and `runtime/aws/` — event payload format, plugin loading, findings API call.
4. Document the exact permissions granted to the execution identity and how to revoke access.

---

## Security

If you discover a security issue, please **do not open a public issue**. Email `info+rivetops@theadamlabs.com` directly.

---

## License

By contributing, you agree your changes will be released under the [MIT License](./LICENSE).
