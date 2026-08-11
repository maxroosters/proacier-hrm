# -*- coding: utf-8 -*-
"""
PROACIER HRM – FASE 6 (Pagina 2) : Présences & Paies  [v07.05]
✅ v07.05: upload "Envoyer au cloud" e download "Prélever du cloud" con auth Basic
   (legge url_presenze_user/pass dal CONFIG) → funziona con Directory Privacy ATTIVA
✅ Include: parser List of Logs, anomalie, paghe quindicina, acconti,
   storico mansioni/sanzioni/performance letti da app, upload/download XLS
Richiede: Apps Script v6.1 + upload.php su /presenze/ + Directory Privacy attiva
"""
import re
import math
import random
import calendar
import csv
import io
import requests
from datetime import datetime, date
import streamlit as st

VERSIONE_PAGHE = "07.05"

LINGUE = {"fr": 0, "it": 1, "en": 2}

MESI = {
    "fr": ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"],
    "it": ["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"],
    "en": ["January","February","March","April","May","June","July","August","September","October","November","December"],
}
GIORNI_SETTIMANA = ["lunedi","martedi","mercoledi","giovedi","venerdi","sabato","domenica"]

T6 = {
 "titolo": ("🕒 Présences & Paies","🕒 Presenze e Paghe","🕒 Attendance & Payroll"),
 "import_title": ("Importation des pointages","Importazione presenze","Attendance import"),
 "import_hint": ("Collez le contenu « List of Logs » OU chargez/prélevez le fichier .XLS du cloud.","Incolla il contenuto « List of Logs » OPPURE carica/preleva il file .XLS dal cloud.","Paste the “List of Logs” content OR upload/fetch the .XLS from the cloud."),
 "import_da_testo": ("Contenu du fichier","Contenuto del file","File content"),
 "import_up_label": ("Fichier .XLS à envoyer au cloud","File .XLS da inviare al cloud",".XLS file to send to cloud"),
 "import_up_btn": ("Envoyer au cloud","Invia al cloud","Send to cloud"),
 "import_cloud_btn": ("Prélever du cloud (mois choisi)","Preleva dal cloud (mese scelto)","Fetch from cloud (chosen month)"),
 "import_parse_btn": ("Analyser le fichier","Analizza il file","Parse file"),
 "import_write_btn": ("Enregistrer dans PRESENZE","Scrivi in PRESENZE","Write to PRESENZE"),
 "import_empty": ("Collez d'abord le contenu du fichier","Prima incolla il contenuto del file","Paste the file content first"),
 "import_up_err": ("Échec de l'envoi. Vérifiez upload.php / token / Directory Privacy.","Invio fallito. Verifica upload.php / token / Directory Privacy.","Upload failed. Check upload.php / token / Directory Privacy."),
 "parsed_none": ("❌ Impossible de lire le fichier.","❌ Impossibile leggere il file.","❌ Cannot read the file."),
 "parsed_ok": ("✅ Fichier analysé","✅ File analizzato","✅ File parsed"),
 "import_period": ("Période","Periodo","Period"),
 "import_workers": ("travailleurs détectés","lavoratori rilevati","workers detected"),
 "import_written": ("présences écrites","presenze scritte","attendances written"),
 "import_dup": ("déjà présentes (ignorées)","già presenti (ignorate)","already present (skipped)"),
 "import_unmapped": ("⚠️ Non mappati: aggiungere riga in MAPPING_PRESENZE → ","⚠️ Non mappati: aggiungere riga in MAPPING_PRESENZE → ","⚠️ Unmapped: add a row in MAPPING_PRESENZE → "),
 "import_go_anomalies": ("Passez à « Anomalies » pour corriger les DA_RIVEDERE.","Vai in « Anomalie » per correggere i DA_RIVEDERE.","Go to “Anomalies” to fix DA_RIVEDERE."),
 "anom_title": ("Anomalies & absences","Anomalie e assenze","Anomalies & absences"),
 "anom_none": ("✅ Aucune anomalie.","✅ Nessuna anomalia.","✅ No anomalies."),
 "anom_hint": ("DA_RIVEDERE = pointage incomplet. Modifiez puis « Enregistrer tout ».","DA_RIVEDERE = timbratura incompleta. Modifica poi « Salva tutto ».","DA_RIVEDERE = incomplete punch. Edit then “Save all”."),
 "anom_uscita": ("Heure de sortie (HH:MM)","Ora uscita (HH:MM)","Clock-out (HH:MM)"),
 "anom_stato": ("Statut","Stato","Status"),
 "anom_note": ("Note","Nota","Note"),
 "anom_save_all": ("💾 Enregistrer toutes les corrections","💾 Salva tutte le correzioni","💾 Save all corrections"),
 "anom_fixed_n": ("corrections enregistrées","correzioni salvate","corrections saved"),
 "anom_need_out": ("Pour OK il faut une heure de sortie valide","Per OK serve un'ora di uscita valida","For OK a valid clock-out is needed"),
 "paghe_title": ("Calcul des paies (quinzaine)","Calcolo paghe (quindicina)","Payroll (fortnight)"),
 "paghe_anno": ("Année","Anno","Year"),
 "paghe_mese": ("Mois","Mese","Month"),
 "paghe_quindicina": ("Quinzaine","Quindicina","Fortnight"),
 "paghe_q1": ("1 → 15","1 → 15","1 → 15"),
 "paghe_q2": ("16 → fin du mois","16 → fine mese","16 → end of month"),
 "paghe_calc_btn": ("Calculer","Calcola","Calculate"),
 "paghe_periodo": ("Période de paie","Periodo paga","Pay period"),
 "paghe_nulla": ("ℹ️ Aucune activité ni salaire.","ℹ️ Nessuna attività né salario.","ℹ️ No activity or salary."),
 "paghe_no_salario": ("pas de salaire actif (ignoré)","nessun salario attivo (ignorato)","no active salary (skipped)"),
 "paghe_gia": ("déjà payé (ignoré)","già pagato (ignorato)","already paid (skipped)"),
 "paghe_confirm_btn": ("Confirmer et écrire dans PAGAMENTI","Conferma e scrivi in PAGAMENTI","Confirm and write to PAGAMENTI"),
 "paghe_done": ("✅ Paies confirmées : ","✅ Paghe confermate: ","✅ Payrolls confirmed: "),
 "dar_warn": ("ligne(s) DA_RIVEDERE exclue(s) — corrigez dans Anomalies puis recalculez","riga/e DA_RIVEDERE escluse — correggi in Anomalie poi ricalcola","DA_RIVEDERE row(s) excluded — fix in Anomalies then recalc"),
 "premi_title": ("Prix de production (FCFA)","Premi produzione (FCFA)","Production bonuses (FCFA)"),
 "tot_lordo": ("Total brut","Totale lordo","Total gross"),
 "tot_acc": ("Total avances déduites","Totale acconti dedotti","Total advances deducted"),
 "tot_netto": ("Total net (sans prix)","Totale netto (senza premi)","Total net (without bonuses)"),
 "netto_hint": ("Le net final tient compte des prix saisis ci-dessus.","Il netto finale tiene conto dei premi inseriti.","Final net includes the bonuses entered."),
 "col_codice": ("Code","Codice","Code"),
 "col_nome": ("Nom","Nome","Name"),
 "col_tipo": ("Type","Tipo","Type"),
 "col_base": ("Tarif","Tariffa","Rate"),
 "col_giorni": ("Jours","Giorni","Days"),
 "col_ore": ("Heures","Ore","Hours"),
 "col_stra": ("H. supp.","Straord.","OT hrs"),
 "col_rit": ("Retards (½h)","Ritardi (½h)","Delays (½h)"),
 "col_abs": ("Abs.","Ass.","Abs."),
 "col_lordo": ("Brut (FCFA)","Lordo (FCFA)","Gross (FCFA)"),
 "col_acc": ("Avances (FCFA)","Acconti (FCFA)","Advances (FCFA)"),
 "acc_title": ("Avances","Acconti","Advances"),
 "acc_new": ("Nouvelle avance","Nuovo acconto","New advance"),
 "acc_codice": ("Travailleur","Lavoratore","Worker"),
 "acc_tipo": ("Type d'avance","Tipo acconto","Advance type"),
 "acc_generico": ("Générique","Generico","Generic"),
 "acc_tabasky": ("Tabaski","Tabaski","Tabaski"),
 "acc_scuola": ("École","Scuola","School"),
 "acc_karem": ("Karêm","Karem","Karem"),
 "acc_importo": ("Montant (FCFA)","Importo (FCFA)","Amount (FCFA)"),
 "acc_modalita": ("Remboursement","Rimborso","Repayment"),
 "acc_unica": ("Une seule fois","Unica soluzione","One-off"),
 "acc_rate": ("Par versements","A rate","Installments"),
 "acc_num_rate": ("Nombre de versements","Numero rate","Number of installments"),
 "acc_data_rich": ("Date demande (JJ/MM/AAAA)","Data richiesta (GG/MM/AAAA)","Request date (DD/MM/YYYY)"),
 "acc_data_ero": ("Date paiement (JJ/MM/AAAA)","Data erogazione (GG/MM/AAAA)","Payment date (DD/MM/YYYY)"),
 "acc_crea_btn": ("Créer l'avance","Crea acconto","Create advance"),
 "acc_created": ("✅ Avance enregistrée","✅ Acconto registrato","✅ Advance saved"),
 "acc_open_title": ("Avances ouvertes","Acconti aperti","Open advances"),
 "acc_none": ("ℹ️ Aucune avance ouverte.","ℹ️ Nessun acconto aperto.","ℹ️ No open advances."),
 "acc_err": ("Sélectionnez un travailleur et un montant > 0","Seleziona un lavoratore e un importo > 0","Select a worker and amount > 0"),
 "acc_dedotto": ("sera déduit à la prochaine paie","sarà dedotto alla prossima paga","will be deducted at next payroll"),
}

