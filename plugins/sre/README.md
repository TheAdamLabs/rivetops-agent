# plugins/sre

SRE intelligence plugin for RivetOps. Loaded by `runtime/aws` at invocation time - turns the generic Lambda shell into an autonomous SRE monitor: anomaly detection, incident correlation, and plain-English findings.

## What it does

1. Reads CloudWatch metrics, CloudTrail events, and EC2/ECS/EKS state using the Lambda's own IAM execution role (no cross-account - the Lambda runs in the customer's account).
2. Correlates signals across services to identify anomalies.
3. Posts structured findings to the RivetOps findings API over HTTPS.

## Finding format

```
[FINDING] Severity: HIGH
Resource:  i-0abc123def456789
Type:      ec2 / us-east-1

Signal:    CPU spike 94% (15 min sustained)
           ELB 5xx rate correlated at 12%

Action:    Check application logs on instance.
           Possible OOM event. Recommend memory
           increase or code-level investigation.

Confidence: 91%   Context tokens: 4,812
```

## Status

Active development. Targets the Operational Excellence, Reliability, and Performance pillars.
