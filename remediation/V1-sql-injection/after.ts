// ===================================================================
// V1 - APRES  |  routes/login.ts  |  Correction CWE-89
// ===================================================================
// 1. Requête paramétrée : la valeur utilisateur ne fait plus partie de
//    la structure de la requête, elle est transmise comme donnée liée.
// 2. Validation d'entrée en amont (format e-mail, longueur bornée).
// 3. Comparaison du mot de passe par bcrypt (voir V4).
// 4. Message d'erreur générique (pas d'oracle sur l'existence du compte).
// 5. Limitation du nombre de tentatives (défense en profondeur).
// ===================================================================

import { Request, Response, NextFunction } from 'express'
import { QueryTypes } from 'sequelize'
import * as bcrypt from 'bcryptjs'
import rateLimit from 'express-rate-limit'
import * as models from '../models/index'
import * as security from '../lib/insecurity'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

export const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  standardHeaders: true,
  message: 'Trop de tentatives de connexion. Réessayez dans 15 minutes.'
})

export function login () {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const email: string = String(req.body.email ?? '').trim()
      const password: string = String(req.body.password ?? '')

      // --- Validation stricte des entrées (allow-list) ---
      if (!EMAIL_RE.test(email) || email.length > 254 ||
          password.length === 0 || password.length > 128) {
        return res.status(401).send('Identifiants invalides.')
      }

      // --- Requête PARAMETREE : plus aucune concaténation ---
      const rows: any[] = await models.sequelize.query(
        'SELECT id, email, password, role, deletedAt FROM Users ' +
        'WHERE email = :email AND deletedAt IS NULL LIMIT 1',
        {
          replacements: { email },      // valeur liée, échappée par le driver
          type: QueryTypes.SELECT
        }
      )

      const user = rows[0]

      // --- Comparaison à temps constant, message uniforme ---
      const stored = user?.password ?? '$2a$12$invalidinvalidinvalidinvalidinvalidinvalidinvalidinv'
      const ok = await bcrypt.compare(password, stored)

      if (!user || !ok) {
        return res.status(401).send('Identifiants invalides.')
      }

      return res.json({ authentication: security.authorize(user) })
    } catch (error) {
      return next(error)
    }
  }
}

// Montage de la route : app.post('/rest/user/login', loginLimiter, login())
