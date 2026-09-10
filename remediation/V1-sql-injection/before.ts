// ===================================================================
// V1 - AVANT  |  routes/login.ts  |  CWE-89  |  Sévérité : CRITICAL
// ===================================================================
// La requête est construite par interpolation de chaîne : la valeur de
// req.body.email est injectée telle quelle dans le SQL.
// Payload de contournement : email = ' OR 1=1--   password = n'importe quoi
// ===================================================================

import { Request, Response, NextFunction } from 'express'
import * as models from '../models/index'
import * as security from '../lib/insecurity'
import { User as UserModel } from '../models/user'

export function login () {
  return (req: Request, res: Response, next: NextFunction) => {
    models.sequelize.query(
      `SELECT * FROM Users
         WHERE email = '${req.body.email || ''}'
           AND password = '${security.hash(req.body.password || '')}'
           AND deletedAt IS NULL`,
      { model: UserModel, plain: true }
    )
      .then((authenticatedUser: any) => {
        if (authenticatedUser) {
          res.json({ authentication: security.authorize(authenticatedUser) })
        } else {
          res.status(401).send('Invalid email or password.')
        }
      })
      .catch((error: Error) => next(error))
  }
}
