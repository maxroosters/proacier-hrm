# -*- coding: utf-8 -*-
"""PROACIER HRM - paghe.py v08.03 - FASE 7 (Presenze & Paies)
✅ v08.03: _pdf_safe su tutti i PDF (fix FPDFUnicodeEncodingException)
✅ v08.03: sezione_buste legge PAGAMENTI direttamente (fix "Aucune paie")
✅ v08.03: icone tab singole (niente doppie)
Ruoli: admin calcola+genera; dipendente consulta storico+PDF propri (in app.py)
"""
import re
import streamlit as st
from datetime import datetime, date
from fpdf import FPDF
VERSIONE = "v08.03"
T6 = {
 "anom_title": ("Anomalies & absences", "Anomalie & assenze", "Anomalies & absences"),
 "paghe_title": ("Calcul des paies (quinzaine)", "Calcolo paghe (quindicina)", "Payroll (fortnight)"),
 "acc_title": ("Avances", "Acconti", "Advances"),
 "buste_title": ("🖨️ Fiche de paie", "🖨️ Busta paga", "🖨️ Pay slip"),
 "releve_title": ("📤 Relevé d'heures (externes)", "📤 Presenze (esterni)", "📤 Hours (external)"),
 "solde_title": ("📤 Solde de tout compte", "📤 Conteggio finale", "📤 Final settlement"),
 "import_title": ("Importation des pointages", "Importazione presenze", "Attendance import"),
 "anno": ("Année", "Anno", "Year"), "mese": ("Mois", "Mese", "Month"),
 "analizza": (" Analyser le fichier chargé", "🔍 Analizza il file caricato", "🔍 Analyse loaded file"),
 "calcola": ("💰 Calculer la quinzaine", "💰 Calcola la quindicina", "💰 Compute fortnight"),
 "conferma": ("✅ Confirmer et écrire dans PAGAMENTI", "✅ Conferma e scrivi in PAGAMENTI", "✅ Confirm & write to PAGAMENTI"),
 "travailleur": ("Travailleur", "Lavoratore", "Worker"),
 "period": ("Période (quinzaine)", "Periodo (quindicina)", "Period (fortnight)"),
 "gen_fiche": ("🖨️ Générer / Imprimer la fiche", "🖨️ Genera / Stampa la fiche", "🖨️ Generate / Print slip"),
 "buste_none": ("Aucune paie enregistrée.", "Nessuna paga registrata.", "No payroll recorded."),
 "quinz1": ("1 → 15", "1 → 15", "1 → 15"), "quinz2": ("16 → fin du mois", "16 → fine mese", "16 → end of month"),
 "lordo": ("Brut", "Lordo", "Gross"), "netto": ("Net", "Netto", "Net"),
 "trattenute": ("Retenues", "Trattenute", "Deductions"), "giorni": ("Jours", "Giorni", "Days"),
 "ore_n": ("Heures norm.", "Ore norm.", "Normal hrs"), "ore_s": ("Heures sup.", "Ore stra", "Overtime"),
}
def t6(k, lingua="fr"):
    t = T6.get(k)
    return k if not t else t[{"fr": 0, "it": 1, "en": 2}.get(lingua, 0)]
_PDF_MAP = {"→": "->", "–": "-", "—": "-", "•": "-", "…": "...", "’": "'", "‘": "'", "“": '"', "”": '"', "≤": "<=", "≥": ">=", "€": "EUR", "Œ": "OE", "œ": "oe", "⚠": "!", "✅": "[OK]", "⭐": "*", "📈": "^", "⛔": "X", "➡": "->", "\xa0": " ", "★": "*", "☆": "*", "←": "<-"}
def _pdf_safe(s):
    out = []
    for ch in str(s or ""):
        if ch in _PDF_MAP: out.append(_PDF_MAP[ch]); continue
        try:
            ch.encode("latin-1"); out.append(ch)
        except Exception: out.append("?")
    return "".join(out)
def _f(v, d=0.0):
    try: return float(str(v).replace(",", "."))
    except Exception: return float(d)
def _cfgf(A, k, d):
    return _f(A.cfg_get(k, str(d)), d)
def _ir_bareme(A):
    s = A.cfg_get("ir_bareme_mensile", "35000|0;66333|12.1;133333|20.4;216666|25.3;333333|30.3;566666|38.1;1000000000|42.7")
    out = []
    for chunk in s.split(";"):
        if "|" in chunk:
            a, b = chunk.split("|")
            out.append((_f(a), _f(b)))
    return out