def t6(k, lingua="fr"):
    v = T6.get(k)
    return k if not v else v[LINGUE.get(lingua, 0)]

def s_str(v):
    if v is None: return ""
    s = str(v)
    if s in ("nan","None","#ERROR!"): return ""
    return s.strip()

def to_min(t):
    try:
        p = str(t).strip().split(":")
        return int(p[0])*60 + int(p[1])
    except Exception:
        return None

def to_float(s):
    try: return float(str(s).replace(",",".").strip())
    except Exception: return 0.0

def to_float_or_none(s):
    try: return float(str(s).replace(",",".").strip())
    except Exception: return None

def parse_data(s):
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s_str(s))
    if not m: return None
    d,mo,y = map(int, m.groups())
    try: return date(y,mo,d)
    except Exception: return None

def data_ord(s):
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s_str(s))
    if not m: return None
    d,mo,y = map(int, m.groups())
    return (y,mo,d)

def timbro_notte(t):
    m = to_min(t)
    return m is not None and (m < 2*60 or m >= 23*60)

def etichetta(tipo, valore, lingua="fr"):
    v = s_str(valore)
    if not v: return ""
    for o in OPZ.get(tipo, []):
        if v in o: return o[LINGUE.get(lingua,0)+1]
    return v

OPZ = {
 "tipo_visita": [("assunzione","Visite d'embauche","Visita di assunzione","Hiring visit"),("periodica","Visite périodique","Visita periodica","Periodic visit"),("straordinaria","Visite extraordinaire","Visita straordinaria","Extraordinary visit")],
 "idoneita": [("apte","Apte","Apto","Fit"),("restriction","Apte avec restriction","Apto con restrizioni","Fit with restrictions"),("inapte","Inapte","Inapto","Unfit")],
 "tipo_paga": [("giornaliero","Journalier","Giornaliero","Daily"),("orario","Horaire","Orario","Hourly"),("mensile","Mensuel","Mensile","Monthly")],
}

DEFAULT_CONFIG = {
 "straordinario_1_percent": 25.0, "straordinario_2_percent": 50.0,
 "ore_normali_giorno": 8.0, "modalita_paga": "giornaliero",
 "ritardo_tolleranza_min": 15.0, "ritardo_metodo": "mezzora", "assenza_penale_percent": 0.0,
}

