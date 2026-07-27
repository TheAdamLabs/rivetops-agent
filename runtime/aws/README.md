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
4. Plugin returns a list of structured findings with fingerprint fields and narrative fields (see `plugins/sre/README.md`).
5. For each finding: checks DynamoDB to decide whether SNS should fire (rate limiting).
6. Publishes to SNS for findings outside their suppression window.
7. Posts all findings to the RivetOps dashboard API regardless of suppression (optional).

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

This is rate limiting, not incident lifecycle management. There is no explicit "resolved" event — incident lifecycle is the customer's alerting tool's responsibility (PagerDuty dedup keys, Opsgenie alert deduplication, etc.).

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
Plugin returns findings list
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

## What `infra/terraform/aws` deploys

- Lambda function (this code + specified plugin)
- EventBridge rule + scheduler
- SNS topic (customer subscribes their own endpoints)
- DynamoDB table (suppression state, on-demand billing, TTL enabled)
- IAM execution role with the permissions above

---

## Not deployed standalone

Packaged and deployed by `infra/terraform/aws` or `infra/cdk`. Do not run directly.

---

## Status

Planned — implementation starts after `infra/terraform` and `infra/cdk` are complete.
