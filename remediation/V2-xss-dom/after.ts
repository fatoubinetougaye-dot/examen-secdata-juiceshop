// ===================================================================
// V2 - APRES  |  Correction CWE-79
// ===================================================================
// 1. Suppression de bypassSecurityTrustHtml : le sanitizer Angular
//    reprend son rôle et neutralise les balises actives.
// 2. Interpolation textuelle ({{ }}) au lieu de [innerHTML] :
//    l'encodage contextuel HTML est appliqué automatiquement.
// 3. Validation/normalisation de l'entrée (longueur bornée).
// 4. Content-Security-Policy en défense en profondeur côté serveur.
// ===================================================================

export class SearchResultComponent implements OnInit {
  public searchValue = ''          // string simple, plus de SafeHtml

  constructor (private readonly route: ActivatedRoute) {}

  ngOnInit () {
    this.route.queryParams.subscribe((queryParam: any) => {
      const raw = String(queryParam.q ?? '')
      // Normalisation défensive : bornage et suppression des caractères de contrôle
      this.searchValue = raw.slice(0, 100).replace(/[\u0000-\u001F\u007F]/g, '')
      this.filterTable(this.searchValue)
    })
  }
}

// Template corrigé (search-result.component.html) :
// <h3>Résultats pour <span>{{ searchValue }}</span></h3>
//   -> Angular encode automatiquement < > " ' &

// -------------------------------------------------------------------
// Défense en profondeur côté serveur (server.ts) : en-têtes de sécurité
// -------------------------------------------------------------------
import helmet from 'helmet'

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],           // ni 'unsafe-inline' ni 'unsafe-eval'
      styleSrc: ["'self'"],
      imgSrc: ["'self'", 'data:'],
      objectSrc: ["'none'"],
      frameAncestors: ["'none'"],
      baseUri: ["'self'"],
      formAction: ["'self'"]
    }
  },
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
  frameguard: { action: 'deny' },
  noSniff: true,
  referrerPolicy: { policy: 'no-referrer' }
}))
app.disable('x-powered-by')
