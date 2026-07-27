# plugins/sre

SRE intelligence plugin for RivetOps. Loaded by `runtime/aws` at invocation time - turns the generic Lambda shell into an autonomous SRE monitor: anomaly detection, incident correlation, and plain-English findings.

## What it does

1. Reads CloudWatch metrics, CloudTrail events, and EC2/ECS/EKS state using the Lambda's own IAM execution role (no cross-account - the Lambda runs in the customer's account).
2. Correlates signals across services to identify anomalies.
3. Returns a structured finding to `runtime/aws`, which publishes it to SNS and optionally to the RivetOps dashboard API.

## Finding format

```json
{
  "severity": "HIGH",
  "resource": "i-0abc123def456789",
  "type": "ec2",
  "region": "us-east-1",
  "signals": [
    "CPU spike 94% (15 min sustained)",
    "ELB 5xx rate correlated at 12%"
  ],
  "action": "Check application logs on instance. Possible OOM event. Recommend memory increase or code-level investigation.",
  "confidence": 0.91,
  "context_tokens": 4812
}
```

SNS message body is the JSON finding above. Subscribers receive it directly and can filter by `severity` using SNS filter policies.

## Status

Active development. Targets the Operational Excellence, Reliability, and Performance pillars.