def _ir_su(imponibile, bareme, half):
    imp = max(0.0, imponibile)
    prev = 0.0; tax = 0.0
    for i, (lim, rate) in enumerate(bareme):
        L = lim / 2.0 if half else lim
        if imp <= L:
            tax += (imp - prev) * rate / 100.0; return tax
        if i == 0 and imp <= (0 if not half else 0):
            continue
        tax += (L - prev) * rate / 100.0; prev = L
    return tax
def _trattenute(A, lordo, half):
    if str(A.cfg_get("trattenute_legali_attive", "NO")).upper() != "SI":
        return {"css": 0, "ipres": 0, "ipm": 0, "ir": 0, "tot": 0}
    css_p = _cfgf(A, "css_lavoratore_percent", 5.6); css_pl = _cfgf(A, "css_plafond_mensile", 285000)
    ipm_p = _cfgf(A, "ipm_lavoratore_percent", 2.5); ipm_pl = _cfgf(A, "ipm_plafond_mensile", 285000)
    fp_p = _cfgf(A, "ir_frais_prof_percent", 20); fp_pl = _cfgf(A, "ir_frais_prof_plafond_mensile", 125000)
    div = 2.0 if half else 1.0
    b_css = min(lordo, css_pl / div); css = b_css * css_p / 100.0
    b_ipm = min(lordo, ipm_pl / div); ipm = b_ipm * ipm_p / 100.0
    tiers = [(_cfgf(A, "ipres_t1_plafond", 291600), _cfgf(A, "ipres_t1_lav_percent", 2.8)),
             (_cfgf(A, "ipres_t2_plafond", 583200), _cfgf(A, "ipres_t2_lav_percent", 6.1)),
             (_cfgf(A, "ipres_t3_plafond", 874800), _cfgf(A, "ipres_t3_lav_percent", 10.2))]
    ipres = 0.0; prev = 0.0
    for lim, rate in tiers:
        L = lim / div
        if lordo > prev:
            ipres += (min(lordo, L) - prev) * rate / 100.0
        prev = L
    fp = min(lordo * fp_p / 100.0, fp_pl / div)
    impon = lordo - css - ipres - ipm - fp
    ir = _ir_su(max(0, impon), _ir_bareme(A), half)
    tot = css + ipres + ipm + ir
    return {"css": round(css), "ipres": round(ipres), "ipm": round(ipm), "ir": round(ir), "tot": round(tot)}
def _period_range(anno, mese, quind):
    import calendar
    last = calendar.monthrange(anno, mese)[1]
    if quind == 1: return date(anno, mese, 1), date(anno, mese, 15)
    return date(anno, mese, 16), date(anno, mese, last)
def calcola_anteprima(A, lingua, anno, mese, quind):
    d0, d1 = _period_range(anno, mese, quind)
    _, sal = A.leggi_foglio("SALARI")
    _, pres = A.leggi_foglio("IMPORT_PRESENZE")
    attivi = {}
    for s in sal:
        cod = A.s_str(s.get("codice_lavoratore"))
        if cod and not A.s_str(s.get("data_fine_validita")):
            attivi[cod] = s
    agg = {}
    for p in pres:
        cod = A.s_str(p.get("codice")) or A.s_str(p.get("codice_lavoratore"))
        if not cod: continue
        do = A.data_ord(p.get("data"))
        if not do: continue
        dd = date(*do)
        if not (d0 <= dd <= d1): continue
        ore = _f(p.get("ore"))
        stra = _f(p.get("straordinario"))
        a = agg.setdefault(cod, {"g": 0, "on": 0.0, "os": 0.0})
        if ore > 0 or stra > 0: a["g"] += 1
        a["on"] += ore; a["os"] += stra
    dets = []
    for cod, s in attivi.items():
        tipo = A.s_str(s.get("tipo_paga")) or "giornaliero"
        base = _f(s.get("importo_base"))
        a = agg.get(cod, {"g": 0, "on": 0.0, "os": 0.0})
        if tipo == "giornaliero":
            lordo = base * a["g"] + (base / 8.0) * a["os"] * 1.5
        elif tipo == "orario":
            lordo = base * a["on"] + base * a["os"] * 1.5
        else:
            lordo = base / 2.0 + (base / 173.0) * a["os"] * 1.5
        lordo = round(lordo)
        tr = _trattenute(A, lordo, True)
        dets.append({"code": cod, "nome": A.s_str(s.get("nome")) or cod, "tipo": tipo, "base": base,
                     "giorni": a["g"], "ore_n": a["on"], "ore_s": a["os"], "lordo": lordo,
                     "css": tr["css"], "ipres": tr["ipres"], "ipm": tr["ipm"], "ir": tr["ir"],
                     "tot_trat": tr["tot"], "netto": lordo - tr["tot"]})
    dets.sort(key=lambda x: x["code"])
    return {"dets": dets, "da": d0, "a": d1}
