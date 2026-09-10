# reports/ — sorties des outils de sécurité

Ce dossier reçoit les rapports produits par le pipeline. Il est vide dans
le dépôt : les fichiers sont générés à chaque build et archivés par Jenkins
(`archiveArtifacts`).

| Fichier | Produit par | Étape du pipeline |
|---|---|---|
| `semgrep-report.json` | Semgrep (SAST) | 3 — Security Analysis |
| `npm-audit-report.json` / `.txt` | npm audit (SCA) | 3 — Security Analysis |
| `trivy-report.json` | Trivy (SCA + configuration) | 3 — Security Analysis |
| `gitleaks-report.json` | Gitleaks (Secret Detection) | 4 — Additional Security Check |
| `zap-report.json` / `zap-report.html` | OWASP ZAP (DAST) | 4 — Additional Security Check |
| `security-summary.json` | `scripts/aggregate-reports.py` | 5 — Report Generation |
| `security-summary.html` | `scripts/aggregate-reports.py` | 5 — Report Generation |

`security-summary.json` est le seul fichier consommé par le quality gate :
il contient le décompte par sévérité et la décision de déploiement calculée.

Un exemple de rendu est conservé dans `exemple-security-summary.html`.
