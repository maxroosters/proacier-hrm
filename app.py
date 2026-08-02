# Sostituisci SOLO queste due funzioni nel tuo codice attuale:

# ============================================
# PAGINA CANDIDATURA SPONTANEA (MODIFICATA)
# ============================================
def pagina_candidatura_spontanea(lingua):
    st.title(get_testo("titolo_candidatura", lingua))
    st.markdown(get_testo("sottotitolo_candidatura", lingua))
    st.info("️ Ceci n'est PAS un contrat d'embauche, mais une transmission de données pour une éventuelle future embauche.")
    st.markdown("---")
    
    with st.form("form_candidatura", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cognome = st.text_input("Nom *")
            nome = st.text_input("Prénom *")
            telefono = st.text_input("Téléphone *")
            cni = st.text_input("Numéro CNI *")
        with col2:
            email = st.text_input("Email")
            data_nascita = st.date_input("Date de naissance")
            indirizzo = st.text_input("Adresse / Quartier")
            citta = st.text_input("Ville", value="Thiès")
        
        st.markdown("---")
        st.subheader("💼 Expérience Professionnelle")
        lavoro_attuale = st.text_input("Poste actuel ou dernier poste occupé")
        azienda_attuale = st.text_input("Entreprise actuelle ou dernière entreprise")
        anni_esperienza = st.number_input("Années d'expérience", min_value=0, max_value=50, value=0)
        
        st.markdown("---")
        st.subheader("🎓 Formation et Études")
        livello_studio = st.selectbox("Niveau d'études", [
            "Aucun", "Primaire", "Collège", "Lycée", 
            "CAP/BTSA", "BTS", "Licence", "Master", "Doctorat"
        ])
        specializzazione = st.text_input("Spécialité / Filière")
        corsi_certificazioni = st.text_area("Cours, certifications ou formations complémentaires", 
                                           placeholder="Décrivez brièvement les cours ou certifications obtenus...")
        
        st.markdown("---")
        st.subheader("🛠️ Compétences et Motivations")
        skills = st.text_area("Vos compétences techniques", 
                             placeholder="Ex: Soudure, mécanique, électricité, maçonnerie, conduite d'engins...")
        motivazione = st.text_area("Pourquoi souhaitez-vous travailler chez PROACIER?", 
                                  placeholder="Expliquez votre motivation...")
        disponibilita = st.selectbox("Disponibilité", [
            "Immédiate", "1 semaine", "2 semaines", "1 mois", "Autre"
        ])
        
        st.markdown("---")
        conferma = st.checkbox("Je confirme l'exactitude des informations *")
        
        submitted = st.form_submit_button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True)
        
        if submitted:
            if cognome and nome and telefono and cni and conferma:
                dati = {
                    "id": genera_codice(),
                    "cognome": cognome,
                    "nome": nome,
                    "telefono": telefono,
                    "email": email,
                    "cni": cni,
                    "data_nascita": str(data_nascita),
                    "indirizzo": indirizzo,
                    "citta": citta,
                    "lavoro_attuale": lavoro_attuale,
                    "azienda_attuale": azienda_attuale,
                    "anni_esperienza": anni_esperienza,
                    "livello_studio": livello_studio,
                    "specializzazione": specializzazione,
                    "corsi_certificazioni": corsi_certificazioni,
                    "skills": skills,
                    "motivazione": motivazione,
                    "disponibilita": disponibilita,
                    "data_invio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "tipo": "candidatura_spontanea"
                }
                if salva_su_google_sheet(dati, GOOGLE_SCRIPT_URL_CANDIDATURE, "append"):
                    st.success("✅ Candidature envoyée avec succès!")
                    st.info("Nous vous contacterons en cas de besoin.")
                else:
                    st.error("Erreur de connexion")
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*)")

