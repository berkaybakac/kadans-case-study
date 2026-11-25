"""Generate the case-study diagrams in light and dark themes.

Run: python3 assets/src/diagrams.py  (writes assets/<name>-{light,dark}.svg)
Edit text and layout here; never edit the generated SVG files by hand.
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent

THEMES = {
    "light": dict(
        bg="#ffffff", surface="#f6f8fa", card="#ffffff", ink="#1f2328", muted="#59636e",
        line="#d1d9e0", arrow="#818b98", server="#4f46e5", server_tint="#eef0fe",
        pi="#a21caf", pi_tint="#fbeefc", amber="#b45309", amber_tint="#fdf3e6",
        red="#c2410c", red_tint="#fdefe8", on_accent="#ffffff",
    ),
    "dark": dict(
        bg="#0d1117", surface="#151b23", card="#1c2129", ink="#e6edf3", muted="#9198a1",
        line="#3d444d", arrow="#768390", server="#8f94fb", server_tint="#1b1d3d",
        pi="#e17ff0", pi_tint="#2c1530", amber="#f0a742", amber_tint="#2d2010",
        red="#f0805a", red_tint="#2e1812", on_accent="#0d1117",
    ),
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"


class Svg:
    def __init__(self, w, h, title, t):
        self.w, self.h, self.t = w, h, t
        self.parts = []
        self.title = title

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=14, color="ink", weight=400, anchor="start", extra=""):
        self.add(
            f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{self.t[color]}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'
        )

    def lines(self, x, y, rows, size=14, color="muted", gap=20, **kw):
        for i, row in enumerate(rows):
            self.text(x, y + i * gap, row, size=size, color=color, **kw)

    def rect(self, x, y, w, h, fill="card", stroke="line", rx=12, dash=None, sw=1.2):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{self.t[fill]}" '
            f'stroke="{self.t[stroke]}" stroke-width="{sw}"{d}/>'
        )

    def path(self, d, color="arrow", width=1.8, dash=None, head=True, both=False):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#h-{color})"' if head else ""
        if both:
            m += f' marker-start="url(#h-{color})"'
        self.add(
            f'<path d="{d}" fill="none" stroke="{self.t[color]}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{dd}{m}/>'
        )

    def card(self, x, y, w, h, title, body, accent, number=None, dash=None, size=14):
        self.rect(x, y, w, h, dash=dash)
        if not dash:
            self.add(f'<rect x="{x}" y="{y + 12}" width="4" height="{h - 24}" rx="2" fill="{self.t[accent]}"/>')
        tx = x + 20
        if number is not None:
            self.add(f'<circle cx="{x + 32}" cy="{y + 29}" r="13" fill="{self.t[accent]}"/>')
            self.text(x + 32, y + 34, str(number), size=13, color="on_accent", weight=700, anchor="middle")
            tx = x + 54
        self.text(tx, y + 34, title, size=16, weight=650, color="muted" if dash else "ink")
        self.lines(x + 20, y + 62, body, size=size)

    def render(self):
        markers = "".join(
            f'<marker id="h-{c}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{self.t[c]}"/></marker>'
            for c in ("arrow", "server", "pi", "amber", "red")
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" font-family="{FONT}">'
            f"<title>{escape(self.title)}</title><defs>{markers}</defs>"
            f'<rect width="{self.w}" height="{self.h}" rx="16" fill="{self.t["bg"]}" stroke="{self.t["line"]}"/>'
            + "".join(self.parts)
            + "</svg>\n"
        )


def header(s, title, subtitle):
    s.text(40, 54, title, size=26, weight=700)
    s.text(40, 82, subtitle, size=15, color="muted")


def legend(s, x, y, items):
    for color, label, dash in items:
        s.path(f"M{x} {y} H{x + 34}", color=color, width=2.6, dash=dash, head=False)
        s.text(x + 44, y + 5, label, size=13, color="muted")
        x += 54 + len(label) * 7.1


COLS = (40, 274, 508, 742, 976)
CW = 204


def price_to_speaker(t):
    s = Svg(1200, 690, "From a price change in the ERP to an announcement in the store", t)
    header(s, "From a price change to the speaker", "Fully automatic: facts come from the ERP, words from the model, every number from code.")
    legend(s, 700, 50, [("server", "Kadans server", None), ("amber", "Tellal", None), ("pi", "Branch Pi", None)])
    steps = [
        ("server", "ERP price drops", ["Go collector reads the", "customer's SQL Server", "ERP per branch"]),
        ("server", "Facts verified", ["product, old and new", "price, validity: checked", "in code, not by a model"]),
        ("amber", "Model writes copy", ["a Turkish template", "with placeholders only,", "never a number"]),
        ("amber", "Guard, then fill", ["any digit is rejected;", "code inserts the prices", "and the dates"]),
        ("amber", "Speech", ["one voice; rejected copy", "falls back to a verified", "sentence, same voice"]),
        ("server", "Loudness", ["normalized to −16 LUFS", "and −1.5 dBTP,", "48 kHz MP3"]),
        ("server", "Stored by hash", ["named by its SHA-256,", "stored once for every", "branch with the discount"]),
        ("server", "New plan revision", ["declarative, versioned,", "byte-stable; no play", "command exists"]),
        ("pi", "Hint, then pull", ["MQTT: “new revision”;", "HTTPS fetch, every file", "verified by its hash"]),
        ("pi", "Duck and play", ["only if hours, prayer", "silence and a trusted", "clock all allow it"]),
    ]
    for i, (accent, title, body) in enumerate(steps):
        row, col = divmod(i, 5)
        x, y = COLS[col], 112 + row * 160
        s.card(x, y, CW, 122, title, body, accent, number=i + 1)
        if col < 4:
            s.path(f"M{x + CW + 5} {y + 61} H{COLS[col + 1] - 7}")
    s.path(f"M{COLS[4] + CW / 2} 239 V256 H{COLS[0] + CW / 2} V266")

    # Ducking chart for step 10.
    top, base = 470, 600
    y100, y25 = top + 22, top + 22 + 0.75 * (base - top - 22)
    s.text(40, 452, "Step 10, up close: the music ducks under the announcement", size=16, weight=650)
    s.rect(420, top, 400, base - top, fill="amber_tint", stroke="amber_tint", rx=8)
    s.text(620, top + 74, "announcement plays", size=14, color="amber", weight=600, anchor="middle")
    s.path(f"M820 {top - 6} V{base}", color="amber", width=1.4, dash="4 4", head=False)
    s.text(828, top + 8, "player exits", size=13, color="amber", weight=600)
    s.path(f"M120 {base} H1160", color="line", width=1.2, head=False)
    s.text(108, y100 + 5, "100", size=13, color="muted", anchor="end")
    s.text(108, y25 + 5, "25", size=13, color="muted", anchor="end")
    s.text(40, (y100 + y25) / 2 + 5, "Music", size=13, color="muted")
    s.path(
        f"M120 {y100} H330 L420 {y25} H820 L1000 {y100} H1160",
        color="pi", width=3.4, head=False,
    )
    s.text(375, base + 22, "700 ms", size=13, color="muted", anchor="middle")
    s.text(910, base + 22, "1400 ms", size=13, color="muted", anchor="middle")
    s.text(1160, 452, "Music returns only after the player really exits, not after an estimated duration.", size=13, color="muted", anchor="end")
    s.text(120, base + 22, "claim, then duck", size=13, color="muted")
    return s


def architecture(t):
    s = Svg(1200, 770, "Architecture of Kadans and Tellal", t)
    header(
        s, "Where everything runs",
        "Everything a store needs lives on the customer's network. The cloud generates speech, watches the fleet and serves releases.",
    )
    s.rect(24, 104, 770, 600, fill="surface", dash="6 5", rx=16)
    s.rect(818, 104, 358, 600, fill="surface", dash="6 5", rx=16)
    s.text(44, 132, "CUSTOMER NETWORK · VPN", size=12.5, color="muted", weight=700, extra=' letter-spacing="1"')
    s.text(838, 132, "CLOUD", size=12.5, color="muted", weight=700, extra=' letter-spacing="1"')

    s.card(48, 156, 240, 88, "Customer ERP", ["SQL Server, read-only"], "muted")
    s.card(48, 296, 240, 88, "Headquarters panel", ["React · TypeScript"], "muted")

    s.card(360, 156, 410, 268, "Kadans server", ["one Windows service on the customer's machine"], "server", size=13.5)
    rows = [
        "FastAPI · PostgreSQL · audio store",
        "Go: ERP collector · prayer-time sync",
        "Go: MQTT 5 broker · fleet uplink",
        "Caddy TLS · nightly backup · self-update",
    ]
    for i, r in enumerate(rows):
        y = 238 + i * 44
        s.rect(382, y, 366, 36, fill="server_tint", stroke="server_tint", rx=8)
        s.text(398, y + 23, r, size=14)

    s.path("M288 200 H354")
    s.text(321, 190, "SQL", size=12.5, color="muted", anchor="middle")
    s.path("M294 340 H354", both=True)
    s.text(324, 330, "HTTPS", size=12.5, color="muted", anchor="middle")

    # Branch players.
    s.rect(360, 548, 410, 136, fill="card", stroke="line", rx=12)
    s.add(f'<rect x="360" y="560" width="4" height="112" rx="2" fill="{t["pi"]}"/>')
    s.text(380, 576, "Branch players · Raspberry Pi", size=16, weight=650)
    for i, (title, body, dash) in enumerate([
        ("Branch", ["mpv · cache", "pure decide()"], None),
        ("Branch", ["mpv · cache", "pure decide()"], None),
        ("Next branch", ["passive, ready", "for its first Pi"], "5 4"),
    ]):
        x = 380 + i * 128
        s.rect(x, 592, 118, 80, fill="pi_tint" if not dash else "card", stroke="pi_tint" if not dash else "line", rx=8, dash=dash)
        s.text(x + 12, 614, title, size=14, weight=650, color="muted" if dash else "ink")
        s.lines(x + 12, 636, body, size=12.5, gap=18)

    for x, color, dash, up, label in [
        (392, "server", None, False, ["plans + audio", "HTTPS pull"]),
        (500, "pi", "6 5", False, ["revision hint", "MQTT"]),
        (604, "pi", "6 5", True, ["presence,", "live state"]),
        (700, "server", None, True, ["evidence", "HTTPS"]),
    ]:
        d = f"M{x} 542 V430" if up else f"M{x} 430 V542"
        s.path(d, color=color, width=2.2, dash=dash)
        s.lines(x + 9, 480, label, size=12.5, gap=17)

    s.card(840, 156, 312, 120, "Tellal · AI platform", ["Claude copy behind guardrails", "ElevenLabs speech", "prepaid balances · spend caps"], "amber")
    s.card(840, 306, 312, 92, "Fleet hub", ["health reports · Prometheus · Grafana"], "muted", size=13.5)
    s.card(840, 428, 312, 92, "Signed releases", ["Ed25519 · office canary first"], "muted", size=13.5)
    s.card(840, 550, 312, 92, "Support files · backups", ["backups sealed to the owner's key"], "muted", size=13.5)

    s.path("M770 196 H834", color="amber", width=2.2)
    s.text(804, 188, "facts", size=12.5, color="amber", anchor="middle")
    s.path("M840 236 H776", color="amber", width=2.2)
    s.text(808, 254, "MP3", size=12.5, color="amber", anchor="middle")
    s.path("M770 352 H806 V596", head=False)
    for y in (352, 474, 596):
        s.path(f"M806 {y} H834")
    s.text(838, 676, "Every cloud link starts at the customer server.", size=12.5, color="muted")

    legend(s, 40, 738, [
        ("server", "data plane: HTTPS, authoritative", None),
        ("pi", "control plane: MQTT 5, hints only", "6 5"),
        ("amber", "generation", None),
        ("arrow", "outbound only", None),
    ])
    return s


def releases(t):
    s = Svg(1200, 420, "How a release reaches the stores, and what happens when it fails", t)
    header(s, "Safe releases", "After the first installation, nobody at the customer runs a setup program again.")
    steps = [
        ("server", "Windows checks", ["clean runners: fresh,", "every upgrade path,", "rolled-back updates"]),
        ("server", "Sign", ["Ed25519 key that", "never leaves the", "owner's machine"]),
        ("server", "Office canary", ["installs it first and", "reports the outcome", "to the fleet hub"]),
        ("server", "Customers, at night", ["each customer server,", "03:15, only the release", "the canary installed"]),
        ("pi", "Players follow", ["each Pi updates from", "its own server, only", "if its code changed"]),
    ]
    legend(s, 820, 50, [("server", "release and server", None), ("pi", "branch players", None)])
    for i, (accent, title, body) in enumerate(steps):
        x = COLS[i]
        s.card(x, 112, CW, 122, title, body, accent, number=i + 1)
        if i < 4:
            s.path(f"M{x + CW + 5} 173 H{COLS[i + 1] - 7}")
    s.text(40, 300, "If it fails", size=16, weight=650, color="red")
    s.lines(40, 324, ["each layer stops", "or undoes itself"], size=13.5)
    fails = [
        (2, ["stores are never", "offered that release"]),
        (3, ["the installer rolls back", "and reports why"]),
        (4, ["no healthy player in 90 s:", "switch back to the old one"]),
    ]
    for col, body in fails:
        x = COLS[col]
        s.path(f"M{x + CW / 2} 240 V{276}", color="red", width=1.8, dash="4 4")
        s.rect(x, 282, CW, 76, fill="red_tint", stroke="red_tint", rx=10)
        s.lines(x + 16, 312, body, size=13.5, color="ink", gap=21)
    return s


def main():
    for name, build in [("price-to-speaker", price_to_speaker), ("architecture", architecture), ("releases", releases)]:
        for theme, t in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(build(t).render(), encoding="utf-8")


if __name__ == "__main__":
    main()
