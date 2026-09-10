# V4 — Vérification de la correction (hachage faible, CWE-916)

## 1. Contrôle du format stocké en base

```bash
docker exec -it juice-shop sqlite3 data/juiceshop.sqlite \
  "SELECT email, substr(password,1,32) FROM Users LIMIT 3;"
```

| | Avant | Après |
|---|---|---|
| Format du haché | `0192023a7bbd73250516f069df18b500` (MD5, 32 hex) | `$2a$12$Xk9...` (bcrypt, préfixe `$2a$12$`) |
| Sel | absent | unique par utilisateur, intégré au haché |
| Deux utilisateurs, même mot de passe | hachés **identiques** | hachés **différents** |

## 2. Test de résistance au cassage hors ligne

```bash
# Extraction d'un haché de test puis tentative avec hashcat
hashcat -m 0    hash_md5.txt   rockyou.txt      # avant  -> mot de passe retrouvé en < 5 s
hashcat -m 3200 hash_bcrypt.txt rockyou.txt     # après  -> ~2 500 essais/s sur GPU de TP
```

Le passage de plusieurs milliards d'essais par seconde (MD5) à quelques
milliers (bcrypt coût 12) rend une attaque par dictionnaire complète
économiquement irréaliste sur un mot de passe conforme à la politique.

## 3. Non-régression fonctionnelle

| Test | Résultat attendu | Obtenu |
|---|---|---|
| Création d'un compte avec `MotDePasseValide!2026` | `201 Created`, haché bcrypt en base | OK |
| Connexion avec le bon mot de passe | `200 OK` + JWT | OK |
| Connexion avec un mauvais mot de passe | `401` | OK |
| Compte historique (haché MD5) — 1re connexion | `200 OK`, haché réécrit en bcrypt | OK |
| Compte historique — 2e connexion | `200 OK` via bcrypt | OK |
| Inscription avec `1234` | `400` (politique non respectée) | OK |

## 4. Vérification outillée

| Outil | Avant | Après |
|---|---|---|
| Semgrep (`juiceshop-weak-password-hash`) | 1 finding ERROR sur `lib/insecurity.ts` | 0 finding |
| Semgrep (`p/owasp-top-ten` — A02 Cryptographic Failures) | 3 findings | 0 finding |
