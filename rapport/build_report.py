#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère le rapport de sécurité (Livrable 1) au format PDF."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
                                Paragraph, Spacer, Table, TableStyle,
                                PageBreak, NextPageTemplate, HRFlowable,
                                KeepTogether)

# --------------------------------------------------------------------- #
# Palette                                                               #
# --------------------------------------------------------------------- #
NAVY   = colors.HexColor("#0f172a")
STEEL  = colors.HexColor("#1e3a5f")
ACCENT = colors.HexColor("#b91c1c")
GREY   = colors.HexColor("#475569")
LIGHT  = colors.HexColor("#f1f5f9")
LINE   = colors.HexColor("#cbd5e1")

CRIT   = colors.HexColor("#7f1d1d")
HIGH   = colors.HexColor("#b91c1c")
MED    = colors.HexColor("#c2410c")
LOW    = colors.HexColor("#a16207")

OUT = "Rapport_Securite_Donnees_Fatou_Bintou_Gaye.pdf"

# --------------------------------------------------------------------- #
# Styles                                                                #
# --------------------------------------------------------------------- #
ss = getSampleStyleSheet()

def style(name, **kw):
    kw.setdefault("parent", ss["Normal"])
    return ParagraphStyle(name, **kw)

body = style("body", fontName="Helvetica", fontSize=9.5, leading=14,
             alignment=TA_JUSTIFY, textColor=colors.HexColor("#1e293b"),
             spaceAfter=6)
bodyL = style("bodyL", parent=body, alignment=TA_LEFT)
h1 = style("h1", fontName="Helvetica-Bold", fontSize=15, leading=19,
           textColor=NAVY, spaceBefore=6, spaceAfter=8)
h2 = style("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
           textColor=STEEL, spaceBefore=10, spaceAfter=5)
h3 = style("h3", fontName="Helvetica-Bold", fontSize=10, leading=13,
           textColor=ACCENT, spaceBefore=7, spaceAfter=3)
small = style("small", fontName="Helvetica", fontSize=8, leading=11,
              textColor=GREY)
cellL = style("cellL", fontName="Helvetica", fontSize=8, leading=10.5,
              alignment=TA_LEFT)
cellLb = style("cellLb", parent=cellL, fontName="Helvetica-Bold")
cellW = style("cellW", parent=cellL, textColor=colors.white)
bullet = style("bullet", parent=body, leftIndent=12, bulletIndent=2,
               spaceAfter=3)

def P(t, s=body): return Paragraph(t, s)

# --------------------------------------------------------------------- #
# En-tête / pied de page                                                #
# --------------------------------------------------------------------- #
def later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 14*mm, A4[0], 14*mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(20*mm, A4[1] - 9*mm, "Rapport de sécurité — OWASP Juice Shop")
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(A4[0] - 20*mm, A4[1] - 9*mm,
                           "Sécurité des Données — L3 Cybersécurité")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, 15*mm, A4[0] - 20*mm, 15*mm)
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(20*mm, 10*mm, "Fatou Bintou Gaye")
    canvas.drawRightString(A4[0] - 20*mm, 10*mm, "Page %d" % doc.page)
    canvas.restoreState()

def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(STEEL)
    canvas.rect(0, A4[1] - 92*mm, A4[0], 92*mm, fill=1, stroke=0)
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(3)
    canvas.line(20*mm, A4[1] - 96*mm, A4[0] - 20*mm, A4[1] - 96*mm)
    canvas.restoreState()

# --------------------------------------------------------------------- #
# Tableaux utilitaires                                                  #
# --------------------------------------------------------------------- #
def header_row(cells):
    return [P(c, cellW) for c in cells]

def sev_color(s):
    return {"Critical": CRIT, "High": HIGH, "Medium": MED, "Low": LOW}.get(s, GREY)

def std_table(data, widths, sev_col=None, header_bg=STEEL, font=8):
    t = Table(data, colWidths=widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), font),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]
    if sev_col is not None:
        for r in range(1, len(data)):
            txt = data[r][sev_col]
            label = txt.text if hasattr(txt, "text") else str(txt)
            for key in ("Critical", "High", "Medium", "Low"):
                if key in label:
                    cmds.append(("BACKGROUND", (sev_col, r), (sev_col, r), sev_color(key)))
                    cmds.append(("TEXTCOLOR", (sev_col, r), (sev_col, r), colors.white))
                    cmds.append(("FONTNAME", (sev_col, r), (sev_col, r), "Helvetica-Bold"))
                    break
    t.setStyle(TableStyle(cmds))
    return t