# ============================================
# PAGINA TRASMETTI DATI (COMPLETA CON TUTTI I CAMPI)
# ============================================
def pagina_trasmetti_dati(lingua):
    st.title(get_testo("trasmetti_titolo", lingua))
    st.markdown("---")
    st.warning(get_testo("disclaimer_trasmetti", lingua))
    st.markdown("---")
    
    with st.form("form_trasmetti_completo", clear_on_submit=True):
        # STEP 1: Informazioni Personali
        st.subheader(" Informations Personnelles")
        col1, col2 = st.columns(2)
        with col1:
            cognome = st.text_input("Nom de famille *")
            nome = st.text_input("Prénom *")
            data_nascita = st.date_input("Date de naissance *")
            luogo_nascita = st.text_input("Lieu de naissance *")
            sesso = st.selectbox("Sexe", ["M", "F"])
        with col2:
            cni = st.text_input("Numéro CNI *")
            telefono = st.text_input("Téléphone *")
            email = st.text_input("Email")
            indirizzo = st.text_input("Adresse complète")
            quartiere = st.text_input("Quartier")
            citta = st.text_input("Ville", value="Thiès")
        
        st.markdown("---")
        
        # STEP 2: Stato Civile e Famiglia
        st.subheader("👨‍‍👧‍ Situation Familiale")
        col1, col2 = st.columns(2)
        with col1:
            stato_civile = st.selectbox("État civil", 
                ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf/Veuve", "Union libre"])
            num_figli = st.number_input("Nombre d'enfants", min_value=0, value=0)
        with col2:
            nome_coniuge = st.text_input("Nom du conjoint(e) (si applicable)")
            data_matrimonio = st.date_input("Date de mariage (si applicable)")
        
        # Dettagli figli
        if num_figli > 0:
            st.markdown("---")
            st.info("📝 Informations sur les enfants (pour couverture sociale)")
            figli_dati = []
            for i in range(num_figli):
                col1, col2, col3 = st.columns(3)
                with col1:
                    nome_figlio = st.text_input(f"Nom enfant {i+1}", key=f"figlio_nome_{i}")
                with col2:
                    data_figlio = st.date_input(f"Date naissance enfant {i+1}", key=f"figlio_data_{i}")
                with col3:
                    sesso_figlio = st.selectbox(f"Sexe enfant {i+1}", ["M", "F"], key=f"figlio_sesso_{i}")
                figli_dati.append({
                    "nome": nome_figlio,
                    "data_nascita": str(data_figlio),
                    "sesso": sesso_figlio
                })
        
        st.markdown("---")
        
        # STEP 3: Taglie per Uniformi
        st.subheader("👕 Tailles (pour équipements/uniformes)")
        col1, col2, col3 = st.columns(3)
        with col1:
            taglia_maglia = st.selectbox("Taille t-shirt/chemise", 
                ["XS", "S", "M", "L", "XL", "XXL", "XXXL"])
        with col2:
            taglia_pantaloni = st.selectbox("Taille pantalon", 
                ["28", "30", "32", "34", "36", "38", "40", "42", "44", "46"])
        with col3:
            taglia_scarpe = st.selectbox("Pointure chaussures", 
                ["38", "39", "40", "41", "42", "43", "44", "45", "46"])
        
        st.markdown("---")
        
        # STEP 4: Formazione
        st.subheader("🎓 Formation et Études")
        col1, col2 = st.columns(2)
        with col1:
            livello_studio = st.selectbox("Niveau d'études", [
                "Aucun", "Primaire", "Collège", "Lycée", 
                "CAP/BTSA", "BTS", "Licence", "Master"
            ])
            specializzazione = st.text_input("Spécialité / Filière")
        with col2:
            patente = st.selectbox("Permis de conduire", 
                ["Aucun", "A", "B", "C", "D", "E"])
            data_patente = st.date_input("Date d'obtention permis")
        
        corsi = st.text_area("Cours, certifications ou formations complémentaires",
                            placeholder="Décrivez les formations suivies...")
        
        st.markdown("---")
        
        # STEP 5: Esperienza Lavorativa
        st.subheader("💼 Expérience Professionnelle")
        mansione_precedente = st.text_input("Poste précédent ou actuel")
        azienda_precedente = st.text_input("Entreprise précédente ou actuelle")
        anni_esperienza = st.number_input("Années d'expérience", min_value=0, max_value=50, value=0)
        skills = st.text_area("Compétences techniques",
                             placeholder="Ex: Soudure, mécanique, électricité, maçonnerie...")
        
        st.markdown("---")
        
        # STEP 6: Informazioni Mediche
        st.subheader(" Informations Médicales")
        col1, col2 = st.columns(2)
        with col1:
            gruppo_sanguigno = st.selectbox("Groupe sanguin", ["A", "B", "AB", "O", "Je ne sais pas"])
            rh = st.selectbox("Rhésus", ["+", "-", "Je ne sais pas"])
        with col2:
            allergie = st.text_area("Allergies connues")
            patologie = st.text_area("Pathologies chroniques (si applicable)")
        
        st.markdown("---")
        
        # STEP 7: Contatto Emergenza
        st.subheader("🚨 Contact d'Urgence")
        col1, col2 = st.columns(2)
        with col1:
            emergenza_nome = st.text_input("Nom du contact d'urgence *")
            emergenza_parentela = st.selectbox("Relation", 
                ["Conjoint(e)", "Père", "Mère", "Frère/Soeur", "Autre"])
        with col2:
            emergenza_telefono = st.text_input("Téléphone contact d'urgence *")
            emergenza_indirizzo = st.text_input("Adresse du contact")
        
        st.markdown("---")
        
        # Validazione
        conferma = st.checkbox("Je confirme que toutes les informations fournies sont exactes et complètes *")
        
        submitted = st.form_submit_button(get_testo("btn_envia_trasmetti", lingua), 
                                         type="primary", use_container_width=True)
        
        if submitted:
            if cognome and nome and cni and telefono and emergenza_nome and emergenza_telefono and conferma:
                # Costruisci dati completi
                dati = {
                    "id": genera_codice(),
                    "cognome": cognome,
                    "nome": nome,
                    "data_nascita": str(data_nascita),
                    "luogo_nascita": luogo_nascita,
                    "sesso": sesso,
                    "cni": cni,
                    "telefono": telefono,
                    "email": email,
                    "indirizzo": indirizzo,
                    "quartiere": quartiere,
                    "citta": citta,
                    "stato_civile": stato_civile,
                    "num_figli": num_figli,
                    "nome_coniuge": nome_coniuge,
                    "data_matrimonio": str(data_matrimonio),
                    "figli_dati": str(figli_dati) if num_figli > 0 else "",
                    "taglia_maglia": taglia_maglia,
                    "taglia_pantaloni": taglia_pantaloni,
                    "taglia_scarpe": taglia_scarpe,
                    "livello_studio": livello_studio,
                    "specializzazione": specializzazione,
                    "patente": patente,
                    "data_patente": str(data_patente),
                    "corsi": corsi,
                    "mansione_precedente": mansione_precedente,
                    "azienda_precedente": azienda_precedente,
                    "anni_esperienza": anni_esperienza,
                    "skills": skills,
                    "gruppo_sanguigno": gruppo_sanguigno,
                    "rh": rh,
                    "allergie": allergie,
                    "patologie": patologie,
                    "emergenza_nome": emergenza_nome,
                    "emergenza_parentela": emergenza_parentela,
                    "emergenza_telefono": emergenza_telefono,
                    "emergenza_indirizzo": emergenza_indirizzo,
                    "data_invio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "tipo": "trasmissione_dati_completa"
                }
                
                if salva_su_google_sheet(dati, GOOGLE_SCRIPT_URL_CANDIDATURE, "append"):
                    st.success(get_testo("trasmetti_successo", lingua))
                    st.info(get_testo("trasmetti_contatto", lingua))
                    st.ballo()
                else:
                    st.error("❌ Erreur de connexion. Réessayez.")
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*) et confirmer.")
    
    if st.button(get_testo("indietro", lingua), use_container_width=True):
        st.session_state.pagina = 'login_lavoratore'
        st.rerun()