def leggi_config(A):
    cfg = dict(DEFAULT_CONFIG)
    festivi = {}
    riposo = {"sabato","domenica"}
    flottanti = set()
    soglia_notte = 3*60
    try:
        _, recs = A.leggi_foglio("CONFIG")
    except Exception:
        recs = []
    for r in recs:
        k = A.s_str(r.get("chiave")).strip().lower().replace(" ","_")
        v = A.s_str(r.get("valore")).strip()
        if not k: continue
        if k.startswith("festivo_"):
            ds = k.replace("festivo_","",1)
            try:
                y,m,g = ds.split("-")
                festivi[f"{int(g):02d}/{int(m):02d}/{y}"] = v or "Férié"
            except Exception: pass
        elif k == "riposo_settimanale":
            if v: riposo = {x.strip().lower() for x in v.split(",") if x.strip()}
        elif k == "turni_flottanti":
            if v: flottanti = {x.strip().upper() for x in v.split(",") if x.strip()}
        elif k == "soglia_uscita_notturna":
            m2 = to_min(v)
            if m2 is not None: soglia_notte = m2
        elif k.startswith("assenza"):
            f = to_float_or_none(v)
            if f is not None: cfg["assenza_penale_percent"] = f
        elif k in ("straordinario_1_percent","straordinario_2_percent","ore_normali_giorno","ritardo_tolleranza_min"):
            f = to_float_or_none(v)
            if f is not None: cfg[k] = f
        elif k in ("modalita_paga","ritardo_metodo"):
            if v: cfg[k] = v.lower()
    if not festivi:
        festivi = {}
        cfg["_festivi_default"] = True
    cfg["_riposo"] = riposo
    cfg["_flottanti"] = flottanti
    cfg["_soglia_notte"] = soglia_notte
    return cfg, festivi

def _auth_presenze(A):
    """v07.05: legge url_presenze_user/pass dal CONFIG → tuple (user,pass) per auth Basic."""
    up = A.cfg_get("url_presenze_user/pass", "")
    if up and ":" in up:
        u, p = up.split(":", 1)
        return (u.strip(), p.strip())
    return None

def mappa_turni(A, recs_turni):
    info = {}
    for r in recs_turni:
        ct = A.s_str(r.get("codice_turno")).strip().upper()
        if not ct or ct in ("REGOLE",): continue
        attr = A.s_str(r.get("attraversa_mezzanotte")).strip().lower() in ("si","sì","oui","yes","true","1","vrai")
        oi = A.s_str(r.get("ora_inizio")).strip()
        start = to_min(oi) if re.match(r"^\d{1,2}:\d{2}", oi) else None
        if start is None and not oi: continue
        info[ct] = {"attr": attr, "start": start}
    info.setdefault("T1", {"attr": False, "start": 8*60})
    info.setdefault("T2", {"attr": True, "start": 16*60})
    info.setdefault("T3", {"attr": False, "start": 0})
    info.setdefault("EQUIPE", {"attr": False, "start": 4*60})
    return info

TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")

def _extract_day_map(celle):
    nums = []
    for ci, cv in enumerate(celle):
        cv2 = cv.strip().strip('"')
        if cv2.isdigit() and 1 <= int(cv2) <= 31:
            nums.append((ci, int(cv2)))
    if len(nums) >= 15:
        return {ci: dv for ci, dv in nums}
    return None

def _cell_times(cv):
    out = []
    for tok in re.split(r'[\s,;/"]+', str(cv).strip()):
        mt = TIME_RE.match(tok)
        if mt and int(mt.group(1)) < 24:
            out.append(f"{int(mt.group(1)):02d}:{mt.group(2)}")
    return out

def _is_header(r):
    j = "\t".join(r)
    return re.search(r"No\s*:", j, re.I) and re.search(r"Name\s*:", j, re.I)

def _build_blocchi(rows, get_name):
    anno = mese = g1 = g2 = None
    for r in rows:
        m = re.search(r"Period\s*:\s*(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})\s*~\s*(\d{1,2})(?:[/\-.](\d{1,2}))?", "\t".join(r), re.I)
        if m:
            anno, mese, g1 = int(m.group(1)), int(m.group(2)), int(m.group(3))
            g2 = int(m.group(5)) if m.group(5) else int(m.group(4))
            break
    if g2 is not None and g2 < (g1 or 1): g2 = g1
    blocchi = []
    i, n = 0, len(rows)
    while i < n:
        if _is_header(rows[i]):
            nome = get_name(rows[i])
            day_map = {}
            for j in list(range(max(0,i-3), i)) + list(range(i+1, min(n,i+4))):
                dm = _extract_day_map(rows[j])
                if dm: day_map = dm; break
            per_giorno = {}
            j = i+1
            while j < n and not _is_header(rows[j]):
                if not _extract_day_map(rows[j]):
                    for ci, cv in enumerate(rows[j]):
                        for t in _cell_times(cv):
                            g = day_map.get(ci)
                            if g is None: g = ci+1 if 1 <= ci+1 <= 31 else None
                            if g: per_giorno.setdefault(int(g), []).append(t)
                j += 1
            blocchi.append({"nome": nome, "per_giorno": per_giorno})
            i = j
        else:
            i += 1
    return {"anno": anno, "mese": mese, "g1": g1 or 1, "g2": g2 or 31, "blocchi": blocchi}

def parse_list_of_logs(testo):
    rows = list(csv.reader(io.StringIO(testo.replace("\r","")), delimiter="\t"))
    def get_name(r):
        m = re.search(r"Name\s*:\s*([^|\t]+)", "\t".join(r), re.I)
        return m.group(1).strip().strip('"') if m else ""
    return _build_blocchi(rows, get_name)

def parse_matrix(rows):
    def get_name(r):
        for ci, cv in enumerate(r):
            if re.search(r"Name\s*:", str(cv), re.I):
                return str(r[ci+1]).strip() if ci+1 < len(r) else ""
        return ""
    return _build_blocchi(rows, get_name)

def resolve_code(nome, mapping, codici_dip, A):
    n = _norm_nome(nome)
    if not n: return None, ""
    if n in codici_dip: return n, ""
    for m in mapping:
        nm = _norm_nome(m.get("nome_macchina"))
        nmach = A.s_str(m.get("n_macchina")).strip().upper()
        if n and n in (nm, nmach):
            cod = A.s_str(m.get("codice_lavoratore")).strip().upper()
            if cod: return cod, A.s_str(nome)
    for c in codici_dip:
        if c and c in n: return c, A.s_str(nome)
    return None, A.s_str(nome)

def _norm_nome(s):
    s = re.sub(r"\s+"," ", str(s or "")).strip().upper()
    s = re.split(r"\bDEPT\b", s)[0].strip()
    return s

