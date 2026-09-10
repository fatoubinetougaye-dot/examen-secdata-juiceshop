// ===================================================================
// V2 - AVANT  |  frontend/src/app/search-result/  |  CWE-79  |  HIGH
// ===================================================================
// Le terme de recherche fourni par l'utilisateur est marqué comme
// "de confiance" puis injecté via [innerHTML] : le sanitizer Angular,
// qui bloquerait normalement les balises actives, est court-circuité.
// Payload : #/search?q=<iframe src="javascript:alert(`xss`)">
// ===================================================================

import { DomSanitizer, SafeHtml } from '@angular/platform-browser'

export class SearchResultComponent implements OnInit {
  public searchValue?: SafeHtml

  constructor (private readonly sanitizer: DomSanitizer,
               private readonly route: ActivatedRoute) {}

  ngOnInit () {
    this.route.queryParams.subscribe((queryParam: any) => {
      const q = queryParam.q ?? ''
      // Neutralisation explicite du sanitizer : vulnérabilité
      this.searchValue = this.sanitizer.bypassSecurityTrustHtml(q)
      this.filterTable(q)
    })
  }
}

// Template associé (search-result.component.html) :
// <h3>Résultats pour <span [innerHTML]="searchValue"></span></h3>
