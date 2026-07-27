# runtime/aws — Lambda Handler

The AWS Lambda execution shell for the RivetOps agent. This is the code that runs **inside the customer's AWS account** - deployed and managed by the customer via `infra/terraform/aws` or `infra/cdk`.

---

## What it does

1. Receives an EventBridge event payload:
   ```json
   {
     "pluginId": "sre",
     "snsTopicArn": "arn:aws:sns:us-east-1:123456789012:rivetops-findings",
     "dashboardEndpoint": "https://api.rivetops.pro",
     "token": "<per-tenant bearer token>"
   }
   ```
2. Boots the Pi SDK and loads the specified plugin from `plugins/<pluginId>`.
3. Plugin reads CloudWatch, CloudTrail, EC2, ECS, EKS using the Lambda's own IAM execution role (same account - no cross-account needed).
4. Publishes structured findings to the SNS topic in the customer's account - subscribers (Slack, PagerDuty, email, webhook) receive them immediately.
5. Optionally posts findings to the RivetOps dashboard API over HTTPS if `dashboardEndpoint` and `token` are provided.

---

## Notification flow

```
Lambda
  ↓
SNS topic (customer's account) — module outputs the ARN
  ├── PagerDuty  (auto-confirms SNS HTTPS subscriptions natively)
  ├── Email      (requires manual confirmation click from AWS)
  ├── SQS        (no confirmation needed; use for custom integrations)
  └── Slack      (via AWS Chatbot — bridges SNS to Slack without custom Lambda)

  + optionally → RivetOps Dashboard API (HTTPS)
```

The SNS publish step always runs. The dashboard step is skipped if no token is configured — the agent works fully standalone without it.

---

## IAM execution role

The Lambda's IAM execution role (created by `infra/terraform/aws`) has:
- `ReadOnlyAccess` to the customer's own account (CloudWatch, CloudTrail, EC2, ECS, EKS)
- `sns:Publish` to the findings SNS topic

It never reaches outside the customer's AWS account.

---

## Not deployed standalone

This code is packaged and deployed by `infra/terraform/aws` or `infra/cdk`. You do not run it directly.

See `infra/terraform/aws/` for deployment instructions.

---

## Status

Planned — implementation starts after onboarding modules (`infra/terraform`, `infra/cdk`) are complete.