def coppie_giorno(per_giorno, attr, notte_ok, soglia_notte):
    esiti = []
    pending = None
    for g in sorted(per_giorno.keys()):
        times = sorted(set(per_giorno.get(g, [])), key=to_min)
        if not times: continue
        i = 0
        if pending is not None:
            if to_min(times[0]) is not None and to_min(times[0]) <= soglia_notte:
                esiti.append((pending[0], pending[1], times[0], "OK", "uscita dopo mezzanotte (turno doppio)"))
                i = 1
            else:
                esiti.append((pending[0], pending[1], "", "DA_RIVEDERE", "uscita mancante"))
            pending = None
        rest = times[i:]
        if rest and not attr and not notte_ok and pending is None and timbro_notte(rest[0]):
            esiti.append((g, rest[0], "", "DA_RIVEDERE", "timbratura in fascia notturna - verificare"))
            rest = rest[1:]
        if attr and pending is None:
            entrate = [t for t in rest if to_min(t) >= 12*60]
            uscite_next = sorted({t for t in per_giorno.get(g+1, []) if to_min(t) < 12*60}, key=to_min)
            for k, e in enumerate(entrate):
                if k < len(uscite_next):
                    esiti.append((g, e, uscite_next[k], "OK", "uscita dopo mezzanotte"))
                else:
                    pending = (g, e)
            continue
        for k in range(0, len(rest)-1, 2):
            esiti.append((g, rest[k], rest[k+1], "OK", ""))
        if len(rest) % 2 == 1:
            pending = (g, rest[-1])
    if pending is not None:
        esiti.append((pending[0], pending[1], "", "DA_RIVEDERE", "uscita mancante"))
    return esiti

def genera_righe_lavoratore(code, nome_macchina, per_giorno, anno, mese, g1, g2, tinfo, festivi, riposo, flottante, soglia_notte):
    rows = []
    attr = tinfo.get("attr", False)
    start = tinfo.get("start")
    notte_ok = (start is not None and start < 2*60) or flottante
    for (g, ingr, usc, stato, nota) in coppie_giorno(per_giorno, attr, notte_ok, soglia_notte):
        if g < g1 or g > g2: continue
        dstr = f"{g:02d}/{mese:02d}/{anno}"
        ore = 0.0
        if ingr and usc:
            diff = to_min(usc) - to_min(ingr)
            if diff < 0: diff += 24*60
            ore = round(diff/60.0, 2)
        rows.append({"codice_lavoratore": code, "nome_macchina": nome_macchina or code,
            "data": dstr, "ora_ingresso": ingr or "", "ora_uscita": usc or "",
            "ore_lavorate": f"{ore:.2f}", "tipo_giorno": tipo_giorno(anno, mese, g, festivi),
            "stato": stato, "note": nota})
    giorni_timbrati = set(per_giorno.keys())
    if not flottante:
        for g in range(g1, g2+1):
            if g in giorni_timbrati: continue
            tg = tipo_giorno(anno, mese, g, festivi)
            if tg != "feriale": continue
            try: wd = GIORNI_SETTIMANA[date(anno, mese, g).weekday()]
            except ValueError: continue
            if wd in riposo: continue
            rows.append({"codice_lavoratore": code, "nome_macchina": nome_macchina or code,
                "data": f"{g:02d}/{mese:02d}/{anno}", "ora_ingresso": "", "ora_uscita": "",
                "ore_lavorate": "0.00", "tipo_giorno": tg, "stato": "ASSENTE", "note": ""})
    return rows

def tipo_giorno(anno, mese, g, festivi):
    try: d = date(anno, mese, g)
    except ValueError: return "feriale"
    if d.strftime("%d/%m/%Y") in festivi: return "festivo"
    if d.weekday() == 6: return "domenica"
    return "feriale"

def scrivi_presenze(A, parsed):
    _, mapping = A.leggi_foglio("MAPPING_PRESENZE")
    b = A.leggi_admin()
    dips = b.get("DIPENDENTI", [])
    codici_dip = {A.s_str(d.get("codice")).upper() for d in dips if A.s_str(d.get("codice"))}
    turni_dip = {A.s_str(d.get("codice")).upper(): A.s_str(d.get("turno")).upper() for d in dips}
    turni = mappa_turni(A, b.get("TURNI", []))
    cfg, festivi = leggi_config(A)
    riposo = cfg.get("_riposo", {"sabato","domenica"})
    flottanti = cfg.get("_flottanti", set())
    soglia_notte = cfg.get("_soglia_notte", 3*60)
    _, pres_old = A.leggi_foglio("PRESENZE", force=True)
    esistenti = {(A.s_str(p.get("codice_lavoratore")).upper(), A.s_str(p.get("data"))) for p in pres_old}
    rows, unmapped, dup = [], set(), 0
    anno, mese, g1, g2 = parsed["anno"], parsed["mese"], parsed["g1"], parsed["g2"]
    for blk in parsed["blocchi"]:
        code, nome_macchina = resolve_code(blk["nome"], mapping, codici_dip, A)
        if not code:
            unmapped.add(_norm_nome(blk["nome"]))
            continue
        turno_cod = turni_dip.get(code, "")
        flottante = turno_cod in flottanti
        tinfo = turni.get(turno_cod, {"attr": False, "start": None})
        for r in genera_righe_lavoratore(code, nome_macchina, blk["per_giorno"], anno, mese, g1, g2, tinfo, festivi, riposo, flottante, soglia_notte):
            key = (r["codice_lavoratore"], r["data"])
            if key in esistenti: dup += 1; continue
            esistenti.add(key)
            rows.append(r)
    if rows:
        ok, msg = A.salva_append_many("PRESENZE", rows)
        if not ok: return {"ok": False, "msg": msg}
    return {"ok": True, "scritte": len(rows),
        "okn": sum(1 for r in rows if r["stato"]=="OK"),
        "dar": sum(1 for r in rows if r["stato"]=="DA_RIVEDERE"),
        "abs": sum(1 for r in rows if r["stato"]=="ASSENTE"),
        "dup": dup, "unmapped": sorted(unmapped)}

