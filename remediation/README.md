# remediation/ — corrections et preuves de vérification

Quatre vulnérabilités ont été corrigées (le sujet en demande trois au
minimum). Chaque dossier contient le code fautif, le code corrigé et la
démarche de vérification.

| Dossier | Vulnérabilité | CWE | Sévérité | Correction principale |
|---|---|---|---|---|
| `V1-sql-injection/` | Contournement d'authentification par injection SQL | CWE-89 | Critical | Requêtes paramétrées (`replacements`) + validation d'entrée |
| `V2-xss-dom/` | XSS DOM dans la barre de recherche | CWE-79 | High | Suppression de `bypassSecurityTrustHtml` + interpolation + CSP |
| `V3-idor-basket/` | Accès au panier d'un autre utilisateur | CWE-639 | High | Contrôle d'appartenance côté serveur à partir du JWT |
| `V4-password-hashing/` | Mots de passe hachés en MD5 sans sel | CWE-916 | Critical | bcrypt coût 12 + politique de mot de passe + migration |

## Contenu de chaque dossier

- `before.ts` — extrait du code vulnérable, avec la cause commentée ;
- `after.ts` — code corrigé, chaque mesure numérotée en en-tête ;
- `verification.md` — rejeu de l'attaque, non-régression fonctionnelle et
  confrontation des résultats des outils avant/après.

## Méthode de vérification appliquée

Une correction n'est considérée comme valide que si les quatre conditions
suivantes sont réunies :

1. **L'attaque ne fonctionne plus** — la charge utile d'origine et ses
   variantes sont rejouées et échouent.
2. **La fonctionnalité légitime est préservée** — un cas d'usage normal est
   testé pour écarter toute régression.
3. **L'outil qui avait signalé le problème ne le signale plus** — Semgrep,
   ZAP ou Gitleaks selon la vulnérabilité.
4. **Un test automatisé verrouille la correction** — pour empêcher la
   réintroduction de la faille lors d'une évolution ultérieure.
