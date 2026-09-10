// ===================================================================
// V4 - APRES  |  Correction CWE-916 / CWE-327
// ===================================================================
// 1. bcrypt avec un facteur de coût 12 : sel unique généré
//    automatiquement, dérivation volontairement lente (~250 ms).
// 2. Comparaison à temps constant (bcrypt.compare) contre les attaques
//    temporelles.
// 3. Politique de mot de passe minimale appliquée à l'inscription.
// 4. Migration transparente des comptes existants au premier login.
// ===================================================================

import * as bcrypt from 'bcryptjs'

const BCRYPT_COST = 12

export const hashPassword = async (clearText: string): Promise<string> =>
  await bcrypt.hash(clearText, BCRYPT_COST)

export const verifyPassword = async (clearText: string, stored: string): Promise<boolean> =>
  await bcrypt.compare(clearText, stored)

// --- Politique de mot de passe (CWE-521) ---
export const isPasswordAcceptable = (pwd: string): boolean =>
  typeof pwd === 'string' &&
  pwd.length >= 12 && pwd.length <= 128 &&
  /[a-z]/.test(pwd) && /[A-Z]/.test(pwd) && /\d/.test(pwd)

// --- Migration progressive des anciens hachés MD5 ---
// Au premier login réussi, l'ancien haché est remplacé par un haché bcrypt.
export const migrateLegacyHash = async (user: any, clearText: string) => {
  const isLegacy = /^[a-f0-9]{32}$/i.test(user.password)   // format MD5
  if (isLegacy) {
    const legacyMatch =
      crypto.createHash('md5').update(clearText).digest('hex') === user.password
    if (legacyMatch) {
      user.password = await hashPassword(clearText)
      await user.save()
      return true
    }
    return false
  }
  return await verifyPassword(clearText, user.password)
}