def calcola_busta(pp_list, tipo_paga, base, cfg, turno_start):
    ore_norm = cfg.get("ore_normali_giorno", 8) or 8
    s1 = cfg.get("straordinario_1_percent", 25)
    s2 = cfg.get("straordinario_2_percent", 50)
    toll = cfg.get("ritardo_tolleranza_min", 15)
    pen = cfg.get("assenza_penale_percent", 0)
    if tipo_paga == "orario": v_or = base
    elif tipo_paga == "mensile": v_or = base/26.0/ore_norm
    else: v_or = base/ore_norm
    n_giorni = n_assenze = n_dar = mezzore = 0
    ore_tot = ore_stra = comp_base = comp_stra = 0.0
    for p in pp_list:
        st_ = p["_stato"]
        if st_ in ("ANNULLATA","RIPOSO","MALATTIA","GIUSTIFICATA"): continue
        if st_ == "ASSENTE": n_assenze += 1; continue
        if st_ == "DA_RIVEDERE": n_dar += 1; continue
        if st_ != "OK": continue
        n_giorni += 1
        ore = p["_ore"]
        ore_tot += ore
        extra = max(0.0, ore - ore_norm)
        ore_stra += extra
        mult = (1+s2/100.0) if p.get("tipo_giorno") in ("domenica","festivo") else (1+s1/100.0)
        if tipo_paga == "giornaliero": comp_base += base
        elif tipo_paga == "orario": comp_base += min(ore, ore_norm)*v_or
        comp_stra += extra*v_or*mult
        ingr = str(p.get("ora_ingresso") or "").strip()
        if ingr and turno_start is not None and to_min(ingr) is not None:
            diff = to_min(ingr) - (turno_start + toll)
            if diff > 0: mezzore += math.ceil(diff/30.0)
    trat = mezzore * (v_or/2.0)
    if tipo_paga == "mensile":
        comp_base = base/2.0 - n_assenze*(base/26.0)*(1+pen/100.0)
    elif pen > 0 and n_assenze > 0:
        comp_base -= n_assenze*(base if tipo_paga=="giornaliero" else v_or*ore_norm)*(pen/100.0)
    return {"n_giorni": n_giorni, "n_assenze": n_assenze, "n_dar": n_dar,
        "ore_tot": round(ore_tot,2), "ore_stra": round(ore_stra,2), "mezzore": mezzore,
        "comp_base": comp_base, "comp_stra": comp_stra, "trat_rit": trat,
        "lordo": comp_base + comp_stra - trat}

def pianifica_acconti(code, accs, A):
    ded, piani = 0.0, []
    for idx, a in enumerate(accs):
        if A.s_str(a.get("codice_lavoratore")).upper() != code: continue
        if A.s_str(a.get("stato")).lower() in ("chiuso","annullato"): continue
        imp = to_float(A.s_str(a.get("importo")))
        if imp <= 0: continue
        if "rate" in A.s_str(a.get("modalita_rimborso")).lower():
            nr = max(1, int(to_float(A.s_str(a.get("numero_rate"))) or 1))
            rata = to_float(A.s_str(a.get("importo_rata"))) or (imp/nr)
            rp = int(to_float(A.s_str(a.get("rate_pagate"))))
            if rp >= nr:
                piani.append((idx, {"stato":"chiuso"}, 0.0, a)); continue
            ded += rata
            rp2 = rp+1
            piani.append((idx, {"rate_pagate": str(rp2), "stato": "chiuso" if rp2>=nr else "in_corso"}, rata, a))
        else:
            ded += imp
            piani.append((idx, {"stato":"chiuso"}, imp, a))
    return ded, piani

def calcola_anteprima(A, lingua, anno, mese, quindicina):
    cfg, festivi = leggi_config(A)
    b = A.leggi_admin(force=True)
    dips = b.get("DIPENDENTI", [])
    sals = b.get("SALARI", [])
    turni = mappa_turni(A, b.get("TURNI", []))
    _, pres = A.leggi_foglio("PRESENZE", force=True)
    _, accs = A.leggi_foglio("ACCONTI", force=True)
    _, pays = A.leggi_foglio("PAGAMENTI", force=True)
    g_in = 1 if quindicina == 1 else 16
    g_fine = 15 if quindicina == 1 else calendar.monthrange(anno, mese)[1]
    da, a = date(anno, mese, g_in), date(anno, mese, g_fine)
    pda, paa = da.strftime("%d/%m/%Y"), a.strftime("%d/%m/%Y")
    pres_per, dar_count = {}, 0
    for i, p in enumerate(pres):
        d = parse_data(A.s_str(p.get("data")))
        if not d or not (da <= d <= a): continue
        cod = A.s_str(p.get("codice_lavoratore")).upper()
        if not cod: continue
        pp = dict(p); pp["_idx"] = i
        pp["_ore"] = to_float(A.s_str(p.get("ore_lavorate")))
        pp["_stato"] = A.s_str(p.get("stato")).upper()
        if pp["_stato"] == "DA_RIVEDERE": dar_count += 1
        pres_per.setdefault(cod, []).append(pp)
    dip_map = {A.s_str(d.get("codice")).upper(): d for d in dips}
    sal_map = {}
    for s in sals:
        cod = A.s_str(s.get("codice_lavoratore")).upper()
        if not cod or A.s_str(s.get("data_fine_validita")): continue
        cur = sal_map.get(cod)
        if cur is None: sal_map[cod] = s
        else:
            d1 = parse_data(A.s_str(s.get("data_inizio_validita"))) or date(1900,1,1)
            d0 = parse_data(A.s_str(cur.get("data_inizio_validita"))) or date(1900,1,1)
            if d1 > d0: sal_map[cod] = s
    giapagati = {A.s_str(py.get("codice_lavoratore")).upper() for py in pays
                 if A.s_str(py.get("periodo_da")) == pda and A.s_str(py.get("periodo_a")) == paa}
    dets, avvisi = [], []
    for code in sorted(set(list(pres_per.keys()) + list(sal_map.keys()))):
        dip = dip_map.get(code, {})
        nome = f"{A.s_str(dip.get('cognome'))} {A.s_str(dip.get('nome'))}".strip() or code
        if code in giapagati:
            avvisi.append(f"{code} {nome}: {t6('paghe_gia', lingua)}"); continue
        sal = sal_map.get(code)
        if not sal:
            avvisi.append(f"{code} {nome}: {t6('paghe_no_salario', lingua)}"); continue
        tipo_paga = A.s_str(sal.get("tipo_paga")).lower() or cfg.get("modalita_paga", "giornaliero")
        base = to_float(A.s_str(sal.get("importo_base")))
        turno = A.s_str(dip.get("turno")).upper()
        tinfo = turni.get(turno, {"attr": False, "start": None})
        busta = calcola_busta(pres_per.get(code, []), tipo_paga, base, cfg, tinfo.get("start"))
        ded, piani = pianifica_acconti(code, accs, A)
        if busta["n_giorni"] == 0 and busta["n_assenze"] == 0 and ded == 0: continue
        d = {"code": code, "nome": nome, "tipo_paga": tipo_paga, "base": base, "turno": turno, "ded": ded, "piani": piani}
        d.update(busta)
        dets.append(d)
    return {"pda": pda, "paa": paa, "dets": dets, "avvisi": avvisi, "dar_count": dar_count,
            "festivi_default": cfg.get("_festivi_default", False)}

