// ===================================================================
// V4 - AVANT  |  lib/insecurity.ts  |  CWE-916 / CWE-327  |  CRITICAL
// ===================================================================
// Les mots de passe sont dérivés avec MD5, sans sel et sans facteur de
// coût. Un dump de la table Users est cassé en quelques minutes avec
// hashcat (-m 0) ou une simple recherche en base de rainbow tables.
// ===================================================================

import * as crypto from 'crypto'

export const hash = (data: string) =>
  crypto.createHash('md5').update(data).digest('hex')

// models/user.ts
UserModel.init({
  password: {
    type: DataTypes.STRING,
    set (clearTextPassword: string) {
      this.setDataValue('password', security.hash(clearTextPassword))
    }
  }
})
