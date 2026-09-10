// ===================================================================
// V3 - APRES  |  Correction CWE-639 / CWE-284
// ===================================================================
// 1. L'identité provient EXCLUSIVEMENT du jeton vérifié côté serveur,
//    jamais de l'URL ni d'un en-tête modifiable par le client.
// 2. Le filtre d'appartenance (UserId) est intégré à la requête :
//    un panier tiers ne peut pas être retourné, même par erreur.
// 3. Réponse 404 (et non 403) pour ne pas révéler l'existence de la ressource.
// 4. Journalisation de la tentative pour détection côté SIEM.
// ===================================================================

import { Request, Response, NextFunction } from 'express'
import { BasketModel } from '../models/basket'
import * as security from '../lib/insecurity'
import logger from '../lib/logger'

export function retrieveBasket () {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      // --- Identité issue du JWT vérifié, pas de l'URL ---
      const token = security.authenticatedUsers.tokenOf(req)
      const currentUser = security.authenticatedUsers.from(req)
      if (!token || !currentUser?.data?.id) {
        return res.status(401).json({ error: 'Authentification requise.' })
      }

      const requestedId = Number.parseInt(String(req.params.id), 10)
      if (!Number.isInteger(requestedId) || requestedId <= 0) {
        return res.status(400).json({ error: 'Identifiant de panier invalide.' })
      }

      // --- Contrôle d'accès appliqué DANS la requête (fail-safe) ---
      const basket = await BasketModel.findOne({
        where: { id: requestedId, UserId: currentUser.data.id },
        include: [{ model: ProductModel, paranoid: false, as: 'Products' }]
      })

      if (!basket) {
        logger.warn(
          `Tentative d'accès non autorisé au panier ${requestedId} ` +
          `par l'utilisateur ${currentUser.data.id} (IP ${req.ip})`
        )
        return res.status(404).json({ error: 'Panier introuvable.' })
      }

      return res.json(utils.queryResultToJson(basket))
    } catch (error) {
      return next(error)
    }
  }
}