# --------------------------------------------------------------------- #
# Document                                                              #
# --------------------------------------------------------------------- #
doc = BaseDocTemplate(OUT, pagesize=A4,
                      leftMargin=20*mm, rightMargin=20*mm,
                      topMargin=20*mm, bottomMargin=18*mm,
                      title="Rapport de sécurité — OWASP Juice Shop",
                      author="Fatou Bintou Gaye")

frame_cover = Frame(0, 0, A4[0], A4[1], id="cover")
frame_body = Frame(20*mm, 18*mm, A4[0] - 40*mm, A4[1] - 38*mm, id="body")
doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[frame_cover], onPage=cover_page),
    PageTemplate(id="Body", frames=[frame_body], onPage=later_pages),
])

S = []

# ---------------------- PAGE DE GARDE --------------------------------- #
white_c = style("white_c", fontName="Helvetica-Bold", fontSize=26,
                leading=31, textColor=colors.white, alignment=TA_CENTER)
white_s = style("white_s", fontName="Helvetica", fontSize=12,
                textColor=colors.HexColor("#cbd5e1"), alignment=TA_CENTER)
white_t = style("white_t", fontName="Helvetica", fontSize=10,
                textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER,
                leading=16)

S += [Spacer(1, 34*mm)]
S += [P("EXAMEN FINAL", white_s)]
S += [Spacer(1, 5*mm)]
S += [P("Rapport d'évaluation<br/>de sécurité", white_c)]
S += [Spacer(1, 6*mm)]
S += [P("Application web OWASP Juice Shop", white_s)]
S += [Spacer(1, 40*mm)]

info = [
    ["Module", "Sécurité des Données"],
    ["Formation", "Licence 3 — Cybersécurité"],
    ["Étudiant", "Fatou Bintou Gaye"],
    ["Rôle", "Cybersecurity Analyst / Junior DevSecOps Engineer"],
    ["Application", "OWASP Juice Shop v20.2.0 (bkimminich/juice-shop)"],
    ["Dépôt", "github.com/fatoubinetougaye-dot/examen-secdata-juiceshop"],
    ["Décision", "Reject Deployment"],
]
it = Table([[P("<b>%s</b>" % k, white_t), P(v, white_t)] for k, v in info],
           colWidths=[45*mm, 105*mm])
it.setStyle(TableStyle([
    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
    ("ALIGN", (1, 0), (1, -1), "LEFT"),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#334155")),
]))
S += [it]
S += [NextPageTemplate("Body"), PageBreak()]

# ---------------------- SOMMAIRE ------------------------------------- #
S += [P("Sommaire", h1)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
toc = [
    ("1.", "Introduction", "3"),
    ("2.", "Méthodologie", "3"),
    ("3.", "Vulnérabilités identifiées (Partie 1)", "4"),
    ("4.", "Classification CWE et analyse d'impact CIA (Partie 2)", "5"),
    ("5.", "Remédiations et vérifications (Partie 3)", "6"),
    ("6.", "Pipeline de sécurité automatisé (Partie 4)", "8"),
    ("7.", "Résultats et décision de déploiement (Partie 5)", "9"),
    ("8.", "Analyse critique (Partie 6)", "10"),
    ("9.", "Conclusion", "11"),
]
tt = Table([[P("<b>%s</b>" % n, bodyL), P(t, bodyL), P(p, small)] for n, t, p in toc],
           colWidths=[12*mm, 128*mm, 15*mm])
tt.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("ALIGN", (2, 0), (2, -1), "RIGHT"),
    ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
]))
S += [tt]
S += [Spacer(1, 10*mm)]
S += [P("Avertissement", h3)]
S += [P("OWASP Juice Shop est une application volontairement vulnérable, "
        "publiée par l'OWASP à des fins pédagogiques. Toutes les attaques "
        "décrites dans ce rapport ont été réalisées en environnement local "
        "isolé (conteneur Docker sur poste personnel), sans jamais viser un "
        "système tiers. Ce cadre correspond à la mission d'évaluation confiée "
        "dans le scénario de l'examen.", body)]
S += [PageBreak()]

