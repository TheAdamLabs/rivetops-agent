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
     "dashboardEndpoint": "https://api.rivetops.pro",
     "token": "<per-tenant bearer token>"
   }
   ```
2. Boots the Pi SDK and loads the specified plugin from `plugins/<pluginId>`.
3. Plugin reads CloudWatch, CloudTrail, EC2, ECS, EKS using the Lambda's IAM execution role.
4. Plugin returns a structured finding with fingerprint fields and narrative fields (see `plugins/sre/README.md`).
5. Runtime checks DynamoDB for the finding fingerprint and applies deduplication logic.
6. Publishes to SNS only on state transitions (OPEN, RE_ALERT, RESOLVED).
7. Optionally posts all findings to the RivetOps dashboard API regardless of suppression.

---

## Deduplication

LLM output is non-deterministic — the same condition produces different explanation text every run. To avoid re-alerting on the same open incident every 5 minutes, the runtime deduplicates on the **fingerprint fields** defined by the plugin, not on the narrative.

```
fingerprint = hash(anomaly_type + primary_resource + sorted(correlated_resources) + region)
```

### State machine

```
           first seen
               ↓
[ OPEN ] ─── SNS: "new finding" ──────────────────────────┐
               │                                           │
               │ still present after suppression window    │
               ↓                                           │
[ RE_ALERT ] ─ SNS: "still open after Nh" ─ refresh TTL  │
               │                                           │
               │ condition cleared on next run             │
               ↓                                           │
[ RESOLVED ] ─ SNS: "resolved" ─ delete DynamoDB record ──┘
```

SNS only fires on: **OPEN** (first occurrence), **RE_ALERT** (still present after suppression window), **RESOLVED** (condition cleared). Repeated detections within the suppression window are silent.

### DynamoDB record

```json
{
  "fingerprint":    "a3f9c2...",
  "state":          "OPEN",
  "anomaly_type":   "cpu_spike",
  "primary_resource": "i-0abc123def456789",
  "region":         "us-east-1",
  "first_seen":     1722110400,
  "last_seen":      1722110400,
  "ttl":            1722124800
}
```

`ttl` is set to `now + suppressionWindowHours`. DynamoDB auto-deletes expired records — no cleanup Lambda needed. On each run where the condition still holds, the runtime updates `last_seen` and refreshes `ttl`.

---

## Notification flow

```
Plugin returns finding
  ↓
Check DynamoDB fingerprint
  ├── Not found       → state = OPEN    → publish to SNS + write DynamoDB
  ├── Found, TTL live → state = SUSTAINED → skip SNS, update last_seen
  ├── Found, TTL expired → state = RE_ALERT → publish to SNS + refresh TTL
  └── Was OPEN, now cleared → state = RESOLVED → publish to SNS + delete record

SNS topic (customer's account)
  ├── PagerDuty  (auto-confirms SNS HTTPS subscriptions natively)
  ├── Email      (requires manual confirmation click from AWS)
  ├── SQS        (no confirmation needed; use for custom integrations)
  └── Slack      (via AWS Chatbot)

  + all findings (including SUSTAINED) → RivetOps Dashboard API (optional)
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

## What `infra/terraform/aws` deploys

- Lambda function (this code + specified plugin)
- EventBridge rule + scheduler
- SNS topic (customer subscribes their own endpoints)
- DynamoDB table (finding state, on-demand billing, TTL enabled)
- IAM execution role with the permissions above

---

## Not deployed standalone

Packaged and deployed by `infra/terraform/aws` or `infra/cdk`. Do not run directly.

---

## Status

Planned — implementation starts after `infra/terraform` and `infra/cdk` are complete.
