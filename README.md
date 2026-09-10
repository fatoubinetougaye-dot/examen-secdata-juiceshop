# Examen Final — Sécurité des Données (L3 Cybersécurité)

Évaluation de sécurité de **OWASP Juice Shop** et intégration de contrôles
automatisés dans un pipeline **Jenkins**.

| | |
|---|---|
| **Étudiant** | Fatou Bintou Gaye |
| **Application évaluée** | OWASP Juice Shop (`bkimminich/juice-shop`) |
| **Application évaluée (cible)** | OWASP Juice Shop v20.2.0 — clonée automatiquement dans `app/` par le pipeline |
| **Modèle du dépôt** | Dépôt autonome (contient Jenkinsfile, security-config, scripts, remediation, reports, screenshots) |
| **Rôle assumé** | Cybersecurity Analyst / Junior DevSecOps Engineer |
| **Contrôles intégrés** | SAST · SCA · Secret Detection · DAST |
| **Décision finale** | 🔴 **Reject Deployment** |

---

## 1. Structure du dépôt

```
project/
├── README.md                     ← ce fichier
├── Jenkinsfile                   ← pipeline déclaratif (6 étapes)
├── docker-compose.yml            ← application cible + outils d'analyse
├── reports/                      ← sorties des outils + rapport consolidé
├── screenshots/                  ← captures d'écran des preuves
├── security-config/              ← règles Semgrep, Gitleaks, ZAP
├── scripts/                      ← agrégation des rapports + quality gate
├── remediation/                  ← code avant/après + preuves de correction
└── docs/                         ← script de la démonstration vidéo
```

---

## 2. Prérequis

