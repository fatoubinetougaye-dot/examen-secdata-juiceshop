#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidation des rapports de sécurité produits par le pipeline Jenkins.

Entrées attendues dans --input :
    semgrep-report.json      (SAST)
    npm-audit-report.json    (SCA)
    trivy-report.json        (SCA)
    gitleaks-report.json     (Secret Detection)
    zap-report.json          (DAST)

Sorties dans --output :
    security-summary.json    (agrégat machine, utilisé par le quality gate)
    security-summary.html    (rapport lisible, publié par Jenkins)

Usage :
    python scripts/aggregate-reports.py --input reports --output reports \
           --build 12 --commit a1b2c3d
"""

import argparse
import datetime
import html
import json
import os
import sys

SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]

SEV_COLORS = {
    "CRITICAL": "#7f1d1d",
    "HIGH": "#b91c1c",
    "MEDIUM": "#c2410c",
    "LOW": "#a16207",
    "INFO": "#334155",
}


def load(path):
    """Charge un JSON en tolérant l'absence ou la corruption du fichier."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read().strip()
        return json.loads(content) if content else None
    except (json.JSONDecodeError, OSError):
        return None


def norm(value, default="INFO"):
    if not value:
        return default
    v = str(value).upper()
    mapping = {
        "ERROR": "HIGH", "WARNING": "MEDIUM", "WARN": "MEDIUM",
        "MODERATE": "MEDIUM", "INFORMATIONAL": "INFO", "NOTE": "LOW",
        "UNKNOWN": "LOW", "NEGLIGIBLE": "LOW",
    }
    v = mapping.get(v, v)
    return v if v in SEVERITIES else default


# ----------------------------------------------------------------------
# Parseurs par outil
# ----------------------------------------------------------------------

def parse_semgrep(data):
    findings = []
    for r in (data or {}).get("results", []):
        extra = r.get("extra", {})
        meta = extra.get("metadata", {})
        cwe = meta.get("cwe")
        if isinstance(cwe, list):
            cwe = ", ".join(cwe)
        findings.append({
            "tool": "Semgrep", "type": "SAST",
            "severity": norm(extra.get("severity")),
            "title": r.get("check_id", "n/a").split(".")[-1],
            "cwe": cwe or "n/a",
            "location": "%s:%s" % (r.get("path", "?"),
                                   r.get("start", {}).get("line", "?")),
            "detail": (extra.get("message") or "")[:400],
        })
    return findings


def parse_npm_audit(data):
    findings = []
    if not data:
        return findings
    for name, adv in (data.get("vulnerabilities") or {}).items():
        via_titles = [v.get("title") for v in adv.get("via", [])
                      if isinstance(v, dict) and v.get("title")]
        cwes = set()
        for v in adv.get("via", []):
            if isinstance(v, dict):
                for c in v.get("cwe", []) or []:
                    cwes.add(c)
        findings.append({
            "tool": "npm audit", "type": "SCA",
            "severity": norm(adv.get("severity")),
            "title": "Dépendance vulnérable : %s" % name,
            "cwe": ", ".join(sorted(cwes)) or "CWE-1395",
            "location": "package.json",
            "detail": "; ".join(via_titles)[:400] or "Avis de sécurité npm",
        })
    return findings


def parse_trivy(data):
    findings = []
    for res in (data or {}).get("Results", []):
        target = res.get("Target", "?")
        for v in res.get("Vulnerabilities", []) or []:
            findings.append({
                "tool": "Trivy", "type": "SCA",
                "severity": norm(v.get("Severity")),
                "title": "%s (%s)" % (v.get("VulnerabilityID", "CVE-?"),
                                      v.get("PkgName", "?")),
                "cwe": ", ".join(v.get("CweIDs", []) or []) or "n/a",
                "location": target,
                "detail": (v.get("Title") or v.get("Description") or "")[:400],
            })
        for m in res.get("Misconfigurations", []) or []:
            findings.append({
                "tool": "Trivy", "type": "SAST",
                "severity": norm(m.get("Severity")),
                "title": m.get("Title", "Mauvaise configuration"),
                "cwe": "CWE-16",
                "location": target,
                "detail": (m.get("Message") or "")[:400],
            })
    return findings


def parse_gitleaks(data):
    findings = []
    for leak in (data or []):
        findings.append({
            "tool": "Gitleaks", "type": "Secret Detection",
            "severity": "CRITICAL",
            "title": "Secret exposé : %s" % leak.get("RuleID", "générique"),
            "cwe": "CWE-798",
            "location": "%s:%s" % (leak.get("File", "?"),
                                   leak.get("StartLine", "?")),
            "detail": "Commit %s — %s" % (str(leak.get("Commit", ""))[:8],
                                          leak.get("Description", "")),
        })
    return findings


