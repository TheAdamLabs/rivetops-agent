# infra/cdk

AWS CDK TypeScript construct — equivalent to `infra/terraform/aws/` for teams using CDK.

Deploys the full RivetOps agent stack into your own AWS account: Lambda function, EventBridge scheduler, and IAM execution role.

## Usage

```typescript
import { App, Stack } from "aws-cdk-lib";
import { RivetOpsAgent } from "rivetops-cdk-aws";

const app = new App();
const stack = new Stack(app, "RivetOpsStack");

new RivetOpsAgent(stack, "RivetOps", {
  pluginId: "sre",
  dashboardEndpoint: "https://api.rivetops.pro",
  connectionToken: process.env.RIVETOPS_TOKEN!,  // from rivetops.pro dashboard
});
```

Run `cdk deploy`. The agent starts monitoring your account immediately.

## What gets deployed

- Lambda function (packages `runtime/aws` + the specified plugin)
- EventBridge rule (triggers Lambda every 5 minutes by default)
- IAM execution role (read-only access to your own account)

## Security

- Lambda reads your own account data — no cross-account role, no credentials handed to RivetOps
- `ReadOnlyAccess` scoped to your own account only
- Revoke access by running `cdk destroy`

> Azure and GCP: use `infra/terraform/azure` and `infra/terraform/gcp` (coming soon).
