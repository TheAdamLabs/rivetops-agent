# infra/cdk

AWS CDK TypeScript construct — equivalent to `infra/terraform/aws/` for teams using CDK.

## Usage

```typescript
import { App, Stack, CfnOutput } from "aws-cdk-lib";
import { RivetOpsOnboarding } from "rivetops-cdk-aws";

const app = new App();
const stack = new Stack(app, "RivetOpsStack");

const onboarding = new RivetOpsOnboarding(stack, "RivetOps", {
  saasAccountId: "123456789012",   // RivetOps AWS account ID
});

new CfnOutput(stack, "RoleArn", {
  value: onboarding.roleArn,
});
```

Run `cdk deploy`, copy the `RoleArn` output, paste it into the RivetOps dashboard.

> Azure and GCP CDK equivalents are not available — use `infra/terraform/azure` and `infra/terraform/gcp` instead.