def genera_busta_paga(A, lingua, dip, det, pago, storico, acconti):
    az = A.azienda_info()
    pdf = FPDF(); pdf.set_auto_page_break(True, 15); pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _pdf_safe(az.get("nome", "")), 0, 1, "C")
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 4, _pdf_safe(az.get("indirizzo", "")), 0, 1, "C")
    pdf.cell(0, 4, _pdf_safe(f"tel. {az.get('tel','')} - {az.get('email','')} - {az.get('fisc','')}"), 0, 1, "C")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, _pdf_safe(f"FICHE DE PAIE - {A.s_str(pago.get('periodo_da'))} / {A.s_str(pago.get('periodo_a'))}"), 0, 1, "C")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, _pdf_safe(f"Travailleur : {A.s_str(dip.get('cognome'))} {A.s_str(dip.get('nome'))}   Code : {A.s_str(dip.get('codice'))}"), 0, 1, "L")
    pdf.cell(0, 6, _pdf_safe(f"CNI : {A.s_str(dip.get('cni')) or '---'}   CSS : {A.s_str(dip.get('css'))}   IPRES : {A.s_str(dip.get('ipres'))}"), 0, 1, "L")
    pdf.cell(0, 6, _pdf_safe(f"Type : {A.s_str(pago.get('tipo_pagamento')) or A.s_str(pago.get('tipo_paga'))}"), 0, 1, "L")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, _pdf_safe(f"Brut : {A.s_str(pago.get('importo_lordo'))} FCFA"), 0, 1, "L")
    pdf.set_font("Helvetica", "", 9)
    if det:
        pdf.cell(0, 5, _pdf_safe(f"Jours : {det['giorni']}   Heures norm. : {det['ore_n']}   Heures sup. : {det['ore_s']}"), 0, 1, "L")
    pdf.cell(0, 5, _pdf_safe(f"Retenues CSS : {A.s_str(pago.get('trattenute_css')) or 0}   IPRES : {A.s_str(pago.get('trattenute_ipres')) or 0}   IPM : {A.s_str(pago.get('trattenute_ipm')) or 0}   IR : {A.s_str(pago.get('trattenute_ir')) or 0}"), 0, 1, "L")
    pdf.cell(0, 5, _pdf_safe(f"Avances deduites : {A.s_str(pago.get('acconti_dedotti')) or 0}   Premis : {A.s_str(pago.get('premi_produzione')) or 0}"), 0, 1, "L")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, _pdf_safe(f"NET A PAYER : {A.s_str(pago.get('importo_netto'))} FCFA"), 0, 1, "L")
    pdf.ln(3)
    if storico:
        pdf.set_font("Helvetica", "B", 9); pdf.cell(0, 6, "Historique :", 0, 1, "L")
        pdf.set_font("Helvetica", "", 8)
        for s in storico:
            pdf.cell(0, 5, _pdf_safe(f"- {A.s_str(s.get('periodo_da'))} -> {A.s_str(s.get('periodo_a'))} : NET {A.s_str(s.get('importo_netto'))} FCFA"), 0, 1, "L")
    if acconti:
        pdf.ln(2); pdf.set_font("Helvetica", "B", 9); pdf.cell(0, 6, "Avances :", 0, 1, "L")
        pdf.set_font("Helvetica", "", 8)
        for a in acconti:
            pdf.cell(0, 5, _pdf_safe(f"- {A.s_str(a.get('data'))} : {A.s_str(a.get('importo'))} FCFA ({A.s_str(a.get('motivo'))})"), 0, 1, "L")
    pdf.ln(6); pdf.set_font("Helvetica", "", 9)
    pdf.cell(90, 8, "Signature employeur", 1, 0, "C"); pdf.cell(10, 8, "", 0, 0); pdf.cell(90, 8, "Signature travailleur", 1, 1, "C")
    out = pdf.output(dest="S")
    return out.encode("latin-1", "ignore") if isinstance(out, str) else bytes(out)
