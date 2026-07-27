"""Generates docs/aws-architecture.svg — run once, commit the output."""

SVG_W, SVG_H = 960, 820

# ── colours ────────────────────────────────────────────────────────────────
C_BG          = "#ffffff"
C_ACCOUNT_BG  = "#fffbf5"
C_ACCOUNT_BD  = "#CD7B2E"
C_ORANGE      = "#FF9900"   # Lambda, EC2
C_PINK        = "#C7166B"   # EventBridge, CloudWatch, CloudTrail, SNS
C_BLUE        = "#3F48CC"   # DynamoDB
C_GREY_BOX    = "#f4f4f4"
C_GREY_BD     = "#cccccc"
C_DARK        = "#1a1a2e"
C_DARK_BD     = "#44446a"
C_TEXT        = "#1a1a2e"
C_MUTED       = "#888888"
C_ARROW       = "#555555"
C_DASH        = "#aaaaaa"

def rect(x, y, w, h, fill, stroke, rx=8, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" {extra}/>'

def text(x, y, s, size=11, weight="normal", fill=C_TEXT, anchor="middle", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" font-family="\'Amazon Ember\',system-ui,sans-serif" {extra}>{s}</text>'

def icon_box(cx, cy, size, color, label, sublabel=None):
    """Coloured square icon with label below."""
    r = size // 2
    lines = [
        rect(cx - r, cy - r, size, size, color, "none", rx=10),
    ]
    label_y = cy + r + 16
    lines.append(text(cx, label_y, label, size=10, weight="600", fill=C_TEXT))
    if sublabel:
        lines.append(text(cx, label_y + 14, sublabel, size=9, fill=C_MUTED))
    return "\n".join(lines)

def pill(cx, cy, w, h, label, fill=C_GREY_BOX, stroke=C_GREY_BD, tcolor=C_TEXT, tsize=10):
    x = cx - w // 2
    y = cy - h // 2
    return f"""
{rect(x, y, w, h, fill, stroke, rx=6)}
{text(cx, cy + 4, label, size=tsize, fill=tcolor)}"""

def arrow(x1, y1, x2, y2, dashed=False, label=None, lx=None, ly=None):
    dash = 'stroke-dasharray="5,4"' if dashed else ""
    color = C_DASH if dashed else C_ARROW
    lw = "1.2" if dashed else "1.8"
    parts = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{lw}" {dash} marker-end="url(#arr{"d" if dashed else ""})"/>',
    ]
    if label:
        lx = lx or (x1 + x2) // 2 + 6
        ly = ly or (y1 + y2) // 2 - 4
        parts.append(text(lx, ly, label, size=9, fill=C_MUTED))
    return "\n".join(parts)

def vline(x, y1, y2, dashed=False):
    return arrow(x, y1, x, y2, dashed)

def hline(x1, y, x2, dashed=False):
    return arrow(x1, y, x2, y, dashed)

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">
<defs>
  <!-- solid arrowhead -->
  <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <path d="M0,0 L0,6 L8,3 z" fill="{C_ARROW}"/>
  </marker>
  <!-- dashed arrowhead -->
  <marker id="arrd" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <path d="M0,0 L0,6 L8,3 z" fill="{C_DASH}"/>
  </marker>
</defs>

<!-- white background -->
<rect width="{SVG_W}" height="{SVG_H}" fill="{C_BG}"/>

<!-- ── AWS Account boundary ───────────────────────────────────────────── -->
{rect(30, 30, 740, 660, C_ACCOUNT_BG, C_ACCOUNT_BD, rx=12)}
<text x="50" y="58" font-size="12" font-weight="700" fill="{C_ACCOUNT_BD}" font-family="'Amazon Ember',system-ui,sans-serif">Customer AWS Account</text>

<!-- ── EventBridge ────────────────────────────────────────────────────── -->
{icon_box(400, 110, 48, C_PINK, "EventBridge Scheduler", "every 5 min")}

<!-- EventBridge → Lambda -->
{vline(400, 138, 218)}

<!-- ── Lambda ─────────────────────────────────────────────────────────── -->
{icon_box(400, 240, 56, C_ORANGE, "Lambda")}
{text(400, 312, "runtime/aws  +  plugins/sre", size=9, fill=C_MUTED)}

<!-- ── Data sources (left) ────────────────────────────────────────────── -->
{text(145, 218, "reads own account", size=9, fill=C_MUTED, weight="600")}

{icon_box(90,  270, 42, C_PINK,   "CloudWatch")}
{icon_box(185, 270, 42, C_PINK,   "CloudTrail")}
{icon_box(283, 270, 42, C_ORANGE, "EC2 / ECS / EKS")}

<!-- Lambda → data sources -->
{arrow(372, 248, 116, 252)}
{arrow(372, 250, 198, 253)}
{arrow(372, 252, 303, 254)}

<!-- ── DynamoDB (right) ───────────────────────────────────────────────── -->
{icon_box(590, 230, 48, C_BLUE, "DynamoDB", "alert suppression")}

<!-- Lambda ↔ DynamoDB -->
<line x1="428" y1="238" x2="562" y2="222" stroke="{C_ARROW}" stroke-width="1.8" marker-end="url(#arr)" marker-start="url(#arr)"/>

<!-- ── SNS ────────────────────────────────────────────────────────────── -->
{icon_box(590, 390, 48, C_PINK, "SNS Topic", "findings")}

<!-- Lambda → SNS -->
{arrow(428, 262, 562, 372)}

<!-- ── Notification targets ───────────────────────────────────────────── -->
{text(590, 468, "subscribe your endpoints", size=9, fill=C_MUTED)}

{pill(490, 520, 100, 34, "PagerDuty")}
{pill(608, 520, 80,  34, "Email")}
{pill(710, 520, 80,  34, "SQS")}

<!-- SNS → targets -->
{arrow(570, 418, 508, 504, dashed=True)}
{arrow(590, 418, 608, 504, dashed=True)}
{arrow(614, 418, 700, 504, dashed=True)}

<!-- AWS Chatbot note -->
{pill(710, 580, 120, 32, "AWS Chatbot → Slack", fill="#eef4ff", stroke="#8899cc", tsize=9)}
{arrow(710, 537, 710, 564, dashed=True)}

<!-- ── RivetOps Dashboard (outside account) ───────────────────────────── -->
{rect(820, 200, 110, 290, C_DARK, C_DARK_BD, rx=10)}
<text x="875" y="228" font-size="11" font-weight="700" fill="#ffffff" text-anchor="middle" font-family="'Amazon Ember',system-ui,sans-serif">RivetOps</text>
<text x="875" y="244" font-size="11" font-weight="700" fill="#ffffff" text-anchor="middle" font-family="'Amazon Ember',system-ui,sans-serif">Dashboard</text>
<text x="875" y="268" font-size="9" fill="#9999cc" text-anchor="middle" font-family="'Amazon Ember',system-ui,sans-serif">historical view</text>
<text x="875" y="282" font-size="9" fill="#9999cc" text-anchor="middle" font-family="'Amazon Ember',system-ui,sans-serif">multi-account</text>
<text x="875" y="296" font-size="9" fill="#9999cc" text-anchor="middle" font-family="'Amazon Ember',system-ui,sans-serif">richer UI</text>
<line x1="875" y1="310" x2="875" y2="332" stroke="#44446a" stroke-width="1" stroke-dasharray="3,3"/>
<text x="875" y="356" font-size="9" fill="#6666aa" text-anchor="middle" font-family="'Amazon Ember',system-ui,sans-serif">optional</text>
<text x="875" y="370" font-size="9" fill="#6666aa" text-anchor="middle" font-family="'Amazon Ember',system-ui,sans-serif">HTTPS POST</text>
<text x="875" y="450" font-size="9" fill="#6666aa" text-anchor="middle" font-family="'Amazon Ember',system-ui,sans-serif">closed source</text>

<!-- Lambda - - → Dashboard -->
{arrow(428, 254, 816, 310, dashed=True, label="optional")}

<!-- ── Legend ─────────────────────────────────────────────────────────── -->
<rect x="30" y="720" width="740" height="1" fill="{C_GREY_BD}"/>
<text x="50" y="748" font-size="9" fill="{C_MUTED}" font-family="'Amazon Ember',system-ui,sans-serif">MIT licensed · runs entirely in your account · RivetOps never touches your infrastructure · github.com/TheAdamLabs/rivetops-agent</text>

</svg>
"""

out = "/Users/adam.pavlat/projects/RivetOps/rivetops-agent/docs/aws-architecture.svg"
with open(out, "w") as f:
    f.write(svg)
print(f"Written {out}")
