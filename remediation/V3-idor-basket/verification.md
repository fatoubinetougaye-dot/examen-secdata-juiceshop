# V3 — Vérification de la correction (IDOR, CWE-639)

## 1. Scénario de test à deux comptes

```bash
# Compte A -> propriétaire du panier 1
TOKEN_A=$(curl -s -X POST http://localhost:3000/rest/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"userA@juice-sh.op","password":"MotDePasseA!2026"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['authentication']['token'])")

# Accès à SON panier (doit rester autorisé)
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/rest/basket/1 \
  -H "Authorization: Bearer $TOKEN_A"

# Accès au panier d'un AUTRE utilisateur (doit être refusé)
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/rest/basket/2 \
  -H "Authorization: Bearer $TOKEN_A"
```

| Requête | Avant correction | Après correction |
|---|---|---|
| `GET /rest/basket/1` avec le jeton de A (propriétaire) | `200 OK` | `200 OK` (non-régression) |
| `GET /rest/basket/2` avec le jeton de A | `200 OK` + contenu du panier de B | `404 Not Found` |
| `GET /rest/basket/2` sans jeton | `401` | `401` |
| `GET /rest/basket/abc` | `500` (erreur SQL exposée) | `400 Bad Request` |

## 2. Test d'énumération automatisée

```bash
for i in $(seq 1 20); do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    http://localhost:3000/rest/basket/$i -H "Authorization: Bearer $TOKEN_A")
  echo "basket/$i -> $code"
done
```

- Avant : 20 réponses `200` (énumération complète des paniers de la base).
- Après : 1 réponse `200` (le panier de A) et 19 réponses `404`.

## 3. Vérification par la journalisation

Chaque tentative refusée produit une entrée exploitable par un SIEM :

```
warn: Tentative d'accès non autorisé au panier 2 par l'utilisateur 5 (IP 172.17.0.1)
```

Cette trace permet de définir une règle de détection (seuil : plus de
5 refus en 60 secondes pour un même utilisateur = alerte).