def conferma_paghe(A, ant):
    rows, piani_totali = [], []
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    for det in ant["dets"]:
        premio = to_float(st.session_state.get(f"f6_premio_{det['code']}", 0))
        lordo, ded = round(det["lordo"]), round(det["ded"])
        rows.append({"id_pagamento": f"PAG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{det['code']}",
            "codice_lavoratore": det["code"], "periodo_da": ant["pda"], "periodo_a": ant["paa"],
            "tipo_pagamento": det["tipo_paga"], "importo_lordo": str(lordo),
            "acconti_dedotti": str(ded), "premi_produzione": str(round(premio)),
            "importo_netto": str(lordo - ded + round(premio)),
            "data_pagamento": datetime.now().strftime("%d/%m/%Y"), "stato": "confermato", "timestamp": ts})
        for idx, upd, imp, _src in det["piani"]:
            if imp > 0: piani_totali.append((idx, upd))
    if rows:
        ok, msg = A.salva_append_many("PAGAMENTI", rows)
        if not ok: return False, msg, 0
    for idx, upd in piani_totali:
        A.salva_update("ACCONTI", idx, upd)
    return True, "ok", len(rows)

def sezione_import(A, lingua):
    st.subheader("📥 " + t6("import_title", lingua))
    st.caption(t6("import_hint", lingua))
    auth = _auth_presenze(A)   # v07.05
    c1, c2 = st.columns([3, 1])
    anno_sel = c1.number_input(t6("paghe_anno", lingua), min_value=2024, max_value=2035, value=datetime.now().year, key="f6_imp_anno")
    nomi = MESI.get(lingua, MESI["fr"])
    mese_sel = c2.selectbox(t6("paghe_mese", lingua), list(range(1,13)), format_func=lambda m: nomi[m-1], index=datetime.now().month-1, key="f6_imp_mese")
    up = st.file_uploader(t6("import_up_label", lingua), type=["xls","xlsx"])
    if up is not None and st.button("📤 " + t6("import_up_btn", lingua), use_container_width=True):
        url_up = A.cfg_get("url_upload_presenze", "")
        token = A.cfg_get("url_upload_token", "")
        nome_file = f"001_{int(anno_sel)}_{int(mese_sel)}_MON.XLS"
        try:
            import base64
            r = requests.post(url_up, data={"token": token, "filename": nome_file,
                              "file_b64": base64.b64encode(up.getvalue()).decode()}, timeout=120)
            if r.status_code == 200:
                st.success("✅ " + nome_file)
            else:
                st.error(f"{t6('import_up_err', lingua)} — HTTP {r.status_code}")
        except Exception as e:
            st.error(f"{t6('import_up_err', lingua)} — {e}")
    if st.button("📥 " + t6("import_cloud_btn", lingua), use_container_width=True):
        url_cart = A.cfg_get("url_cartella_presenze", "").rstrip("/")
        nome_file = f"001_{int(anno_sel)}_{int(mese_sel)}_MON.XLS"
        try:
            r = requests.get(f"{url_cart}/{nome_file}", auth=auth, timeout=120)   # v07.05 auth
            if r.status_code == 200 and r.content:
                try:
                    parsed = parse_matrix(_xls_matrix(r.content))
                except Exception:
                    parsed = None
                if parsed and parsed["blocchi"]:
                    st.session_state.f6_parsed = parsed
                    st.session_state.pop("f6_esito_import", None)
                    st.rerun()
                else:
                    st.error(t6("parsed_none", lingua))
            else:
                st.error(f"{t6('import_up_err', lingua)} — HTTP {r.status_code}")
        except Exception as e:
            st.error(f"{t6('import_up_err', lingua)} — {e}")
    testo = st.text_area(t6("import_da_testo", lingua), height=200, key="f6_ta")
    if st.button("🔎 " + t6("import_parse_btn", lingua), type="primary"):
        if not testo.strip():
            st.warning(t6("import_empty", lingua))
        else:
            parsed = parse_list_of_logs(testo)
            if not parsed["anno"] or not parsed["blocchi"]:
                st.error(t6("parsed_none", lingua))
            else:
                st.session_state.f6_parsed = parsed
                st.session_state.pop("f6_esito_import", None)
                st.rerun()
    parsed = st.session_state.get("f6_parsed")
    if parsed:
        st.success(f"{t6('parsed_ok', lingua)} — {t6('import_period', lingua)}: "
                   f"{parsed['g1']:02d}/{parsed['mese']:02d}/{parsed['anno']} → "
                   f"{parsed['g2']:02d}/{parsed['mese']:02d}/{parsed['anno']} — "
                   f"{len(parsed['blocchi'])} {t6('import_workers', lingua)}")
        if st.button("💾 " + t6("import_write_btn", lingua), type="primary"):
            with st.spinner("..."):
                esito = scrivi_presenze(A, parsed)
            st.session_state.f6_esito_import = esito
            st.session_state.pop("f6_parsed", None)
            st.rerun()
    esito = st.session_state.get("f6_esito_import")
    if esito:
        if esito.get("ok"):
            st.success(f"✅ {esito['scritte']} {t6('import_written', lingua)} "
                       f"(OK: {esito['okn']} — DA_RIVEDERE: {esito['dar']} — ASSENTE: {esito['abs']}) — "
                       f"{esito['dup']} {t6('import_dup', lingua)}")
            if esito["dar"] > 0: st.info(t6("import_go_anomalies", lingua))
            if esito["unmapped"]: st.warning(t6("import_unmapped", lingua) + ", ".join(esito["unmapped"]))
        else:
            st.error("❌ " + str(esito.get("msg")))

