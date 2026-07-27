# infra/cdk

AWS CDK TypeScript construct — equivalent to `infra/terraform/aws/` for teams using CDK.

Deploys the full RivetOps agent stack into your own AWS account: Lambda function, EventBridge scheduler, SNS topic, DynamoDB suppression table, and IAM execution role.

## Usage

```typescript
import { App, Stack, CfnOutput } from "aws-cdk-lib";
import { RivetOpsAgent } from "rivetops-cdk-aws";

const app = new App();
const stack = new Stack(app, "RivetOpsStack");

const agent = new RivetOpsAgent(stack, "RivetOps", {
  pluginId: "sre",
  suppressionWindowHours: 4,      // default; how long to suppress re-alerts for the same finding

  // Optional: connect to the RivetOps managed dashboard
  dashboardEndpoint: "https://api.rivetops.pro",
  connectionToken: process.env.RIVETOPS_TOKEN,
});

// Output the SNS topic ARN - subscribe your notification endpoints to it
new CfnOutput(stack, "FindingsTopicArn", { value: agent.findingsTopicArn });
```

```bash
cdk deploy
# Outputs: FindingsTopicArn = arn:aws:sns:us-east-1:123456789012:rivetops-findings
```

The construct creates an SNS topic and outputs its ARN. You then subscribe notification endpoints to it - via the AWS console, AWS CLI, or additional CDK/Terraform resources. See `infra/terraform/README.md` for subscription examples (PagerDuty, email, SQS, AWS Chatbot for Slack).

## What gets deployed

- Lambda function (packages `runtime/aws` + the specified plugin)
- EventBridge rule (triggers Lambda every 5 minutes by default)
- SNS topic (receives findings; you control subscribers)
- DynamoDB table (alert suppression state, TTL-managed, on-demand billing)
- IAM execution role (read-only access to your own account + scoped SNS + DynamoDB permissions)

## Security

- Lambda reads your own account data — no cross-account role, no credentials handed to RivetOps
- `ReadOnlyAccess` scoped to your own account only
- SNS subscribers are HTTPS endpoints or email addresses you control
- Revoke access by running `cdk destroy`

> Azure and GCP: use `infra/terraform/azure` and `infra/terraform/gcp` (coming soon).
