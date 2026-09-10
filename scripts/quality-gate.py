#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality gate de sécurité — décide si le déploiement est autorisé.

Politique appliquée (Partie 5 de l'examen) :
    CRITICAL > MAX_CRITICAL   -> Reject Deployment  (build FAILURE)
    HIGH     > MAX_HIGH       -> Reject Deployment  (build FAILURE)
    sinon                     -> Accept Deployment  (build SUCCESS)

Code de sortie 0 = déploiement autorisé, 1 = déploiement bloqué.
"""

import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="reports/security-summary.json")
    ap.add_argument("--max-critical", type=int, default=0)
    ap.add_argument("--max-high", type=int, default=5)
    args = ap.parse_args()

    try:
        with open(args.report, "r", encoding="utf-8") as fh:
            summary = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print("ERREUR : rapport consolidé illisible (%s)." % exc)
        print("DÉCISION : REJECT DEPLOYMENT (absence de preuve de sécurité)")
        return 1

    counts = summary.get("counts", {})
    crit = counts.get("CRITICAL", 0)
    high = counts.get("HIGH", 0)

    print("=" * 62)
    print("QUALITY GATE DE SÉCURITÉ")
    print("=" * 62)
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
        print("  %-9s : %d" % (sev, counts.get(sev, 0)))
    print("-" * 62)
    print("  Seuils : CRITICAL <= %d | HIGH <= %d"
          % (args.max_critical, args.max_high))

    violations = []
    if crit > args.max_critical:
        violations.append("%d vulnérabilité(s) CRITICAL (seuil : %d)"
                          % (crit, args.max_critical))
    if high > args.max_high:
        violations.append("%d vulnérabilité(s) HIGH (seuil : %d)"
                          % (high, args.max_high))

    if violations:
        print("-" * 62)
        for v in violations:
            print("  [BLOQUANT] %s" % v)
        print("DÉCISION : REJECT DEPLOYMENT")
        print("=" * 62)
        return 1

    print("-" * 62)
    print("DÉCISION : ACCEPT DEPLOYMENT")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
