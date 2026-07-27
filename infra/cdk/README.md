# infra/cdk

AWS CDK TypeScript construct — equivalent to `infra/terraform/aws/` for teams using CDK.

Deploys the full RivetOps agent stack into your own AWS account: Lambda function, EventBridge scheduler, SNS notification topic, and IAM execution role.

## Usage

```typescript
import { App, Stack } from "aws-cdk-lib";
import { RivetOpsAgent } from "rivetops-cdk-aws";

const app = new App();
const stack = new Stack(app, "RivetOpsStack");

new RivetOpsAgent(stack, "RivetOps", {
  pluginId: "sre",
  snsSubscribers: ["https://hooks.slack.com/..."],  // Slack, PagerDuty, email, or any HTTPS endpoint

  // Optional: connect to the RivetOps managed dashboard
  dashboardEndpoint: "https://api.rivetops.pro",
  connectionToken: process.env.RIVETOPS_TOKEN,
});
```

```bash
cdk deploy
# Findings arrive in Slack within minutes
```

## What gets deployed

- Lambda function (packages `runtime/aws` + the specified plugin)
- EventBridge rule (triggers Lambda every 5 minutes by default)
- SNS topic (receives findings; you control subscribers)
- IAM execution role (read-only access to your own account)

## Security

- Lambda reads your own account data — no cross-account role, no credentials handed to RivetOps
- `ReadOnlyAccess` scoped to your own account only
- SNS subscribers are HTTPS endpoints or email addresses you control
- Revoke access by running `cdk destroy`

> Azure and GCP: use `infra/terraform/azure` and `infra/terraform/gcp` (coming soon).
