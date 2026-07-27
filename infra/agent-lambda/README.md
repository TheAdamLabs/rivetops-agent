# infra/agent-lambda

Agnostic AWS Lambda execution shell. No business logic — it initializes the `pi.dev` SDK, accepts a plugin URL and a target role ARN, and executes the plugin.

## Event payload

```json
{
  "pluginUrl": "rivetops-agent/plugins/sre@v1.0.0",
  "targetRoleArn": "arn:aws:iam::CUSTOMER_ACCOUNT::role/rivetops-agent",
  "context": {
    "tenantId": "tenant-uuid"
  }
}
```

## Lambda execution role permissions

The Lambda execution role is scoped to:
- `sts:AssumeRole` on `arn:aws:iam::*:role/rivetops-*` only
- No other AWS permissions

## Swapping plugins

Changing `pluginUrl` in the event payload is all that is needed to run a different intelligence module. The Lambda itself never changes.
