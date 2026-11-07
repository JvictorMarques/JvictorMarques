# Animated terminal SVG (SMIL, loops). Usage: python3 assets/terminal.py assets/terminal.svg
import sys, html
CW, LH, X0, Y0, W = 9.0, 22, 24, 72, 760   # char width (monospace 15px), line height
TYPE, AFTER_CMD, AFTER_OUT, HOLD = 0.055, 0.45, 1.1, 4.0
G, FG, MUT, RED, YEL, BLUE = "#3fb950", "#e6edf3", "#7d8590", "#f85149", "#d29922", "#58a6ff"
script = [
  ("cmd", "whoami"),
  ("out", [[("joao-victor", BLUE), (" · cloud infrastructure engineer", FG)]]),
  ("cmd", "terraform plan"),
  ("out", [[("No changes.", G), (" Your infrastructure matches the configuration.", FG)],
           [("# boring, just how I like it", MUT)]]),
  ("cmd", "kubectl get pods -n life"),
  ("out", [[("NAME                            READY   STATUS             RESTARTS", MUT)],
           [("burnout-7d9f8c6b5d-x2kqp        1/1     ", FG), ("Running", G), ("            42", FG)],
           [("personal-life-5f6b9d7c4-m8wzt   0/1     ", FG), ("CrashLoopBackOff", RED), ("   17", FG)]]),
]
# timeline
t, events, row = 0.6, [], 0
for kind, val in script:
    if kind == "cmd":
        events.append(("cmd", row, val, t)); t += len(val) * TYPE + AFTER_CMD; row += 1
    else:
        for ln in val: events.append(("out", row, ln, t)); row += 1
        t += AFTER_OUT
cursor_row, T = row, t + HOLD
H = Y0 + row * LH + 40
kt = lambda s: f"{s / T:.4f}"
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="15">',
  f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="#0d1117" stroke="#30363d"/>',
  f'<path d="M0.5 36 H{W-0.5}" stroke="#30363d"/>',
  *[f'<circle cx="{22+i*20}" cy="18" r="6" fill="{c}"/>' for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"])],
  f'<text x="{W/2}" y="23" text-anchor="middle" fill="{MUT}" font-size="13">jvictor@cloud: ~</text>']
def show(start):  # visible from start until loop end
    return (f'<animate attributeName="opacity" values="0;1;1" keyTimes="0;{kt(start)};1" '
            f'calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite"/>')
for i, (kind, r, val, s) in enumerate(events):
    y = Y0 + r * LH
    if kind == "cmd":
        n = len(val)
        widths = ";".join(f"{(k*CW if k < n else n*CW + 40):.1f}" for k in range(n + 1))  # last step padded so wide fonts aren't clipped
        times = ";".join(["0"] + [kt(s + k * TYPE) for k in range(n + 1)])
        out.append(f'<clipPath id="c{i}"><rect x="{X0+2*CW}" y="{y-16}" height="{LH}" width="0">'
                   f'<animate attributeName="width" values="0;{widths}" keyTimes="{times}" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite"/></rect></clipPath>')
        out.append(f'<g opacity="0">{show(s)}<text x="{X0}" y="{y}" fill="{G}">$</text></g>')
        out.append(f'<text x="{X0+2*CW}" y="{y}" fill="{FG}" clip-path="url(#c{i})" xml:space="preserve">{html.escape(val)}</text>')
    else:
        spans = "".join(f'<tspan fill="{c}">{html.escape(s_)}</tspan>' for s_, c in val)
        out.append(f'<text x="{X0}" y="{y}" opacity="0" xml:space="preserve">{show(s)}{spans}</text>')
y = Y0 + cursor_row * LH
out.append(f'<g opacity="0">{show(t)}<text x="{X0}" y="{y}" fill="{G}">$</text>'
           f'<rect x="{X0+2*CW}" y="{y-14}" width="{CW}" height="17" fill="{FG}">'
           f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect></g>')
out.append("</svg>")
open(sys.argv[1], "w").write("\n".join(out))
print(f"{T:.1f}s loop, {W}x{H}")
