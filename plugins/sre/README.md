# plugins/sre

SRE intelligence plugin for RivetOps. A set of **pi.dev skill files** (markdown) that turn the generic Lambda + pi.dev session into an autonomous SRE monitor: anomaly detection, incident correlation, and plain-English findings with structured output.

No custom tool code. The agent uses `bash` + AWS CLI (available in the Lambda runtime) to read your infrastructure. The skill files describe what to look for and how to report it.

---

## Plugin structure

```
plugins/sre/
├── SKILL.md          # main skill: goals, investigation approach, output contract
├── cloudwatch.md     # how to read metrics and alarms
├── cloudtrail.md     # what to look for in recent API activity
└── correlate.md      # how to connect signals across services into a single finding
```

Loaded by `runtime/aws` as pi.dev skills via the `ResourceLoader`. The agent reads all skill files before starting its investigation.

---

## How the agent works

The agent has `bash` as a built-in tool. It runs AWS CLI commands directly:

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0abc... \
  --start-time $(date -u -d "30 minutes ago" +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 --statistics Average

aws cloudtrail lookup-events \
  --start-time $(date -u -d "1 hour ago" +%Y-%m-%dT%H:%M:%SZ) \
  --lookup-attributes AttributeKey=EventCategory,AttributeValue=Data

aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"
```

The skill files instruct the agent which commands to run, how to interpret the output, and when to escalate a signal to a finding. No TypeScript wrappers to write or maintain.

---

## Output contract (enforced by SKILL.md)

The skill instructs the agent to emit a structured JSON array before terminating. `runtime/aws` parses and validates it.

Fields split into two groups — **fingerprint fields** (deterministic, used for deduplication) and **narrative fields** (variable, excluded from deduplication):

```json
[
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
      "explanation": "Sustained CPU spike with correlated ELB errors suggests an OOM condition or compute-bound loop.",
      "action": "Check application logs on the instance. Review recent deployments.",
      "confidence": 0.91
    }
  }
]
```

`fingerprint = hash(anomaly_type + primary_resource + sorted(correlated_resources) + region)`

Fingerprint is stable across runs. Narrative changes every run and is excluded from the hash.

---

## `anomaly_type` enum

The skill instructs the agent to choose one of the following — not a free-form string:

| Value | Condition |
|-------|-----------|
| `cpu_spike` | Sustained CPU above threshold |
| `memory_pressure` | Memory utilisation above threshold or OOM events |
| `disk_near_full` | Disk utilisation above threshold |
| `error_rate_elevated` | HTTP 5xx or application error rate above threshold |
| `latency_degradation` | P99 latency above threshold |
| `crash_loop` | Repeated process or container restarts |
| `network_anomaly` | Unusual inbound/outbound traffic or dropped packets |
| `config_drift` | CloudTrail mutation event on a sensitive resource |
| `iam_anomaly` | Unusual IAM activity (new role assumption, policy change) |
| `deployment_degradation` | Error rate or latency spike correlated with a recent deploy |
| `cascading_failure` | Degradation across three or more correlated resources |
| `unknown` | Last resort — triggers a human review flag |

New anomaly types: add to the enum in `SKILL.md` and update this README.

---

## Multi-resource (correlated) findings

For cascading or correlated anomalies, the agent populates `correlated_resources` alongside `primary_resource`. The fingerprint uses sorted resource IDs so discovery order does not affect deduplication:

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

---

## SNS message format

`runtime/aws` flattens the finding before publishing so SNS filter policies can route by `severity`:

```json
{
  "anomaly_type": "cpu_spike",
  "primary_resource": "i-0abc123def456789",
  "resource_type": "ec2",
  "region": "us-east-1",
  "severity": "HIGH",
  "signals": ["CPU at 94% for 15 min", "ELB 5xx rate correlated at 12%"],
  "explanation": "...",
  "action": "...",
  "confidence": 0.91,
  "fingerprint": "a3f9c2..."
}
```

`fingerprint` is included so downstream tools (PagerDuty dedup keys, Opsgenie grouping, etc.) can implement their own grouping. RivetOps does not track incident lifecycle — that is the customer's alerting tool's responsibility.

---

## Adding coverage

To add a new service or signal type:
1. Add investigation steps to `SKILL.md` or create a new `<service>.md` skill file.
2. Add a new `anomaly_type` to the enum if needed.
3. Test locally by running `pi` with the skill files loaded against a dev account.

No code changes to `runtime/aws` or `infra/` required.

---

## Status

Planned. Targets the Operational Excellence, Reliability, and Performance pillars.
