# runtime/aws — Lambda Handler

The AWS Lambda execution shell for the RivetOps agent. Runs **inside the customer's AWS account**, deployed via `infra/terraform/aws` or `infra/cdk`.

---

## What it does

1. Receives an EventBridge event payload:
   ```json
   {
     "pluginId": "sre",
     "snsTopicArn": "arn:aws:sns:us-east-1:123456789012:rivetops-findings",
     "stateTableName": "rivetops-finding-state",
     "suppressionWindowHours": 4,
     "customInstructions": "Focus on EKS clusters. Ignore batch-worker CPU spikes.",
     "extraPlugins": [],
     "dashboardEndpoint": "https://api.rivetops.pro",
     "token": "<per-tenant bearer token>"
   }
   ```
2. Boots a **pi.dev SDK session** in headless mode, loading the specified plugin's skill files and any extra packages.
3. The agent uses `bash` + AWS CLI (available in Lambda) to read CloudWatch, CloudTrail, EC2, ECS, EKS — no custom tool wrappers needed.
4. Returns a structured findings list. For each finding: checks DynamoDB (rate limiting), publishes to SNS.
5. Posts all findings to the RivetOps dashboard API regardless of suppression (optional).

---

## Pi.dev SDK integration

`runtime/aws` uses the [pi.dev SDK](https://pi.dev/) (`@earendil-works/pi-coding-agent`) in **headless mode** — no TTY, no interactive loop. The Lambda starts a pi agent session, runs to completion, and exits.

```typescript
import { createAgentSession } from "@earendil-works/pi-coding-agent";

export async function handler(event: RivetOpsEvent) {
  const session = await createAgentSession({
    systemPrompt: event.customInstructions,  // from Terraform/CDK input
    skills: [
      `${__dirname}/../../plugins/${event.pluginId}`,  // skill markdown files
    ],
    runMode: "print",  // non-interactive: run to completion, return output
  });

  const result = await session.prompt(
    "Analyze this AWS account for infrastructure anomalies and return your findings."
  );

  const findings = parseFindings(result);
  await processFindings(findings, event);
}
```

The session uses the Lambda's ambient AWS credentials (from the IAM execution role) via the standard AWS SDK/CLI credential chain. No `sts:AssumeRole`, no cross-account, same account only.

### Why no custom tools

Plugins are **skill markdown files**, not TypeScript tool wrappers. The agent already has `bash` built in, and the AWS CLI is available in the Lambda runtime environment. Skill files tell the agent which commands to run and how to interpret output — no code to write or maintain.

---

## Custom instructions

`custom_instructions` (Terraform) / `customInstructions` (CDK) is a multiline string injected as additional system prompt on every run. Use it to tailor the agent to your environment without forking:

```hcl
custom_instructions = <<-EOT
  Focus on our EKS clusters in us-east-1: prod-cluster, staging-cluster.
  Ignore CPU spikes on instances tagged Role=batch-worker — expected behavior.
  For any RDS finding, include the current replica lag from CloudWatch.
EOT
```

---

## Extra plugins

`extra_plugins` (Terraform) / `extraPlugins` (CDK) is a list of pi package names from the [pi package catalog](https://pi.dev/packages) or your private registry. They are bundled into the Lambda at deploy time by the Terraform/CDK build step — not downloaded at runtime.

```hcl
extra_plugins = [
  "@your-org/custom-runbook-skill",  # your own skill markdown package
]
```

---

## Alert suppression

The plugin runs every N minutes. Without suppression, the same CPU spike would page someone every 5 minutes. RivetOps solves this with a simple rate-limit: a DynamoDB record acts as a "do not re-alert" token for a configurable window.

```
fingerprint = hash(anomaly_type + primary_resource + sorted(correlated_resources) + region)

For each finding:
  fingerprint in DynamoDB?
    NO  → publish to SNS + write DynamoDB record (TTL = now + suppressionWindowHours)
    YES → skip SNS (still within suppression window)

TTL expires → record deleted automatically → next detection triggers a fresh alert
```

This is rate limiting, not incident lifecycle management. There is no "resolved" event — incident lifecycle is the customer's alerting tool's responsibility (PagerDuty dedup keys, Opsgenie deduplication, etc.).

### DynamoDB record

```json
{
  "fingerprint":      "a3f9c2...",
  "anomaly_type":     "cpu_spike",
  "primary_resource": "i-0abc123def456789",
  "region":           "us-east-1",
  "last_alerted":     1722110400,
  "ttl":              1722124800
}
```

`ttl` is set to `now + suppressionWindowHours`. DynamoDB auto-deletes expired records — no cleanup Lambda needed.

---

## Notification flow

```
Pi session returns findings list
  ↓
For each finding:
  Check DynamoDB fingerprint
  ├── Not found (or TTL expired) → publish to SNS + write/refresh DynamoDB
  └── Found (within window)      → skip SNS

SNS topic (customer's account)
  ├── PagerDuty  (auto-confirms SNS HTTPS subscriptions natively)
  ├── Email      (requires manual confirmation click from AWS)
  ├── SQS        (no confirmation needed; use for custom integrations)
  └── Slack      (via AWS Chatbot)

All findings (including suppressed) → RivetOps Dashboard API (optional)
```

---

## IAM execution role

Created by `infra/terraform/aws`. Permissions:

| Permission | Scope |
|------------|-------|
| `ReadOnlyAccess` | Customer's own account (CloudWatch, CloudTrail, EC2, ECS, EKS) |
| `sns:Publish` | Findings SNS topic only |
| `dynamodb:GetItem`, `PutItem`, `UpdateItem`, `DeleteItem` | Finding state table only |

Never reaches outside the customer's AWS account.

---

## Not deployed standalone

Packaged and deployed by `infra/terraform/aws` or `infra/cdk`. Do not run directly.

---

## Status

Planned — implementation starts after `infra/terraform` and `infra/cdk` are complete.