def sezione_import(A, lingua):
    st.subheader("📥 " + t6("import_title", lingua))
    st.caption("Collez le contenu « List of Logs » OU chargez le .XLS puis « Analyser ».")
    c1, c2 = st.columns([3, 1])
    anno = c1.number_input(t6("anno", lingua), value=datetime.now().year, key="imp_anno")
    mesi = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    mese = c2.selectbox(t6("mese", lingua), mesi, index=datetime.now().month - 1, key="imp_mese") + 1
    up = st.file_uploader("Fichier .XLS à analyser", type=["xls", "xlsx", "csv"], key="imp_file")
    if st.button(t6("analizza", lingua), use_container_width=True):
        if up is not None:
            try:
                import xlrd
                wb = xlrd.open_workbook(file_contents=up.read())
                sh = wb.sheet_by_index(0)
                rows = [[str(c) for c in sh.row_values(i)] for i in range(sh.nrows)]
                st.session_state["imp_rows"] = rows
                st.success(f"Lues {len(rows)} lignes.")
            except Exception as e:
                st.error(f"Impossible de lire le fichier. — {e}")
        else:
            st.warning("Chargez un fichier .XLS/.CSV.")
    if st.session_state.get("imp_rows"):
        st.markdown("Contenu du fichier")
        st.dataframe(st.session_state["imp_rows"][:50])
def sezione_anomalie(A, lingua):
    st.subheader("🔍 " + t6("anom_title", lingua))
    _, pres = A.leggi_foglio("IMPORT_PRESENZE")
    anom = [p for p in pres if str(p.get("stato")).lower() in ("anomalie", "anomalia", "da_rivedere", "da rivedere")]
    if not anom:
        st.success("Aucune anomalie.")
        return
    for p in anom:
        st.markdown(f"- {A.s_str(p.get('codice'))} {A.s_str(p.get('data'))} — {A.s_str(p.get('note')) or 'à vérifier'}")
def sezione_paghe(A, lingua):
    st.subheader("💰 " + t6("paghe_title", lingua))
    c1, c2, c3 = st.columns(3)
    anno = c1.number_input(t6("anno", lingua), value=datetime.now().year, key="pag_anno")
    mesi = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    mese = c2.selectbox(t6("mese", lingua), mesi, index=datetime.now().month - 1, key="pag_mese") + 1
    quind = 1 if c3.radio("Quinzaine", [t6("quinz1", lingua), t6("quinz2", lingua)], key="pag_q") == t6("quinz1", lingua) else 2
    if st.button(t6("calcola", lingua), type="primary", use_container_width=True):
        ant = calcola_anteprima(A, lingua, anno, mese, quind)
        st.session_state["pag_ant"] = ant
    ant = st.session_state.get("pag_ant")
    if ant:
        st.dataframe([{ "Code": d["code"], "Jours": d["giorni"], "Brut": d["lordo"], "Retenues": d["tot_trat"], "Net": d["netto"] } for d in ant["dets"]])
        if st.button(t6("conferma", lingua), type="primary", use_container_width=True):
            now = datetime.now().strftime("%d/%m/%Y")
            rows = []
            for d in ant["dets"]:
                rows.append({"id_pagamento": f"PAG-{datetime.now().strftime('%Y%m%d')}-{d['code']}",
                             "codice_lavoratore": d["code"], "periodo_da": ant["da"].strftime("%d/%m/%Y"),
                             "periodo_a": ant["a"].strftime("%d/%m/%Y"), "tipo_pagamento": d["tipo"],
                             "importo_lordo": d["lordo"], "acconti_dedotti": 0, "premi_produzione": 0,
                             "importo_netto": d["netto"], "data_pagamento": now, "stato": "confermato",
                             "trattenute_css": d["css"], "trattenute_ipres": d["ipres"], "trattenute_ipm": d["ipm"],
                             "trattenute_ir": d["ir"], "trattenute_totale": d["tot_trat"]})
            ok, msg = A.salva_append_many("PAGAMENTI", rows)
            if ok: st.success(f"Écrites {len(rows)} paies.")
            else: st.error(msg)
