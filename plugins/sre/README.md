# plugins/sre

SRE intelligence plugin for RivetOps. Loaded by `runtime/aws` at invocation time - turns the generic Lambda shell into an autonomous SRE monitor: anomaly detection, incident correlation, and plain-English findings.

## What it does

1. Reads CloudWatch metrics, CloudTrail events, and EC2/ECS/EKS state using the Lambda's own IAM execution role (no cross-account - the Lambda runs in the customer's account).
2. Correlates signals across services to identify anomalies.
3. Returns a **structured finding** to `runtime/aws`, which uses it for deduplication before publishing to SNS.

---

## Finding schema

The plugin forces the LLM to emit structured JSON. Fields are split into two groups:

**Fingerprint fields** — deterministic, used by `runtime/aws` for deduplication. The LLM must populate these from a constrained set of values (enums). They describe *what* is wrong, not *how* it looks in text.

**Narrative fields** — variable, excluded from deduplication. The LLM generates these freely.

```json
{
  "schema_version": "1",

  "fingerprint_fields": {
    "anomaly_type": "cpu_spike",
    "primary_resource": "i-0abc123def456789",
    "resource_type": "ec2",
    "region": "us-east-1",
    "correlated_resources": []
  },

  "narrative_fields": {
    "severity": "HIGH",
    "signals": [
      "CPU at 94% for 15 min (threshold: 85%)",
      "ELB 5xx rate correlated at 12%"
    ],
    "explanation": "Sustained CPU spike with correlated ELB errors suggests an OOM condition or compute-bound loop. Possible memory leak or recent code change.",
    "action": "Check application logs on the instance. Review recent deployments. Consider a memory profile or instance resize.",
    "confidence": 0.91,
    "context_tokens": 4812
  }
}
```

`fingerprint = hash(anomaly_type + primary_resource + sorted(correlated_resources) + region)`

This fingerprint is stable across runs. The narrative changes every run; it is excluded.

---

## `anomaly_type` enum

The LLM must choose one of the following. Choosing the closest match is required — the LLM cannot emit a free-form string here.

| Value | Condition |
|-------|-----------|
| `cpu_spike` | Sustained CPU above threshold |
| `memory_pressure` | Memory utilisation above threshold or OOM events |
| `disk_near_full` | Disk utilisation above threshold |
| `error_rate_elevated` | HTTP 5xx or application error rate above threshold |
| `latency_degradation` | P99 latency above threshold |
| `crash_loop` | Repeated process restarts / container restarts |
| `network_anomaly` | Unusual inbound/outbound traffic or dropped packets |
| `config_drift` | CloudTrail mutation event on a sensitive resource |
| `iam_anomaly` | Unusual IAM activity (new role assumption, policy change) |
| `deployment_degradation` | Error rate or latency spike correlated with a recent deploy event |
| `cascading_failure` | Degradation across three or more correlated resources |
| `unknown` | Last resort — triggers a human review flag |

New anomaly types are added here as the plugin expands coverage.

---

## Multi-resource (correlated) findings

For cascading or correlated anomalies, the plugin populates `correlated_resources` alongside `primary_resource`. The fingerprint uses sorted resource IDs so the order the agent discovers them does not affect deduplication:

```json
{
  "fingerprint_fields": {
    "anomaly_type": "cascading_failure",
    "primary_resource": "arn:aws:elasticloadbalancing:us-east-1:123:loadbalancer/app/prod",
    "resource_type": "alb",
    "region": "us-east-1",
    "correlated_resources": [
      "i-0abc123def456789",
      "i-0def456ghi789012"
    ]
  }
}
```

`fingerprint = hash("cascading_failure" + alb_arn + "i-0abc..." + "i-0def..." + "us-east-1")`

---

## SNS message

`runtime/aws` flattens the finding before publishing so SNS filter policies can route by `severity`:

```json
{
  "anomaly_type": "cpu_spike",
  "primary_resource": "i-0abc123def456789",
  "resource_type": "ec2",
  "region": "us-east-1",
  "severity": "HIGH",
  "state": "OPEN",
  "signals": ["CPU at 94% for 15 min", "ELB 5xx rate correlated at 12%"],
  "explanation": "...",
  "action": "...",
  "confidence": 0.91,
  "fingerprint": "a3f9c2..."
}
```

`state` is set by `runtime/aws` based on DynamoDB deduplication state (`OPEN`, `RE_ALERT`, `RESOLVED`) — the plugin itself does not set it.

---

## Status

Active development. Targets the Operational Excellence, Reliability, and Performance pillars.