def _xls_matrix(data):
    import xlrd
    wb = xlrd.open_workbook(file_contents=data)
    sh = None
    for s in wb.sheets():
        if "log" in s.name.lower(): sh = s; break
    if sh is None: sh = wb.sheet_by_index(0)
    rows = []
    for ri in range(sh.nrows):
        cells = []
        for ci in range(sh.ncols):
            v = sh.cell_value(ri, ci)
            if isinstance(v, float) and 0 < v < 1:
                hh, mm, ss = xlrd.xld_as_time(v)
                cells.append(f"{hh:02d}:{mm:02d}")
            elif isinstance(v, float) and v == int(v):
                cells.append(str(int(v)))
            else:
                cells.append("" if v is None else str(v))
        rows.append(cells)
    return rows

def sezione_anomalie(A, lingua):
    st.subheader("🔍 " + t6("anom_title", lingua))
    _, pres = A.leggi_foglio("PRESENZE", force=True)
    righe = [(i, p) for i, p in enumerate(pres) if A.s_str(p.get("stato")).upper() in ("DA_RIVEDERE","ASSENTE")]
    if not righe:
        st.success(t6("anom_none", lingua)); return
    st.caption(t6("anom_hint", lingua))
    opts = ["OK","ASSENTE","RIPOSO","MALATTIA","ANNULLATA"]
    for i, p in righe[:60]:
        cod = A.s_str(p.get("codice_lavoratore"))
        stato = A.s_str(p.get("stato")).upper()
        with st.expander(f"{stato} — {cod} — {A.s_str(p.get('data'))} — ▶ {A.s_str(p.get('ora_ingresso')) or '…'}"):
            c1, c2, c3 = st.columns(3)
            c1.text_input(t6("anom_uscita", lingua), value=A.s_str(p.get("ora_uscita")), key=f"f6u_{i}")
            c2.selectbox(t6("anom_stato", lingua), opts, index=opts.index(stato) if stato in opts else 1, key=f"f6s_{i}")
            c3.text_input(t6("anom_note", lingua), value=A.s_str(p.get("note")), key=f"f6n_{i}")
    if st.button("💾 " + t6("anom_save_all", lingua), type="primary", use_container_width=True):
        fatte = 0
        for i, p in righe[:60]:
            orig_stato = A.s_str(p.get("stato")).upper()
            orig_usc = A.s_str(p.get("ora_uscita"))
            orig_nota = A.s_str(p.get("note"))
            n_stato = st.session_state.get(f"f6s_{i}", orig_stato)
            n_usc = (st.session_state.get(f"f6u_{i}") or "").strip()
            n_nota = st.session_state.get(f"f6n_{i}", orig_nota)
            if (n_stato==orig_stato) and (n_usc==orig_usc) and (n_nota==orig_nota): continue
            upd = {"stato": n_stato, "note": n_nota}
            ok_row = True
            if n_stato == "OK":
                ingr = A.s_str(p.get("ora_ingresso"))
                if ingr and n_usc and to_min(ingr) is not None and to_min(n_usc) is not None:
                    diff = to_min(n_usc) - to_min(ingr)
                    if diff < 0: diff += 24*60
                    upd["ora_uscita"] = n_usc
                    upd["ore_lavorate"] = f"{round(diff/60.0,2):.2f}"
                else:
                    ok_row = False
                    st.error(t6("anom_need_out", lingua))
            elif n_stato == "ASSENTE":
                upd["ora_uscita"] = ""
                upd["ore_lavorate"] = "0.00"
            if ok_row:
                ok, _ = A.salva_update("PRESENZE", i, upd)
                if ok: fatte += 1
        st.success(f"✅ {fatte} {t6('anom_fixed_n', lingua)}")
        st.rerun()
    if len(righe) > 60: st.caption(f"… {len(righe)-60}+")

