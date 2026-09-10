# V1 — Vérification de la correction (SQL Injection, CWE-89)

## 1. Test manuel de non-régression de l'attaque

Requête d'exploitation utilisée avant correction :

```bash
curl -s -X POST http://localhost:3000/rest/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"'"'"' OR 1=1--","password":"x"}'
```

| Étape | Réponse HTTP | Corps de la réponse |
|---|---|---|
| Avant correction | `200 OK` | Jeton JWT du premier compte de la table (`admin@juice-sh.op`) |
| Après correction | `401 Unauthorized` | `Identifiants invalides.` |

Variantes également rejouées et rejetées : `admin@juice-sh.op'--`,
`' UNION SELECT 1,2,3,4,5,6,7,8,9--`, `' OR '1'='1`.

## 2. Test de non-régression fonctionnelle

```bash
curl -s -X POST http://localhost:3000/rest/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@juice-sh.op","password":"MotDePasseValide!2026"}'
```
Résultat attendu : `200 OK` + JWT valide. La connexion légitime fonctionne.

## 3. Vérification outillée

| Outil | Avant | Après |
|---|---|---|
| Semgrep (`juiceshop-sequelize-raw-query-concat`) | 1 finding ERROR sur `routes/login.ts:14` | 0 finding |
| OWASP ZAP (règle 40018 — SQL Injection) | 1 alerte High sur `/rest/user/login` | 0 alerte |
| sqlmap (`--level 3 --risk 2` sur le paramètre `email`) | Paramètre injectable (boolean-based blind) | `not injectable` |

## 4. Preuve de la couverture

Test automatisé ajouté au pipeline (`test/api/loginSpec.ts`) :

```ts
it('rejette une tentative de contournement par injection SQL', async () => {
  const res = await frisby.post(`${API_URL}/rest/user/login`,
    { email: "' OR 1=1--", password: 'x' })
  expect(res.status).toBe(401)
})
```
