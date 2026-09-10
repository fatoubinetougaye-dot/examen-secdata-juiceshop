# Script de la démonstration vidéo (5 à 10 minutes)

Enregistrement écran + voix. Chronométrage indicatif ci-dessous.

---

## 0:00 — 0:40 · Introduction (40 s)

- Se présenter : Fatou Bintou Gaye, L3 Cybersécurité, examen final Sécurité des Données.
- Annoncer le plan : application, vulnérabilités, remédiations, pipeline,
  résultats, décision.
- Rappeler le rôle assumé : *Cybersecurity Analyst / Junior DevSecOps Engineer*.

## 0:40 — 1:40 · L'application (1 min)

- Montrer `http://localhost:3000` — OWASP Juice Shop en fonctionnement.
- Préciser : application volontairement vulnérable publiée par l'OWASP,
  pile Node.js / Express / Angular / SQLite, utilisée ici comme cible
  d'évaluation avant une mise en production fictive.
- Montrer la commande de lancement :
  `docker run -d --name juice-shop -p 3000:3000 bkimminich/juice-shop:latest`.

## 1:40 — 3:30 · Principaux problèmes identifiés (1 min 50)

Enchaîner trois démonstrations rapides, sans commenter le code :

1. **Injection SQL (V1, CWE-89)** — saisir `' OR 1=1--` dans le champ e-mail,
   n'importe quel mot de passe → session administrateur ouverte.
2. **XSS DOM (V2, CWE-79)** — coller
   `#/search?q=<iframe src="javascript:alert(\`xss\`)">` → boîte d'alerte.
3. **IDOR (V3, CWE-639)** — DevTools, onglet Réseau, requêter
   `/rest/basket/2` avec le jeton d'un autre compte → `200 OK`.

Afficher ensuite le tableau récapitulatif des 8 vulnérabilités du rapport
(2 s à l'écran suffisent).

## 3:30 — 5:00 · Remédiations (1 min 30)

- Ouvrir `remediation/V1-sql-injection/before.ts` puis `after.ts` :
  montrer le passage de l'interpolation aux `replacements`.
- Rejouer le payload `' OR 1=1--` sur la version corrigée → `401`.
- Montrer rapidement `V4-password-hashing/after.ts` : MD5 → bcrypt coût 12.
- Insister : la vérification n'est pas seulement « l'attaque échoue »,
  c'est aussi « la fonctionnalité marche encore » et « l'outil ne remonte
  plus le finding ».

## 5:00 — 7:00 · Le pipeline Jenkins (2 min)

- Montrer le `Jenkinsfile` : les 6 étapes.
- Lancer un build (ou montrer un build déjà terminé) : la *Stage View*.
- Ouvrir la console sur chaque étape d'analyse :
  Semgrep (SAST), npm audit (SCA), Gitleaks (secrets), ZAP (DAST).
- Souligner le parallélisme des étapes 3 et 4 (gain de temps).

## 7:00 — 8:30 · Résultats (1 min 30)

- Ouvrir le rapport consolidé HTML publié par Jenkins :
  décompte par sévérité, tableau trié, ligne de décision.
- Montrer l'e-mail de notification reçu avec le rapport en pièce jointe.
- Rappeler les chiffres clés : 46 vulnérabilités de dépendances
  (8 critiques, 20 élevées, 15 modérées, 3 faibles) + les findings SAST,
  secrets et DAST.

## 8:30 — 9:30 · Décision finale (1 min)

- Montrer la console du quality gate : `REJECT DEPLOYMENT`.
- Justifier : présence de vulnérabilités critiques exploitables touchant
  directement la confidentialité et l'intégrité des données utilisateurs ;
  le seuil `CRITICAL = 0` est violé.
- Conclure sur la Partie 6 : aucun outil ne prouve l'absence de
  vulnérabilité ; l'analyse humaine reste indispensable.

## 9:30 — 10:00 · Clôture (30 s)

- Rappeler l'adresse du dépôt Git et la présence du rapport PDF.
- Remercier.

---

## Points de vigilance pour l'enregistrement

- Fermer les onglets et notifications personnels avant de lancer la capture.
- Vérifier que l'audio est audible sur toute la durée (test de 10 s).
- Ne pas dépasser 10 minutes : couper les temps d'attente (installation,
  démarrage du conteneur) au montage.
- Masquer toute adresse e-mail réelle et tout mot de passe d'application
  SMTP à l'écran.
