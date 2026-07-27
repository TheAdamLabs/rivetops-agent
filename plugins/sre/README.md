# plugins/sre

SRE intelligence plugin for RivetOps. Turns the generic `infra/agent-lambda` shell into an autonomous SRE monitor — anomaly detection, incident correlation, and plain-English findings.

## What it does

1. Assumes the customer's read-only cross-account role via STS.
2. Reads CloudWatch metrics, CloudTrail events, and EC2/ECS/EKS state.
3. Correlates signals across services to identify anomalies.
4. Posts structured findings to the RivetOps control plane.

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
