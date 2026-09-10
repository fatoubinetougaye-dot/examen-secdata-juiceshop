// ===================================================================
// V3 - AVANT  |  routes/basket.ts  |  CWE-639 / CWE-284  |  HIGH
// ===================================================================
// L'utilisateur doit être authentifié, mais aucun contrôle ne vérifie
// que le panier demandé LUI appartient : l'identifiant est repris tel
// quel depuis l'URL (référence directe non sécurisée).
// Exploitation : GET /rest/basket/2 avec le JWT du propriétaire du panier 1
// ===================================================================

import { Request, Response, NextFunction } from 'express'
import { BasketModel } from '../models/basket'

export function retrieveBasket () {
  return (req: Request, res: Response, next: NextFunction) => {
    const id = req.params.id
    BasketModel.findOne({
      where: { id },                       // aucun filtre sur le propriétaire
      include: [{ model: ProductModel, paranoid: false, as: 'Products' }]
    })
      .then((basket: BasketModel | null) => {
        res.json(utils.queryResultToJson(basket))
      })
      .catch((error: Error) => next(error))
  }
}