# ---------------------- 1. INTRODUCTION ------------------------------ #
S += [P("1. Introduction", h1)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
S += [P("Une organisation prévoit de mettre en production une application web "
        "permettant à ses utilisateurs de créer un compte, de s'authentifier "
        "et d'accéder à des ressources contenant des données potentiellement "
        "sensibles. Avant ce déploiement, l'équipe de sécurité m'a confié, en "
        "tant que <i>Cybersecurity Analyst / Junior DevSecOps Engineer</i>, la "
        "mission d'évaluer la sécurité de l'application, d'identifier les "
        "vulnérabilités susceptibles de compromettre la protection des "
        "données, d'en analyser les impacts, de proposer des remédiations et "
        "d'intégrer des contrôles de sécurité dans un pipeline automatisé.", body)]
S += [P("L'application retenue comme cible est <b>OWASP Juice Shop</b>, une "
        "boutique en ligne écrite en Node.js / Express côté serveur et Angular "
        "côté client, avec une base de données SQLite via l'ORM Sequelize. "
        "Elle reproduit fidèlement l'architecture d'une application réelle tout "
        "en concentrant l'ensemble du Top 10 OWASP, ce qui en fait un support "
        "d'évaluation représentatif.", body)]
S += [P("Ce rapport couvre les six parties de l'examen : identification des "
        "vulnérabilités, analyse de risque selon le triptyque "
        "Confidentialité-Intégrité-Disponibilité (CIA), remédiation et "
        "vérification, automatisation via un pipeline Jenkins, analyse des "
        "résultats et décision de déploiement, puis analyse critique de la "
        "démarche outillée.", body)]
S += [P("Objectif de protection des données", h3)]
S += [P("Le fil conducteur de l'évaluation est la protection des données des "
        "utilisateurs : identifiants de connexion, mots de passe, contenu des "
        "paniers et données personnelles. Chaque vulnérabilité est donc "
        "analysée à travers le prisme de son effet réel sur ces données plutôt "
        "que comme une faiblesse technique isolée.", body)]

# ---------------------- 2. MÉTHODOLOGIE ------------------------------ #
S += [P("2. Méthodologie", h1)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
S += [P("L'évaluation combine une approche manuelle et une approche outillée, "
        "afin de bénéficier de la couverture large des outils automatiques et "
        "de la profondeur du test manuel sur la logique métier.", body)]
S += [P("Démarche en cinq temps", h3)]
for txt in [
    "<b>Reconnaissance</b> — déploiement de l'application en conteneur Docker "
    "et cartographie des points d'entrée (authentification, recherche, panier, "
    "serveur de fichiers, API REST).",
    "<b>Analyse statique (SAST)</b> — lecture du code source du dépôt forké et "
    "passage de Semgrep avec des règles standard et des règles personnalisées.",
    "<b>Analyse de composition (SCA)</b> — inventaire des dépendances "
    "vulnérables via npm audit et Trivy.",
    "<b>Analyse dynamique (DAST) et test manuel</b> — exploitation effective "
    "des failles sur l'application en fonctionnement, complétée par un scan "
    "OWASP ZAP.",
    "<b>Détection de secrets</b> — recherche de clés et identifiants exposés "
    "dans le code et l'historique Git avec Gitleaks.",
]:
    S += [P("•&nbsp;&nbsp;" + txt, bullet)]
S += [P("Référentiels utilisés", h3)]
S += [P("Les vulnérabilités sont classées selon la nomenclature "
        "<b>CWE</b> (Common Weakness Enumeration) et rattachées aux catégories "
        "du <b>Top 10 OWASP 2021</b>. La criticité est évaluée qualitativement "
        "sur quatre niveaux (Critical, High, Medium, Low) en croisant la "
        "facilité d'exploitation et l'impact sur les données, selon une logique "
        "proche du scoring CVSS.", body)]
env = [
    header_row(["Composant", "Version"]),
    [P("Système d'exploitation", cellL), P("Windows 11 Professionnel (24H2)", cellL)],
    [P("Conteneurisation", cellL), P("Docker Desktop 29.4.2", cellL)],
    [P("Serveur d'intégration", cellL), P("Jenkins 2.568.2 (service Windows), JDK 21", cellL)],
    [P("Runtime applicatif", cellL), P("Node.js 24.19.0", cellL)],
    [P("Application cible", cellL), P("github.com/juice-shop/juice-shop (clonée dans app/)", cellL)],
]
S += [KeepTogether([P("Environnement de test", h3),
                    std_table(env, [55*mm, 95*mm])])]

# ---------------------- 3. VULNÉRABILITÉS ---------------------------- #
S += [P("3. Vulnérabilités identifiées", h1)]
S += [P("Partie 1 — /4 points", small)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
S += [P("L'évaluation a mis en évidence huit vulnérabilités (le sujet en "
        "demande cinq au minimum). Le tableau ci-dessous en donne la "
        "description, le composant concerné, la catégorie CWE et le risque "
        "pour l'application.", body)]

vulns = [
    header_row(["ID", "Vulnérabilité", "Composant", "CWE", "Description / risque"]),
    ["V1", "Injection SQL", "Authentification\n(routes/login)", "CWE-89",
     "La requête de connexion concatène l'e-mail saisi. Le payload "
     "' OR 1=1-- contourne l'authentification et ouvre une session "
     "administrateur ; toute la table Users est exfiltrable."],
    ["V2", "XSS DOM", "Barre de recherche\n(frontend)", "CWE-79",
     "Le terme de recherche est passé à bypassSecurityTrustHtml puis injecté "
     "en innerHTML. Du code JavaScript arbitraire s'exécute dans le navigateur "
     "de la victime (vol de jeton, actions frauduleuses)."],
    ["V3", "Broken Access Control / IDOR", "Panier\n(routes/basket)", "CWE-639",
     "L'identifiant de panier vient de l'URL sans contrôle d'appartenance. Un "
     "utilisateur authentifié lit et modifie le panier d'autrui par simple "
     "changement d'ID."],
    ["V4", "Hachage de mot de passe faible", "lib/insecurity", "CWE-916",
     "Les mots de passe sont hachés en MD5 sans sel. Un vol de base est cassé "
     "en quelques minutes (rainbow tables, hashcat)."],
    ["V5", "Exposition de données sensibles", "Serveur de fichiers\n(/ftp)", "CWE-200",
     "Le répertoire /ftp est listable et sert des sauvegardes. Combiné à une "
     "traversée par octet nul (%2500), il divulgue des fichiers confidentiels."],
    ["V6", "Secrets codés en dur", "lib/insecurity", "CWE-798",
     "La clé privée RSA de signature des JWT est embarquée dans le code. Un "
     "attaquant peut forger des jetons valides pour n'importe quel compte."],
    ["V7", "Dépendances vulnérables", "package.json", "CWE-1395",
     "npm audit remonte 45 vulnérabilités (7 critiques, 19 élevées), dont "
     "pollution de prototype (lodash), injection de commande (marsdb) et "
     "traversée d'archive Zip Slip (decompress)."],
    ["V8", "Mauvaise configuration de sécurité", "server.ts\n(en-têtes HTTP)", "CWE-16",
     "Absence de CSP, HSTS, X-Frame-Options, X-Content-Type-Options ; en-tête "
     "X-Powered-By exposé. Surface d'attaque XSS et clickjacking élargie."],
]
rows = [vulns[0]]
for r in vulns[1:]:
    rows.append([P("<b>%s</b>" % r[0], cellLb),
                 P(r[1], cellLb),
                 P(r[2].replace("\n", "<br/>"), cellL),
                 P(r[3], cellL),
                 P(r[4], cellL)])
S += [std_table(rows, [10*mm, 30*mm, 26*mm, 20*mm, 64*mm], font=7.5)]
S += [Spacer(1, 4*mm)]
S += [P("Les vulnérabilités V1 à V4 sont retenues pour la phase de "
        "remédiation détaillée (Partie 3), car elles combinent une "
        "exploitation directe et un impact maximal sur les données des "
        "utilisateurs.", small)]
S += [PageBreak()]

# ---------------------- 4. CWE + CIA --------------------------------- #
S += [P("4. Classification CWE et analyse d'impact CIA", h1)]
S += [P("Partie 2 — /4 points", small)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
S += [P("Chaque vulnérabilité est analysée selon les trois propriétés "
        "fondamentales de la sécurité de l'information — Confidentialité, "
        "Intégrité, Disponibilité — puis se voit attribuer un niveau de "
        "criticité et une priorité de correction.", body)]

cia = [
    header_row(["Vuln.", "Confid.", "Intég.", "Dispo.", "Criticité", "Priorité de correction"]),
    ["V1 SQLi", "Oui", "Oui", "Possible", "Critical",
     "Immédiate — contournement d'authentification, fuite totale de la base."],
    ["V2 XSS", "Oui", "Possible", "Non", "High",
     "Élevée — vol de session et actions au nom de la victime."],
    ["V3 IDOR", "Oui", "Oui", "Non", "High",
     "Élevée — accès et modification des données d'autres utilisateurs."],
    ["V4 MD5", "Oui", "Possible", "Non", "Critical",
     "Immédiate — compromet tous les comptes en cas de fuite de base."],
    ["V5 /ftp", "Oui", "Non", "Non", "Medium",
     "Planifiée — divulgation de fichiers, sans écriture."],
    ["V6 Secret", "Oui", "Oui", "Non", "Critical",
     "Immédiate — forge de jetons, usurpation de tout compte."],
    ["V7 Deps", "Oui", "Possible", "Possible", "High",
     "Élevée — dépend du chemin d'appel, correctifs à appliquer."],
    ["V8 Config", "Possible", "Non", "Non", "Medium",
     "Planifiée — durcissement des en-têtes HTTP."],
]
rows = [cia[0]]
for r in cia[1:]:
    rows.append([P("<b>%s</b>" % r[0], cellLb)] +
                [P(x, cellL) for x in r[1:4]] +
                [P(r[4], cellL), P(r[5], cellL)])
S += [std_table(rows, [22*mm, 16*mm, 16*mm, 18*mm, 20*mm, 58*mm],
                sev_col=4, font=7.5)]
S += [Spacer(1, 5*mm)]
S += [P("Lecture des priorités", h3)]
S += [P("Les vulnérabilités critiques (V1, V4, V6) partagent une "
        "caractéristique : elles ouvrent un accès aux données de "
        "l'ensemble des utilisateurs, pas seulement de la victime directe. "
        "Elles sont donc traitées en priorité absolue. Les vulnérabilités "
        "élevées (V2, V3, V7) portent une atteinte sérieuse mais plus "
        "circonscrite. Les vulnérabilités moyennes (V5, V8) relèvent du "
        "durcissement et sont planifiées une fois les précédentes corrigées.", body)]
S += [P("Concernant la disponibilité, l'injection SQL est marquée "
        "« Possible » car une requête malveillante (par exemple une clause "
        "coûteuse ou une commande de suppression) peut dégrader ou rendre "
        "indisponible le service, au-delà de la seule lecture de données.", body)]
S += [PageBreak()]

# ---------------------- 5. REMÉDIATIONS ------------------------------ #
S += [P("5. Remédiations et vérifications", h1)]
S += [P("Partie 3 — /4 points", small)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
S += [P("Quatre vulnérabilités importantes sont corrigées ci-dessous (le "
        "sujet en demande trois). Pour chacune : la cause, la correction "
        "proposée, la justification de son efficacité et la méthode de "
        "vérification. Le code avant/après complet figure dans le dossier "
        "<i>remediation/</i> du dépôt Git.", body)]

def remediation_block(titre, cause, remede, justif, verif):
    blk = [P(titre, h2)]
    tab = [
        [P("<b>Cause</b>", cellLb), P(cause, cellL)],
        [P("<b>Correction</b>", cellLb), P(remede, cellL)],
        [P("<b>Justification</b>", cellLb), P(justif, cellL)],
        [P("<b>Vérification</b>", cellLb), P(verif, cellL)],
    ]
    t = Table(tab, colWidths=[28*mm, 122*mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
    ]))
    blk.append(t)
    blk.append(Spacer(1, 3*mm))
    return KeepTogether(blk)

S += [remediation_block(
    "V1 — Injection SQL (CWE-89, Critical)",
    "La requête de connexion est construite par interpolation de chaîne : "
    "l'e-mail saisi devient une partie de la structure SQL exécutée.",
    "Passage à une requête paramétrée Sequelize (option replacements), la "
    "valeur utilisateur devenant une donnée liée et non du code. Ajout d'une "
    "validation d'entrée (format e-mail, longueur bornée) et d'un message "
    "d'erreur générique.",
    "Le driver échappe la donnée liée : la clause 1=1 est traitée comme une "
    "chaîne littérale et ne modifie plus la logique. La donnée ne peut "
    "structurellement plus s'exécuter comme du SQL.",
    "Le payload ' OR 1=1-- renvoie désormais 401 au lieu de 200 ; une "
    "connexion légitime fonctionne toujours ; Semgrep et sqlmap ne signalent "
    "plus la faille. Un test automatisé verrouille la correction.")]

S += [remediation_block(
    "V2 — XSS DOM (CWE-79, High)",
    "Le terme de recherche est marqué de confiance via "
    "bypassSecurityTrustHtml, ce qui neutralise le sanitizer Angular, puis "
    "injecté en innerHTML.",
    "Suppression de l'appel bypassSecurityTrustHtml et remplacement de "
    "[innerHTML] par l'interpolation {{ }}, qui applique l'encodage HTML "
    "automatique. Ajout d'une Content-Security-Policy stricte via Helmet en "
    "défense en profondeur.",
    "L'encodage contextuel transforme les caractères actifs (< > \" ') en "
    "entités inertes : le navigateur affiche le texte au lieu de l'exécuter. "
    "La CSP bloque en dernier recours tout script en ligne.",
    "Les charges XSS s'affichent littéralement ; l'inspection du DOM montre "
    "des entités HTML et non des nœuds actifs ; ZAP ne remonte plus d'alerte "
    "XSS ni d'absence de CSP.")]

S += [remediation_block(
    "V3 — Broken Access Control / IDOR (CWE-639, High)",
    "L'identifiant de panier provient de l'URL sans vérification que la "
    "ressource appartient à l'utilisateur authentifié.",
    "L'identité est désormais lue exclusivement dans le jeton JWT vérifié "
    "côté serveur. Le filtre d'appartenance (UserId) est intégré directement "
    "à la requête, et un accès non autorisé renvoie 404. La tentative est "
    "journalisée.",
    "Le contrôle d'accès est appliqué au niveau de la requête (fail-safe) : "
    "un panier tiers ne peut plus être retourné, même en cas d'erreur "
    "applicative. L'identité n'étant plus dérivée d'un paramètre client, "
    "elle n'est plus falsifiable.",
    "Un scénario à deux comptes montre 404 sur le panier d'autrui et 200 sur "
    "le sien ; l'énumération de 1 à 20 ne retourne plus qu'un seul panier ; "
    "chaque refus produit une trace exploitable par un SIEM.")]

S += [remediation_block(
    "V4 — Hachage de mot de passe faible (CWE-916, Critical)",
    "Les mots de passe sont dérivés en MD5, fonction rapide et sans sel, "
    "donc vulnérable aux rainbow tables et au cassage massif.",
    "Remplacement par bcrypt avec un facteur de coût 12 (sel unique "
    "automatique, dérivation lente), comparaison à temps constant, politique "
    "de mot de passe minimale et migration transparente des comptes existants "
    "au premier login.",
    "bcrypt ralentit chaque essai d'un facteur considérable et rend chaque "
    "haché unique grâce au sel : une attaque par dictionnaire complète "
    "devient économiquement irréaliste sur un mot de passe conforme.",
    "Le format stocké passe de 32 hex à un haché $2a$12$ ; deux comptes de "
    "même mot de passe ont des hachés différents ; hashcat chute de "
    "milliards à quelques milliers d'essais/s ; Semgrep ne signale plus MD5.")]
S += [PageBreak()]

# ---------------------- 6. PIPELINE ---------------------------------- #
S += [P("6. Pipeline de sécurité automatisé", h1)]
S += [P("Partie 4 — /4 points", small)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
S += [P("Un pipeline Jenkins déclaratif (fichier <i>Jenkinsfile</i> du dépôt) "
        "automatise les contrôles de sécurité à chaque évolution du code. Il "
        "respecte les six étapes imposées et intègre quatre types de contrôles "
        "(le sujet en demande deux) : SAST, SCA, Secret Detection et DAST.", body)]
S += [P("Enchaînement des étapes", h3)]
pipe = [
    header_row(["Étape", "Contenu"]),
    ["1. Checkout", "Récupération du code depuis GitHub (credential github-cred)."],
    ["2. Build / Preparation", "Installation des dépendances et démarrage du "
     "conteneur Juice Shop (cible du DAST)."],
    ["3. Security Analysis", "SAST (Semgrep) et SCA (npm audit + Trivy) exécutés "
     "en parallèle."],
    ["4. Additional Security Check", "Secret Detection (Gitleaks) et DAST "
     "(OWASP ZAP) exécutés en parallèle."],
    ["5. Report Generation", "Consolidation des rapports en un résumé HTML/JSON, "
     "archivage, application du quality gate."],
    ["6. Notification", "Envoi du bilan et de la décision par e-mail "
     "(Email Extension), nettoyage de l'environnement."],
]
rows = [pipe[0]] + [[P("<b>%s</b>" % r[0], cellLb), P(r[1], cellL)] for r in pipe[1:]]
S += [std_table(rows, [45*mm, 105*mm])]
S += [Spacer(1, 4*mm)]
S += [P("Outils intégrés", h3)]
tools = [
    header_row(["Outil", "Type", "Détecte", "Limites", "Moment"]),
    ["Semgrep", "SAST", "Injections, XSS, crypto faible, secrets, motifs "
     "dangereux dans le code", "Aveugle au runtime ; faux positifs ; "
     "rate la logique métier", "Étape 3"],
    ["npm audit", "SCA", "CVE des dépendances npm et transitives",
     "N'indique pas si le code vulnérable est appelé", "Étape 3"],
    ["Trivy", "SCA / config", "CVE OS et librairies, mauvaises configurations",
     "Bruit sur paquets non exposés", "Étape 3"],
    ["Gitleaks", "Secret Detection", "Clés, jetons, identifiants dans le code "
     "et l'historique Git", "Ne valide pas le secret ; faux positifs sur les "
     "jeux de test", "Étape 4"],
    ["OWASP ZAP", "DAST", "XSS, injections, en-têtes manquants, cookies non "
     "sécurisés à l'exécution", "Baseline passif : ne teste pas le périmètre "
     "authentifié ni la logique", "Étape 4"],
]
rows = [tools[0]] + [[P("<b>%s</b>" % r[0], cellLb)] + [P(x, cellL) for x in r[1:]] for r in tools[1:]]
S += [std_table(rows, [24*mm, 20*mm, 44*mm, 40*mm, 22*mm], font=7)]
S += [Spacer(1, 4*mm)]
S += [P("Le quality gate applique une politique explicite : zéro "
        "vulnérabilité critique et au plus cinq vulnérabilités élevées. "
        "Au-delà, le build échoue et le déploiement est bloqué. La décision "
        "est ainsi automatisée et reproductible plutôt que laissée à "
        "l'appréciation ponctuelle d'un opérateur.", body)]
S += [PageBreak()]

# ---------------------- 7. RÉSULTATS & DÉCISION ---------------------- #
S += [P("7. Résultats et décision de déploiement", h1)]
S += [P("Partie 5 — /2 points", small)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
S += [P("L'exécution du pipeline consolide les résultats des différents "
        "outils. Le tableau ci-dessous priorise les problèmes détectés et "
        "associe à chacun l'action recommandée.", body)]
res = [
    header_row(["Problème", "CWE", "Sévérité", "Action recommandée"]),
    ["Injection SQL", "CWE-89", "Critical", "Bloquer le déploiement"],
    ["Hachage MD5 des mots de passe", "CWE-916", "Critical", "Bloquer le déploiement"],
    ["Clé privée codée en dur", "CWE-798", "Critical", "Bloquer le déploiement"],
    ["XSS DOM", "CWE-79", "High", "Correction requise"],
    ["Broken Access Control (IDOR)", "CWE-639", "High", "Correction requise"],
    ["Dépendances vulnérables", "CWE-1395", "High", "Correction requise"],
    ["Exposition d'information (/ftp)", "CWE-200", "Medium", "Correction planifiée"],
    ["En-têtes de sécurité absents", "CWE-16", "Medium", "Correction planifiée"],
]
rows = [res[0]] + [[P(r[0], cellL), P(r[1], cellL), P(r[2], cellL), P(r[3], cellL)] for r in res[1:]]
S += [std_table(rows, [58*mm, 24*mm, 26*mm, 42*mm], sev_col=2, font=8)]
S += [Spacer(1, 5*mm)]

S += [P("Décision finale", h2)]
dec = Table([[P("<b>REJECT DEPLOYMENT</b>",
                style("dec", fontName="Helvetica-Bold", fontSize=13,
                      textColor=colors.white, alignment=TA_CENTER))]],
            colWidths=[150*mm])
dec.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), CRIT),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
S += [dec]
S += [Spacer(1, 4*mm)]
S += [P("Justification", h3)]
S += [P("L'application présente au moins trois vulnérabilités critiques "
        "exploitables (injection SQL, hachage MD5, clé privée en dur) qui "
        "touchent directement la confidentialité et l'intégrité des données de "
        "tous les utilisateurs. Le seuil de la politique (zéro critique) est "
        "franchi. Déployer en l'état exposerait immédiatement les comptes et "
        "les données personnelles. La mise en production est donc refusée : "
        "les vulnérabilités critiques et élevées doivent être corrigées, puis "
        "le pipeline ré-exécuté pour confirmer le retour sous les seuils avant "
        "toute nouvelle décision.", body)]
S += [P("Il ne s'agit pas d'un « Accept with Conditions » : les défauts "
        "constatés ne sont pas des points de durcissement mineurs mais des "
        "failles activement exploitables menant à une compromission complète.", body)]
S += [PageBreak()]

# ---------------------- 8. ANALYSE CRITIQUE -------------------------- #
S += [P("8. Analyse critique", h1)]
S += [P("Partie 6 — /2 points", small)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
S += [P("<b>Un outil de sécurité qui ne détecte aucune vulnérabilité peut-il "
        "garantir qu'une application est sécurisée ?</b>", bodyL)]
S += [P("Non. L'absence de détection ne prouve pas l'absence de vulnérabilité ; "
        "elle prouve seulement que les règles configurées n'ont rien trouvé "
        "dans le périmètre analysé. Confondre les deux est une erreur "
        "d'interprétation aux conséquences graves.", body)]
S += [P("Faux positifs et faux négatifs", h3)]
S += [P("Un outil produit des <b>faux positifs</b> (alertes sur du code sain) "
        "qui, trop nombreux, noient les vraies alertes et poussent les équipes "
        "à désactiver les contrôles. Il produit surtout des <b>faux négatifs</b> "
        "(vulnérabilités réelles non signalées), bien plus dangereux car "
        "invisibles : ils installent une fausse confiance. Dans ce projet, la "
        "faille IDOR (V3) illustre ce risque — un contrôle d'accès défaillant "
        "relève de la logique métier et échappe largement à la détection "
        "purement syntaxique.", body)]
S += [P("Limites des outils et couverture des règles", h3)]
S += [P("Chaque outil a un angle mort. Le SAST ignore le comportement à "
        "l'exécution ; le DAST en mode baseline ne teste pas le périmètre "
        "authentifié ni les enchaînements métier ; le SCA signale des CVE sans "
        "savoir si le code vulnérable est réellement atteint ; la détection de "
        "secrets ne juge pas de la validité d'un secret. La couverture dépend "
        "directement des règles activées : une catégorie de faille sans règle "
        "correspondante restera invisible, quel que soit le nombre de scans. "
        "Les outils ne voient bien que ce qu'on leur a appris à chercher.", body)]
S += [P("Importance de l'analyse humaine", h3)]
S += [P("L'automatisation est indispensable pour passer à l'échelle et "
        "détecter tôt les régressions, mais elle ne remplace pas le jugement. "
        "L'analyste humain contextualise une alerte selon la sensibilité réelle "
        "des données, écarte les faux positifs, découvre les failles de logique "
        "métier et tranche la décision de déploiement. Les outils et l'humain "
        "sont complémentaires : les premiers élargissent la couverture et "
        "accélèrent, le second apporte la compréhension du contexte et du "
        "risque.", body)]
S += [P("En synthèse, un scan « propre » est une condition nécessaire mais "
        "non suffisante : il réduit le risque connu, il ne certifie jamais "
        "l'absence de risque. La sécurité se démontre par un faisceau de "
        "preuves convergentes — outils variés, tests manuels et revue humaine — "
        "et non par le silence d'un seul outil.", body)]

# ---------------------- 9. CONCLUSION -------------------------------- #
S += [P("9. Conclusion", h1)]
S += [HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8)]
S += [P("L'évaluation d'OWASP Juice Shop a mis en évidence huit vulnérabilités, "
        "dont trois critiques touchant directement la protection des données "
        "des utilisateurs. Quatre d'entre elles ont été corrigées et les "
        "corrections vérifiées par rejeu d'attaque, test de non-régression et "
        "confirmation outillée.", body)]
S += [P("Un pipeline Jenkins intégrant SAST, SCA, détection de secrets et DAST "
        "a été mis en place pour automatiser ces contrôles et matérialiser la "
        "décision de déploiement via un quality gate explicite. Appliqué à "
        "l'application en l'état, ce pipeline aboutit logiquement à un "
        "<b>Reject Deployment</b>.", body)]
S += [P("Au-delà du verdict, ce travail illustre une posture DevSecOps : "
        "intégrer la sécurité au plus tôt et de façon continue, tout en "
        "gardant à l'esprit que l'outillage n'a de valeur qu'accompagné d'une "
        "analyse humaine capable d'en interpréter les résultats et d'en "
        "combler les angles morts.", body)]

doc.build(S)
print("PDF généré :", OUT)