def parse_zap(data):
    findings = []
    for site in (data or {}).get("site", []):
        for a in site.get("alerts", []):
            risk = a.get("riskdesc", "").split(" ")[0].upper()
            risk = {"HIGH": "HIGH", "MEDIUM": "MEDIUM",
                    "LOW": "LOW"}.get(risk, "INFO")
            inst = a.get("instances", [])
            findings.append({
                "tool": "OWASP ZAP", "type": "DAST",
                "severity": risk,
                "title": a.get("alert", "Alerte ZAP"),
                "cwe": "CWE-%s" % a.get("cweid", "n/a"),
                "location": inst[0].get("uri", site.get("@name", "?")) if inst
                            else site.get("@name", "?"),
                "detail": "%d instance(s) détectée(s)" % len(inst),
            })
    return findings


# ----------------------------------------------------------------------
# Rendu HTML
# ----------------------------------------------------------------------

def render_html(summary):
    counts = summary["counts"]
    rows = []
    order = {s: i for i, s in enumerate(SEVERITIES)}
    for f in sorted(summary["findings"], key=lambda x: order[x["severity"]]):
        rows.append(
            "<tr>"
            "<td><span class='badge' style='background:%s'>%s</span></td>"
            "<td>%s</td><td>%s</td><td>%s</td><td><code>%s</code></td><td>%s</td>"
            "</tr>" % (
                SEV_COLORS[f["severity"]], f["severity"],
                html.escape(f["tool"]), html.escape(f["type"]),
                html.escape(f["title"]), html.escape(f["location"]),
                html.escape(f["cwe"]),
            )
        )

    cards = "".join(
        "<div class='card'><div class='n' style='color:%s'>%d</div><div>%s</div></div>"
        % (SEV_COLORS[s], counts.get(s, 0), s) for s in SEVERITIES
    )

    return """<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<title>Rapport de sécurité consolidé</title><style>
body{font-family:Segoe UI,Helvetica,Arial,sans-serif;margin:24px;color:#0f172a;background:#f8fafc}
h1{font-size:22px;border-bottom:3px solid #0f172a;padding-bottom:8px}
.meta{font-size:13px;color:#475569;margin-bottom:18px}
.cards{display:flex;gap:12px;margin:18px 0}
.card{flex:1;background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:14px;text-align:center;font-size:12px}
.card .n{font-size:28px;font-weight:700}
table{border-collapse:collapse;width:100%%;background:#fff;font-size:13px}
th{background:#0f172a;color:#fff;text-align:left;padding:8px}
td{border-bottom:1px solid #e2e8f0;padding:7px;vertical-align:top}
code{font-size:11px;color:#334155}
.badge{color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}
.gate{padding:12px;border-radius:8px;font-weight:700;margin:16px 0}
</style></head><body>
<h1>Rapport de sécurité consolidé — OWASP Juice Shop</h1>
<div class="meta">Build #%s &middot; Commit %s &middot; Généré le %s<br>
Contrôles : SAST (Semgrep) &middot; SCA (npm audit + Trivy) &middot;
Secret Detection (Gitleaks) &middot; DAST (OWASP ZAP)</div>
<div class="cards">%s</div>
<div class="gate" style="background:%s;color:#fff">DÉCISION AUTOMATIQUE : %s</div>
<table><thead><tr><th>Sévérité</th><th>Outil</th><th>Type</th>
<th>Problème</th><th>Localisation</th><th>CWE</th></tr></thead>
<tbody>%s</tbody></table></body></html>""" % (
        summary["build"], summary["commit"], summary["generated_at"], cards,
        "#7f1d1d" if summary["gate"] == "REJECT DEPLOYMENT" else "#166534",
        summary["gate"], "".join(rows) or
        "<tr><td colspan='6'>Aucun résultat exploitable.</td></tr>",
    )


# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="reports")
    ap.add_argument("--output", default="reports")
    ap.add_argument("--build", default="0")
    ap.add_argument("--commit", default="n/a")
    args = ap.parse_args()

    i = args.input
    findings = []
    findings += parse_semgrep(load(os.path.join(i, "semgrep-report.json")))
    findings += parse_npm_audit(load(os.path.join(i, "npm-audit-report.json")))
    findings += parse_trivy(load(os.path.join(i, "trivy-report.json")))
    findings += parse_gitleaks(load(os.path.join(i, "gitleaks-report.json")))
    findings += parse_zap(load(os.path.join(i, "zap-report.json")))

    counts = {s: 0 for s in SEVERITIES}
    for f in findings:
        counts[f["severity"]] += 1

    gate = ("REJECT DEPLOYMENT"
            if counts["CRITICAL"] > 0 or counts["HIGH"] > 5
            else "ACCEPT DEPLOYMENT")

    summary = {
        "build": args.build,
        "commit": args.commit,
        "generated_at": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "counts": counts,
        "total": len(findings),
        "gate": gate,
        "findings": findings,
    }

    os.makedirs(args.output, exist_ok=True)
    with open(os.path.join(args.output, "security-summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(args.output, "security-summary.html"), "w",
              encoding="utf-8") as fh:
        fh.write(render_html(summary))

    print("Total : %d résultats — %s" % (len(findings), counts))
    print("Décision proposée : %s" % gate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
