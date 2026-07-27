# runtime/aws — Lambda Handler

The AWS Lambda execution shell for the RivetOps agent. This is the code that runs **inside the customer's AWS account** - deployed and managed by the customer via `infra/terraform/aws` or `infra/cdk`.

---

## What it does

1. Receives an EventBridge event payload:
   ```json
   {
     "pluginId": "sre",
     "apiEndpoint": "https://api.rivetops.pro",
     "token": "<per-tenant bearer token>"
   }
   ```
2. Boots the Pi SDK and loads the specified plugin from `plugins/<pluginId>`.
3. Plugin reads CloudWatch, CloudTrail, EC2, ECS, EKS using the Lambda's own IAM execution role (same account - no cross-account needed).
4. Posts structured findings to the RivetOps findings API over HTTPS.

---

## IAM execution role

The Lambda's IAM execution role (created by `infra/terraform/aws`) has read-only access to the customer's own account. It never reaches outside the customer's AWS account.

Permissions attached: `ReadOnlyAccess` scoped to the same account.

---

## Not deployed standalone

This code is packaged and deployed by `infra/terraform/aws` or `infra/cdk`. You do not run it directly.

See `infra/terraform/aws/` for deployment instructions.

---

## Status

Planned — implementation starts after onboarding modules (`infra/terraform`, `infra/cdk`) are complete.