def render_anteprima(lingua, ant):
    if ant.get("festivi_default"):
        st.warning("⚠️ " + "Jours fériés par défaut — complétez CONFIG.")
    if ant["dar_count"] > 0:
        st.warning(f"⚠️ {ant['dar_count']} {t6('dar_warn', lingua)}")
    for av in ant["avvisi"]: st.caption("• " + av)
    tab = []
    for det in ant["dets"]:
        tab.append({t6("col_codice", lingua): det["code"], t6("col_nome", lingua): det["nome"],
            t6("col_tipo", lingua): det["tipo_paga"], t6("col_base", lingua): f"{det['base']:,.0f}",
            t6("col_giorni", lingua): det["n_giorni"], t6("col_ore", lingua): f"{det['ore_tot']:.1f}",
            t6("col_stra", lingua): f"{det['ore_stra']:.1f}", t6("col_rit", lingua): det["mezzore"],
            t6("col_abs", lingua): det["n_assenze"], t6("col_lordo", lingua): f"{det['lordo']:,.0f}",
            t6("col_acc", lingua): f"{det['ded']:,.0f}"})
    st.dataframe(tab, use_container_width=True, hide_index=True)
    with st.expander("🏆 " + t6("premi_title", lingua)):
        for det in ant["dets"]:
            st.number_input(f"{det['code']} — {det['nome']}", min_value=0, step=500, key=f"f6_premio_{det['code']}")
    tot_lordo = sum(d["lordo"] for d in ant["dets"])
    tot_ded = sum(d["ded"] for d in ant["dets"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t6("tot_lordo", lingua), f"{tot_lordo:,.0f} FCFA")
    c2.metric(t6("tot_acc", lingua), f"{tot_ded:,.0f} FCFA")
    c3.metric(t6("tot_netto", lingua), f"{tot_lordo - tot_ded:,.0f} FCFA")
    st.caption(t6("netto_hint", lingua))

def sezione_paghe(A, lingua):
    st.subheader("💰 " + t6("paghe_title", lingua))
    c1, c2, c3, c4 = st.columns([1,1.4,1.5,1.4])
    anno = c1.number_input(t6("paghe_anno", lingua), min_value=2024, max_value=2035, value=datetime.now().year, key="f6_anno")
    nomi = MESI.get(lingua, MESI["fr"])
    mese = c2.selectbox(t6("paghe_mese", lingua), list(range(1,13)), format_func=lambda m: nomi[m-1], index=datetime.now().month-1, key="f6_mese")
    q = c3.radio(t6("paghe_quindicina", lingua), [t6("paghe_q1", lingua), t6("paghe_q2", lingua)], key="f6_q")
    quindicina = 1 if q == t6("paghe_q1", lingua) else 2
    if c4.button("🧮 " + t6("paghe_calc_btn", lingua), type="primary", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith("f6_premio_"): st.session_state.pop(k, None)
        with st.spinner("..."):
            st.session_state.f6_ant = calcola_anteprima(A, lingua, int(anno), int(mese), quindicina)
        st.rerun()
    ant = st.session_state.get("f6_ant")
    if ant:
        st.markdown(f"**{t6('paghe_periodo', lingua)}: {ant['pda']} → {ant['paa']}**")
        if not ant["dets"]:
            st.info(t6("paghe_nulla", lingua)); return
        render_anteprima(lingua, ant)
        if st.button("✅ " + t6("paghe_confirm_btn", lingua), type="primary"):
            ok, msg, n = conferma_paghe(A, ant)
            if ok:
                st.session_state.pop("f6_ant", None)
                st.success(t6("paghe_done", lingua) + str(n))
            else:
                st.error(msg)

def sezione_acconti(A, lingua):
    st.subheader("💸 " + t6("acc_title", lingua))
    b = A.leggi_admin()
    dips = b.get("DIPENDENTI", [])
    opzioni, codmap = [], {}
    for d in dips:
        cod = A.s_str(d.get("codice"))
        if cod:
            lab = f"{cod} — {A.s_str(d.get('cognome'))} {A.s_str(d.get('nome'))}"
            opzioni.append(lab); codmap[lab] = cod
    st.markdown("**➕ " + t6("acc_new", lingua) + "**")
    with st.form("f6_new_acc"):
        c1, c2 = st.columns(2)
        lab = c1.selectbox(t6("acc_codice", lingua), opzioni) if opzioni else None
        tipo = c2.selectbox(t6("acc_tipo", lingua), ["generico","tabasky","scuola","karem"], format_func=lambda x: t6("acc_"+x, lingua))
        c3, c4 = st.columns(2)
        importo = c3.number_input(t6("acc_importo", lingua), min_value=0, step=1000, key="f6acc_imp")
        mod = c4.selectbox(t6("acc_modalita", lingua), ["unica","rate"], format_func=lambda x: t6("acc_"+x, lingua))
        c5, c6 = st.columns(2)
        dr = c5.text_input(t6("acc_data_rich", lingua), value=datetime.now().strftime("%d/%m/%Y"), key="f6acc_dr")
        de = c6.text_input(t6("acc_data_ero", lingua), value=datetime.now().strftime("%d/%m/%Y"), key="f6acc_de")
        nr = 1
        if mod == "rate":
            nr = st.number_input(t6("acc_num_rate", lingua), min_value=1, max_value=24, value=3, key="f6acc_nr")
        if st.form_submit_button("➕ " + t6("acc_crea_btn", lingua), type="primary"):
            if not lab or importo <= 0:
                st.error(t6("acc_err", lingua))
            else:
                rata = round(importo / max(1, nr)) if mod == "rate" else 0
                row = {"id_acconto": f"ACC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10,99)}",
                    "codice_lavoratore": codmap[lab], "tipo_acconto": tipo, "importo": str(int(importo)),
                    "data_richiesta": dr, "data_erogazione": de, "modalita_rimborso": mod,
                    "numero_rate": str(int(nr)) if mod=="rate" else "", "importo_rata": str(int(rata)) if mod=="rate" else "",
                    "rate_pagate": "0", "stato": "aperto", "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")}
                ok, msg = A.salva_append("ACCONTI", row)
                if ok:
                    st.success(t6("acc_created", lingua) + " — " + t6("acc_dedotto", lingua))
                    st.rerun()
                else:
                    st.error(msg)
    st.markdown("---")
    st.markdown("**" + t6("acc_open_title", lingua) + "**")
    _, accs = A.leggi_foglio("ACCONTI", force=True)
    aperti = [a for a in accs if A.s_str(a.get("stato")).lower() not in ("chiuso","annullato")]
    if aperti:
        tab = [{t6("col_codice", lingua): A.s_str(a.get("codice_lavoratore")),
            t6("acc_tipo", lingua): A.s_str(a.get("tipo_acconto")),
            t6("acc_importo", lingua): A.s_str(a.get("importo")),
            t6("acc_modalita", lingua): A.s_str(a.get("modalita_rimborso")),
            "Rate": f"{A.s_str(a.get('rate_pagate')) or '0'}/{A.s_str(a.get('numero_rate')) or '-'}",
            "Rata": A.s_str(a.get("importo_rata")), t6("anom_stato", lingua): A.s_str(a.get("stato"))} for a in aperti]
        st.dataframe(tab, use_container_width=True, hide_index=True)
    else:
        st.info(t6("acc_none", lingua))

def pagina_fase6(lingua, app_module):
    A = app_module
    st.title(t6("titolo", lingua))
    st.caption(VERSIONE_PAGHE)
    cfg, festivi = leggi_config(A)
    with st.expander("⚙️ CONFIG"):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Straord. feriale", f"+{cfg['straordinario_1_percent']:.0f}%")
        c2.metric("Straord. dim./férié", f"+{cfg['straordinario_2_percent']:.0f}%")
        c3.metric("Ore normali", f"{cfg['ore_normali_giorno']:.0f}")
        c4.metric("Toll. ritardo", f"{cfg['ritardo_tolleranza_min']:.0f} min")
        c5.metric("Penale assenza", f"{cfg['assenza_penale_percent']:.0f}%")
        st.caption("Riposo: " + ", ".join(sorted(cfg.get('_riposo', {"sabato","domenica"}))) +
                   " — Flottanti: " + (", ".join(sorted(cfg.get('_flottanti', set()))) or "—"))
    tab1, tab2, tab3, tab4 = st.tabs(["📥 Import", "🔍 " + t6("anom_title", lingua), "💰 " + t6("paghe_title", lingua), "💸 " + t6("acc_title", lingua)])
    with tab1: sezione_import(A, lingua)
    with tab2: sezione_anomalie(A, lingua)
    with tab3: sezione_paghe(A, lingua)
    with tab4: sezione_acconti(A, lingua)
