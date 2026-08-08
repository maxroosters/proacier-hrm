# -*- coding: utf-8 -*-
"""
Script standalone per generare le righe CONFIG delle festività senegalesi
(lunari + fisse) per gli anni 2026-2035.

Esegui:  python genera_festivi_lunari.py
Output:  righe pronte da incollare nel foglio Google CONFIG.

⚠️  Le date islamiche (Korité, Tabaski, Tamkharit, Maouloud) sono INDICATIVE.
    Vanno verificate ogni anno con le autorità religiose locali (1-2 giorni
    di differenza possibili per osservazione della luna).
    Sorgente indicativa: https://www.timeanddate.com/holidays/senegal/
"""

# Festività FIXED (stesse date ogni anno)
FESTIVITA_FISSE = [
    ("01-01", "Nouvel An / Capodanno"),
    ("04-04", "Fête de l'Indépendance / Festa dell'Indipendenza"),
    ("05-01", "Fête du Travail / Festa del Lavoro"),
    ("08-15", "Assomption / Assunzione"),
    ("11-01", "Toussaint / Ognissanti"),
    ("12-25", "Noël / Natale"),
]

# Festività LUNARI (date indicative da verificare ogni anno)
# Formato: anno -> [(mese, giorno, nome), ...]
# Le date scorrono di ~10-11 giorni all'indietro (calendario Hijri lunare 354 gg)
FESTIVITA_LUNARI = {
    2026: [
        (3, 20, "Korité (Aïd el-Fitr, indicative)"),
        (5, 27, "Tabaski (Aïd el-Kébir, indicative)"),
        (6, 26, "Tamkharit (indicative)"),
        (8, 25, "Maouloud / Gamou (indicative)"),
    ],
    2027: [
        (3, 10, "Korité (indicative)"),
        (5, 17, "Tabaski (indicative)"),
        (6, 16, "Tamkharit (indicative)"),
        (8, 15, "Maouloud / Gamou (indicative)"),
    ],
    2028: [
        (2, 27, "Korité (indicative)"),
        (5, 5,  "Tabaski (indicative)"),
        (6, 4,  "Tamkharit (indicative)"),
        (8, 3,  "Maouloud / Gamou (indicative)"),
    ],
    2029: [
        (2, 15, "Korité (indicative)"),
        (4, 24, "Tabaski (indicative)"),
        (5, 24, "Tamkharit (indicative)"),
        (7, 24, "Maouloud / Gamou (indicative)"),
    ],
    2030: [
        (2, 5,  "Korité (indicative)"),
        (4, 14, "Tabaski (indicative)"),
        (5, 14, "Tamkharit (indicative)"),
        (7, 13, "Maouloud / Gamou (indicative)"),
    ],
    2031: [
        (1, 25, "Korité (indicative)"),
        (4, 3,  "Tabaski (indicative)"),
        (5, 3,  "Tamkharit (indicative)"),
        (7, 3,  "Maouloud / Gamou (indicative)"),
    ],
    2032: [
        (1, 14, "Korité (indicative)"),
        (3, 23, "Tabaski (indicative)"),
        (4, 22, "Tamkharit (indicative)"),
        (6, 21, "Maouloud / Gamou (indicative)"),
    ],
    2033: [
        (1, 3,  "Korité (indicative)"),
        (3, 12, "Tabaski (indicative)"),
        (4, 11, "Tamkharit (indicative)"),
        (6, 11, "Maouloud / Gamou (indicative)"),
        (12, 23, "Korité (2ème occurrence, indicative)"),
    ],
    2034: [
        (3, 2,  "Tabaski (indicative)"),
        (4, 1,  "Tamkharit (indicative)"),
        (5, 31, "Maouloud / Gamou (indicative)"),
        (12, 12, "Korité (indicative)"),
    ],
    2035: [
        (2, 20, "Tabaski (indicative)"),
        (3, 21, "Tamkharit (indicative)"),
        (5, 21, "Maouloud / Gamou (indicative)"),
        (12, 2, "Korité (indicative)"),
    ],
}


def main():
    print("=" * 70)
    print("RIGHE DA INCOLLARE NEL FOGLIO CONFIG (colonne chiave | valore)")
    print("=" * 70)
    print()

    # Prima: festività fisse per tutti gli anni
    anni = sorted(FESTIVITA_LUNARI.keys())
    for anno in anni:
        print(f"# === ANNO {anno} ===")
        # Festività fisse dell'anno
        for mm_gg, nome in FESTIVITA_FISSE:
            print(f"festivo_{anno}-{mm_gg}\t{nome}")
        # Festività lunari dell'anno
        for m, g, nome in FESTIVITA_LUNARI[anno]:
            print(f"festivo_{anno}-{m:02d}-{g:02d}\t{nome}")
        print()

    print("=" * 70)
    print("⚠️  RICORDATI DI AGGIUNGERE ANCHE QUESTA RIGA (una sola volta):")
    print("promemoria_festivita_giorni_prima\t10")
    print("=" * 70)


if __name__ == "__main__":
    main()