def sezione_acconti(A, lingua):
    st.subheader("💸 " + t6("acc_title", lingua))
    _, acc = A.leggi_foglio("ACCONTI")
    for a in acc[:30]:
        st.markdown(f"- {A.s_str(a.get('codice_lavoratore'))} {A.s_str(a.get('data'))} : {A.s_str(a.get('importo'))} FCFA ({A.s_str(a.get('stato'))})")
def sezione_buste(A, lingua):
    st.subheader(t6("buste_title", lingua))
    dips = A.leggi_admin().get("DIPENDENTI", [])
    _, pays = A.leggi_foglio("PAGAMENTI")
    _, accs = A.leggi_foglio("ACCONTI")
    opzioni, codmap = [], {}
    for d in dips:
        cod = A.s_str(d.get("codice"))
        if cod:
            lab = f"{cod} — {A.s_str(d.get('cognome'))} {A.s_str(d.get('nome'))}"
            opzioni.append(lab); codmap[lab] = cod
    if not opzioni:
        st.info("Aucun travailleur."); return
    lab = st.selectbox(t6("travailleur", lingua), opzioni, key="f6_buste_worker")
    cod = codmap[lab]
    miei = [p for p in pays if A.s_str(p.get("codice_lavoratore")).upper() == cod.upper()]
    miei.sort(key=lambda p: A.data_ord(p.get("periodo_da")) or (0, 0, 0), reverse=True)
    if not miei:
        st.info(t6("buste_none", lingua)); return
    opts = [f"{A.s_str(p.get('periodo_da'))} -> {A.s_str(p.get('periodo_a'))}" for p in miei]
    sel = st.selectbox(t6("period", lingua), opts, key="f6_buste_period")
    pago = miei[opts.index(sel)]
    mio = next((d for d in dips if A.s_str(d.get("codice")).upper() == cod.upper()), None)
    if st.button(t6("gen_fiche", lingua), type="primary", use_container_width=True):
        det = None
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", A.s_str(pago.get("periodo_da")))
        if m:
            dd, mm, yy = map(int, m.groups())
            try:
                ant = calcola_anteprima(A, lingua, yy, mm, 1 if dd == 1 else 2)
                det = next((x for x in ant["dets"] if x["code"].upper() == cod.upper()), None)
            except Exception:
                det = None
        acconti = [a for a in accs if A.s_str(a.get("codice_lavoratore")).upper() == cod.upper() and A.s_str(a.get("stato")).lower() not in ("annullato",)]
        st.download_button("📥 PDF", data=genera_busta_paga(A, lingua, mio, det, pago, miei, acconti),
                           file_name=f"Busta_{cod}_{A.s_str(pago.get('periodo_da'))}.pdf", mime="application/pdf", use_container_width=True)
def sezione_releve(A, lingua):
    st.subheader(t6("releve_title", lingua))
    _, pres = A.leggi_foglio("IMPORT_PRESENZE")
    st.dataframe([{ "Code": A.s_str(p.get("codice")), "Data": A.s_str(p.get("data")), "Ore": A.s_str(p.get("ore")), "Stra": A.s_str(p.get("straordinario")) } for p in pres[:100]])
def sezione_solde(A, lingua):
    st.subheader(t6("solde_title", lingua))
    st.info("Module de solde de tout compte : sélectionnez un travailleur archivé pour générer le décompte final.")
def pagina_fase7(lingua, A):
    st.caption(VERSIONE)
    with st.expander("⚙️ CONFIG"):
        st.caption("Aliquote e parametri letti da CONFIG (modificabili senza codice).")
    tabs = st.tabs(["📥 Import", "🔍 " + t6("anom_title", lingua), "💰 " + t6("paghe_title", lingua),
                    "💸 " + t6("acc_title", lingua), t6("buste_title", lingua),
                    t6("releve_title", lingua), t6("solde_title", lingua)])
    with tabs[0]: sezione_import(A, lingua)
    with tabs[1]: sezione_anomalie(A, lingua)
    with tabs[2]: sezione_paghe(A, lingua)
    with tabs[3]: sezione_acconti(A, lingua)
    with tabs[4]: sezione_buste(A, lingua)
    with tabs[5]: sezione_releve(A, lingua)
    with tabs[6]: sezione_solde(A, lingua)