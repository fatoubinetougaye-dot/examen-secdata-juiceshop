# screenshots/ — captures d'écran à produire

Nommer les fichiers selon la convention `NN-description.png` pour que
l'ordre de lecture corresponde au déroulé du rapport.

## Partie 1 — Identification des vulnérabilités

| Fichier | Contenu attendu |
|---|---|
| `01-juiceshop-accueil.png` | Page d'accueil de l'application sur `localhost:3000` |
| `02-sqli-payload.png` | Formulaire de connexion avec `' OR 1=1--` saisi |
| `03-sqli-succes-admin.png` | Session ouverte en tant qu'`admin@juice-sh.op` |
| `04-xss-payload-url.png` | URL `#/search?q=<iframe src="javascript:alert(\`xss\`)">` |
| `05-xss-alerte.png` | Boîte d'alerte JavaScript déclenchée |
| `06-idor-basket-devtools.png` | Onglet Réseau : `GET /rest/basket/2` renvoyant `200` |
| `07-ftp-listing.png` | Listing du répertoire `/ftp` |
| `08-ftp-null-byte.png` | Téléchargement de `coupons_2013.md.bak` via `%2500.md` |
| `09-md5-hash-base.png` | Hachés MD5 visibles dans la table `Users` |
| `10-jwt-decode.png` | Jeton JWT décodé sur jwt.io (algorithme + charge utile) |

## Partie 4 — Pipeline Jenkins

| Fichier | Contenu attendu |
|---|---|
| `11-jenkins-pipeline-config.png` | Configuration *Pipeline script from SCM* |
| `12-jenkins-stage-view.png` | Vue des étapes : les 6 stages + Quality Gate |
| `13-console-semgrep.png` | Sortie console de l'étape SAST |
| `14-console-npm-audit.png` | Sortie console de l'étape SCA (46 vulnérabilités) |
| `15-console-gitleaks.png` | Sortie console de la détection de secrets |
| `16-console-zap.png` | Sortie console du scan ZAP baseline |
| `17-rapport-consolide.png` | Page HTML « Rapport de sécurité consolidé » |
| `18-quality-gate-fail.png` | Console du quality gate : `REJECT DEPLOYMENT` |
| `19-email-notification.png` | E-mail reçu avec le rapport en pièce jointe |
| `20-webhook-github.png` | Build déclenché par `Started by GitHub push by fatoubinetougaye-dot` |

## Partie 3 — Vérification des remédiations

| Fichier | Contenu attendu |
|---|---|
| `21-sqli-apres-401.png` | Même payload SQLi renvoyant `401 Unauthorized` |
| `22-xss-apres-encode.png` | Payload XSS affiché littéralement dans la page |
| `23-idor-apres-404.png` | `GET /rest/basket/2` renvoyant `404` |
| `24-headers-apres.png` | En-têtes de sécurité présents (`curl -I`) |
| `25-semgrep-apres.png` | Semgrep : 0 finding sur les règles corrigées |