| Composant | Version utilisée |
|---|---|
| Windows 11 Professionnel | 24H2 |
| Docker Desktop | 29.4.2 |
| Jenkins | 2.568.2 (service Windows) |
| JDK | 21 |
| Node.js | 20.20.2 (outil Jenkins nommé `Node20`) |
| Python | 3.11+ (scripts d'agrégation) |

Plugins Jenkins requis : `NodeJS`, `Docker Pipeline`, `HTML Publisher`,
`Email Extension`, `Pipeline Utility Steps`, `Timestamper`.

---

## 3. Lancer l'application cible

```bash
docker run -d --name juice-shop -p 3000:3000 bkimminich/juice-shop:latest
```

Application accessible sur `http://localhost:3000`.
Arrêt : `docker rm -f juice-shop`.

Alternative via Compose :

```bash
docker compose up -d juice-shop
```

---

## 4. Lancer les analyses manuellement

### 4.1 SAST — Semgrep

```bash
docker run --rm -v "%cd%:/src" semgrep/semgrep:latest semgrep scan ^
  --config=p/javascript --config=p/typescript --config=p/owasp-top-ten ^
  --config=/src/security-config/semgrep-rules.yml ^
  --json --output=/src/reports/semgrep-report.json --metrics=off /src
```

### 4.2 SCA — npm audit + Trivy

```bash
npm install --legacy-peer-deps --ignore-scripts --no-audit --no-fund
npm audit --json > reports/npm-audit-report.json
npm audit > reports/npm-audit-report.txt

docker run --rm -v "%cd%:/src" aquasec/trivy:latest fs ^
  --scanners vuln,misconfig --format json ^
  --output /src/reports/trivy-report.json /src
```

### 4.3 Secret Detection — Gitleaks

```bash
docker run --rm -v "%cd%:/repo" zricethezav/gitleaks:latest detect ^
  --source=/repo --config=/repo/security-config/gitleaks.toml ^
  --report-format=json --report-path=/repo/reports/gitleaks-report.json --redact
```

### 4.4 DAST — OWASP ZAP

```bash
docker run --rm --add-host=host.docker.internal:host-gateway ^
  -v "%cd%/reports:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable ^
  zap-baseline.py -t http://host.docker.internal:3000 ^
  -J zap-report.json -r zap-report.html -I
```

### 4.5 Consolidation et décision

```bash
python scripts/aggregate-reports.py --input reports --output reports --build 0 --commit local
python scripts/quality-gate.py --report reports/security-summary.json --max-critical 0 --max-high 5
```

Le second script renvoie le code `0` (déploiement autorisé) ou `1`
(déploiement bloqué). C'est ce code qui pilote le statut du build Jenkins.

---

## 5. Exécution via Jenkins

1. **Nouveau item** → *Pipeline* → nom `Examen-SecData-JuiceShop`.
2. *Pipeline script from SCM* → Git → URL = **ce dépôt** (celui qui contient le `Jenkinsfile`)
   → branche `*/main` (ou `*/master`) → *Script Path* : `Jenkinsfile`.
   Le dépôt étant public, aucun credential n'est requis ; l'application cible
   OWASP Juice Shop est ensuite clonée dans `app/` par l'étape 1 du pipeline.
3. *Build Triggers* → cocher **GitHub hook trigger for GITScm polling**
   (le webhook est exposé via `ngrok http 8080`).
4. Renseigner l'adresse de notification dans `NOTIFY_EMAIL` du `Jenkinsfile`.
5. **Build Now**.

Le pipeline exécute les six étapes exigées :

```
1. Checkout  →  2. Build / Preparation  →  3. Security Analysis (SAST ∥ SCA)
→  4. Additional Security Check (Secret Detection ∥ DAST)
→  5. Report Generation  →  Quality Gate  →  6. Notification (post)
```

Le rapport consolidé est publié dans l'interface Jenkins sous
**« Rapport de sécurité consolidé »** et envoyé par e-mail en pièce jointe.

---

## 6. Outils utilisés

| Outil | Type | Ce qu'il détecte | Limites principales | Étape |
|---|---|---|---|---|
| **Semgrep** | SAST | Injections, XSS, crypto faible, secrets, mauvais contrôle d'accès syntaxique | Ne voit pas le comportement à l'exécution ; faux positifs sur les motifs génériques ; ignore les failles de logique métier | 3 |
| **npm audit** | SCA | CVE connues des dépendances npm et de leurs transitives | Ne dit pas si le code vulnérable est réellement appelé ; dépend de la fraîcheur de l'avis npm | 3 |
| **Trivy** | SCA + config | CVE OS/librairies, mauvaises configurations, secrets dans les images | Faible sur le code applicatif métier ; bruit sur les paquets non exposés | 3 |
| **Gitleaks** | Secret Detection | Clés privées, jetons, identifiants dans le code **et l'historique Git** | Aucune vérification de validité du secret ; faux positifs sur les jeux de test | 4 |
| **OWASP ZAP** | DAST | XSS, injections, en-têtes manquants, cookies non sécurisés, exposition d'information | Le mode *baseline* est passif : il ne teste pas les zones authentifiées ni la logique métier | 4 |

---

## 7. Résultat du quality gate

La politique appliquée est : `CRITICAL = 0` et `HIGH ≤ 5`.
L'analyse de Juice Shop dépasse largement ces deux seuils
(injection SQL exploitable, secrets en clair, dépendances critiques),
le pipeline échoue donc volontairement et la décision retenue est
**Reject Deployment**. Ce comportement est attendu : Juice Shop est une
application délibérément vulnérable, et le pipeline démontre qu'il sait
la refuser.

---

## 8. Livrables

| Livrable | Emplacement |
|---|---|
| Rapport de sécurité (PDF, 8–12 pages) | `rapport/Rapport_Securite_Donnees_Fatou_Bintou_Gaye.pdf` |
| Dépôt Git | ce dépôt |
| Script de la démonstration vidéo (5–10 min) | `docs/script-demonstration.md` |
| Captures d'écran | `screenshots/` (liste dans `screenshots/README.md`) |
