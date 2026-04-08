"""Rule-based disease triage engine with 55+ rules from ICAR-IVRI/NDDB guidelines."""

from typing import Any

DISEASE_RULES: dict[str, list[dict[str, Any]]] = {
    "cattle": [
        {
            "disease": "Foot and Mouth Disease (FMD)",
            "symptoms": ["fever", "drooling", "blisters_mouth", "lameness", "reduced_milk", "blisters_feet"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Isolate immediately. Contact veterinarian. Do NOT move animal. Report to district veterinary officer.",
            "source": "ICAR-IVRI FMD Guidelines 2023",
        },
        {
            "disease": "Mastitis",
            "symptoms": ["swollen_udder", "hot_udder", "clots_in_milk", "reduced_milk", "fever", "pain_on_milking"],
            "min_match": 2,
            "risk_level": "high",
            "action": "Stop milking affected quarters. Apply cold compress. Consult vet for antibiotics.",
            "source": "NDDB Mastitis Control Programme",
        },
        {
            "disease": "Brucellosis",
            "symptoms": ["abortion", "retained_placenta", "swollen_joints", "fever", "reduced_milk", "infertility"],
            "min_match": 2,
            "risk_level": "critical",
            "action": "Isolate animal. Test entire herd. Do NOT consume raw milk. Report to authorities.",
            "source": "ICAR-IVRI Brucellosis Eradication Programme",
        },
        {
            "disease": "Hemorrhagic Septicemia (HS)",
            "symptoms": ["high_fever", "swollen_throat", "difficulty_breathing", "drooling", "nasal_discharge", "sudden_death"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Emergency vet call. Administer antibiotics immediately. Vaccinate rest of herd.",
            "source": "ICAR-IVRI HS Control Guidelines",
        },
        {
            "disease": "Black Quarter (BQ)",
            "symptoms": ["high_fever", "swollen_leg", "lameness", "crepitant_swelling", "sudden_death", "loss_of_appetite"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Emergency vet treatment with penicillin. Vaccinate rest of herd immediately.",
            "source": "ICAR-IVRI BQ Vaccination Programme",
        },
        {
            "disease": "Theileriosis (Tropical Theileriosis)",
            "symptoms": ["high_fever", "swollen_lymph_nodes", "anaemia", "jaundice", "reduced_milk", "loss_of_appetite"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Administer buparvaquone injection. Tick control measures. Supportive therapy.",
            "source": "ICAR-IVRI Tick-Borne Disease Guidelines",
        },
        {
            "disease": "Babesiosis (Tick Fever)",
            "symptoms": ["high_fever", "red_urine", "anaemia", "jaundice", "loss_of_appetite", "weakness"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Administer diminazene aceturate. Tick control. IV fluids for dehydration.",
            "source": "ICAR-IVRI Babesiosis Treatment Protocol",
        },
        {
            "disease": "Anaplasmosis",
            "symptoms": ["fever", "anaemia", "jaundice", "weakness", "loss_of_appetite", "constipation"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Oxytetracycline treatment. Blood transfusion if severe. Tick control.",
            "source": "ICAR-IVRI Anaplasmosis Guidelines",
        },
        {
            "disease": "Bloat (Ruminal Tympany)",
            "symptoms": ["distended_abdomen", "difficulty_breathing", "restlessness", "stops_eating", "salivation"],
            "min_match": 2,
            "risk_level": "high",
            "action": "Emergency trocarization if severe. Administer anti-bloat agent. Walk animal gently.",
            "source": "NDDB Dairy Farmer Advisory",
        },
        {
            "disease": "Milk Fever (Hypocalcemia)",
            "symptoms": ["weakness", "unable_to_stand", "cold_ears", "muscle_tremors", "dilated_pupils", "reduced_milk"],
            "min_match": 3,
            "risk_level": "high",
            "action": "IV calcium borogluconate immediately. Keep animal warm. Prevent aspiration.",
            "source": "NDDB Metabolic Disease Advisory",
        },
        {
            "disease": "Ketosis",
            "symptoms": ["loss_of_appetite", "reduced_milk", "rapid_weight_loss", "sweet_breath", "lethargy", "constipation"],
            "min_match": 3,
            "risk_level": "medium",
            "action": "Administer propylene glycol orally. IV dextrose. Increase energy in diet.",
            "source": "NDDB Metabolic Disease Advisory",
        },
        {
            "disease": "Retained Placenta",
            "symptoms": ["retained_placenta", "foul_discharge", "fever", "loss_of_appetite", "reduced_milk"],
            "min_match": 2,
            "risk_level": "high",
            "action": "Do NOT pull manually. Administer oxytocin. Antibiotics to prevent infection.",
            "source": "ICAR-IVRI Reproductive Health Guidelines",
        },
        {
            "disease": "Metritis",
            "symptoms": ["foul_discharge", "fever", "loss_of_appetite", "reduced_milk", "straining"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Intrauterine antibiotics. Systemic antibiotics. Hormonal therapy.",
            "source": "ICAR-IVRI Reproductive Health Guidelines",
        },
        {
            "disease": "Johne's Disease (Paratuberculosis)",
            "symptoms": ["chronic_diarrhea", "weight_loss", "reduced_milk", "bottle_jaw", "normal_appetite"],
            "min_match": 3,
            "risk_level": "high",
            "action": "No cure. Cull positive animals. Test herd. Improve hygiene.",
            "source": "ICAR-IVRI Johne's Disease Control",
        },
        {
            "disease": "Infectious Bovine Rhinotracheitis (IBR)",
            "symptoms": ["nasal_discharge", "fever", "red_eyes", "cough", "reduced_milk", "abortion"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Isolate. Supportive treatment. Vaccinate herd. No specific antiviral.",
            "source": "ICAR-IVRI IBR Guidelines",
        },
        {
            "disease": "Bovine Viral Diarrhea (BVD)",
            "symptoms": ["diarrhea", "fever", "nasal_discharge", "mouth_ulcers", "reduced_milk", "abortion"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Identify and remove persistently infected animals. Vaccinate herd.",
            "source": "ICAR-IVRI BVD Control Programme",
        },
        {
            "disease": "Lumpy Skin Disease (LSD)",
            "symptoms": ["skin_nodules", "fever", "swollen_lymph_nodes", "reduced_milk", "nasal_discharge", "lameness"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Isolate immediately. Notify authorities. Supportive care. Vector control.",
            "source": "DAHD-ICAR LSD Emergency Response 2022",
        },
        {
            "disease": "Anthrax",
            "symptoms": ["sudden_death", "bleeding_from_orifices", "high_fever", "swelling", "difficulty_breathing"],
            "min_match": 2,
            "risk_level": "critical",
            "action": "DO NOT open carcass. Report immediately. Penicillin if alive. Quarantine area.",
            "source": "ICAR-IVRI Anthrax Control Guidelines",
        },
        {
            "disease": "Bovine Tuberculosis",
            "symptoms": ["chronic_cough", "weight_loss", "reduced_milk", "swollen_lymph_nodes", "fever"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Tuberculin test herd. Cull positive animals. Do NOT consume raw milk.",
            "source": "ICAR-IVRI TB Eradication Programme",
        },
        {
            "disease": "Trypanosomiasis (Surra)",
            "symptoms": ["fever", "anaemia", "edema", "weight_loss", "weakness", "abortion"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Administer diminazene or suramin. Vector control (flies). Supportive care.",
            "source": "ICAR-IVRI Surra Control Guidelines",
        },
        {
            "disease": "Acidosis (Grain Overload)",
            "symptoms": ["diarrhea", "loss_of_appetite", "dehydration", "weakness", "bloat", "teeth_grinding"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Rumen lavage in severe cases. Oral antacids. Gradual diet correction.",
            "source": "NDDB Feeding Management Advisory",
        },
    ],
    "goat": [
        {
            "disease": "Peste des Petits Ruminants (PPR)",
            "symptoms": ["fever", "nasal_discharge", "mouth_ulcers", "diarrhea", "cough", "eye_discharge"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Isolate. No specific treatment. Supportive care. Vaccinate rest of flock.",
            "source": "ICAR-IVRI PPR Eradication Programme",
        },
        {
            "disease": "Enterotoxemia",
            "symptoms": ["sudden_death", "convulsions", "bloat", "diarrhea", "loss_of_appetite", "abdominal_pain"],
            "min_match": 2,
            "risk_level": "critical",
            "action": "Antitoxin if caught early. Vaccinate entire flock. Regulate feeding.",
            "source": "ICAR-IVRI Enterotoxemia Guidelines",
        },
        {
            "disease": "Goat Pox",
            "symptoms": ["fever", "skin_nodules", "nasal_discharge", "eye_discharge", "loss_of_appetite"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Isolate. Supportive treatment. Apply antiseptic on lesions. Vaccinate flock.",
            "source": "ICAR-IVRI Goat Pox Control",
        },
        {
            "disease": "Haemonchosis (Barber's Pole Worm)",
            "symptoms": ["anaemia", "bottle_jaw", "weakness", "weight_loss", "diarrhea", "pale_gums"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Deworm with effective anthelmintic. FAMACHA scoring. Rotational grazing.",
            "source": "ICAR-IVRI Parasite Control Guidelines",
        },
        {
            "disease": "Pneumonia",
            "symptoms": ["cough", "nasal_discharge", "fever", "difficulty_breathing", "loss_of_appetite", "lethargy"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Antibiotics. Anti-inflammatory. Improve ventilation. Reduce stress.",
            "source": "ICAR-IVRI Respiratory Disease Advisory",
        },
        {
            "disease": "Caprine Mastitis",
            "symptoms": ["swollen_udder", "hot_udder", "reduced_milk", "clots_in_milk", "fever"],
            "min_match": 2,
            "risk_level": "high",
            "action": "Intramammary antibiotics. Strip affected quarter. Improve milking hygiene.",
            "source": "NDDB Small Ruminant Advisory",
        },
        {
            "disease": "Caprine Brucellosis",
            "symptoms": ["abortion", "retained_placenta", "swollen_joints", "fever", "infertility"],
            "min_match": 2,
            "risk_level": "critical",
            "action": "Test and slaughter positive animals. Do NOT consume raw milk. Report to vet.",
            "source": "ICAR-IVRI Brucellosis Control",
        },
        {
            "disease": "Johne's Disease (Caprine)",
            "symptoms": ["chronic_diarrhea", "weight_loss", "normal_appetite", "rough_coat", "weakness"],
            "min_match": 3,
            "risk_level": "high",
            "action": "No cure. Cull positive animals. Improve hygiene. Test kids from positive does.",
            "source": "ICAR-IVRI Johne's Disease Control",
        },
        {
            "disease": "Contagious Ecthyma (Orf)",
            "symptoms": ["scabs_lips", "scabs_nose", "drooling", "loss_of_appetite", "lameness"],
            "min_match": 2,
            "risk_level": "medium",
            "action": "Apply glycerine-iodine on lesions. Soft feed. Usually self-limiting in 3-4 weeks. Zoonotic — wear gloves.",
            "source": "ICAR-IVRI Orf Advisory",
        },
        {
            "disease": "Contagious Caprine Pleuropneumonia (CCPP)",
            "symptoms": ["cough", "difficulty_breathing", "nasal_discharge", "fever", "loss_of_appetite", "head_extended"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Oxytetracycline or tylosin antibiotics. Isolate. Vaccinate flock.",
            "source": "ICAR-IVRI CCPP Guidelines",
        },
        {
            "disease": "Coccidiosis (Caprine)",
            "symptoms": ["bloody_diarrhea", "weight_loss", "dehydration", "weakness", "straining"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Sulfonamide drugs or amprolium. Improve sanitation. Separate young kids.",
            "source": "ICAR-IVRI Coccidiosis Control",
        },
        {
            "disease": "Foot Rot (Caprine)",
            "symptoms": ["lameness", "foul_smell_feet", "swollen_feet", "reluctance_to_walk"],
            "min_match": 2,
            "risk_level": "medium",
            "action": "Trim hooves. Foot bath with copper sulfate. Antibiotics if severe. Dry housing.",
            "source": "ICAR-IVRI Foot Rot Advisory",
        },
        {
            "disease": "Pregnancy Toxemia (Caprine)",
            "symptoms": ["loss_of_appetite", "lethargy", "teeth_grinding", "sweet_breath", "unable_to_stand", "blindness"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Propylene glycol orally. IV dextrose. May require caesarean if near term.",
            "source": "NDDB Small Ruminant Metabolic Disease Advisory",
        },
        {
            "disease": "Caprine Bloat",
            "symptoms": ["distended_abdomen", "difficulty_breathing", "restlessness", "stops_eating"],
            "min_match": 2,
            "risk_level": "high",
            "action": "Stomach tube to release gas. Anti-foaming agent. Walk animal gently.",
            "source": "NDDB Feeding Advisory",
        },
        {
            "disease": "Tetanus",
            "symptoms": ["muscle_stiffness", "lock_jaw", "erect_ears", "erect_tail", "difficulty_eating", "convulsions"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Tetanus antitoxin. Penicillin. Dark quiet environment. Usually fatal if untreated.",
            "source": "ICAR-IVRI Tetanus Advisory",
        },
    ],
    "sheep": [
        {
            "disease": "Blue Tongue",
            "symptoms": ["fever", "swollen_tongue", "blue_tongue", "drooling", "lameness", "nasal_discharge"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Supportive care. Anti-inflammatory drugs. Soft feed. Vector control. Vaccinate.",
            "source": "ICAR-IVRI Blue Tongue Control Programme",
        },
        {
            "disease": "Sheep Pox",
            "symptoms": ["fever", "skin_nodules", "nasal_discharge", "eye_discharge", "loss_of_appetite", "swollen_lymph_nodes"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "Isolate. Supportive care. Antiseptic on lesions. Vaccinate flock. Report to authorities.",
            "source": "ICAR-IVRI Sheep Pox Guidelines",
        },
        {
            "disease": "Enterotoxemia (Ovine)",
            "symptoms": ["sudden_death", "convulsions", "diarrhea", "bloat", "abdominal_pain"],
            "min_match": 2,
            "risk_level": "critical",
            "action": "Antitoxin urgently. Vaccinate flock. Regulate concentrate feeding.",
            "source": "ICAR-IVRI Clostridial Disease Guidelines",
        },
        {
            "disease": "Haemonchosis (Ovine)",
            "symptoms": ["anaemia", "bottle_jaw", "weakness", "weight_loss", "pale_gums", "diarrhea"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Deworm. FAMACHA scoring. Rotational grazing. Targeted selective treatment.",
            "source": "ICAR-IVRI Parasite Control Guidelines",
        },
        {
            "disease": "Foot Rot (Ovine)",
            "symptoms": ["lameness", "foul_smell_feet", "swollen_feet", "reluctance_to_walk", "grazing_on_knees"],
            "min_match": 2,
            "risk_level": "medium",
            "action": "Hoof trimming. Foot bath with zinc sulfate. Isolate affected. Keep dry.",
            "source": "ICAR-IVRI Foot Rot Advisory",
        },
        {
            "disease": "Ovine Pneumonia",
            "symptoms": ["cough", "nasal_discharge", "fever", "difficulty_breathing", "loss_of_appetite"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Antibiotics (oxytetracycline). Anti-inflammatory. Improve housing ventilation.",
            "source": "ICAR-IVRI Respiratory Disease Advisory",
        },
        {
            "disease": "Pregnancy Toxemia (Ovine)",
            "symptoms": ["loss_of_appetite", "lethargy", "teeth_grinding", "sweet_breath", "unable_to_stand", "blindness"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Oral propylene glycol. IV glucose. Improve nutrition in late pregnancy.",
            "source": "NDDB Small Ruminant Advisory",
        },
        {
            "disease": "Braxy",
            "symptoms": ["sudden_death", "high_fever", "abdominal_pain", "blood_stained_fluid", "loss_of_appetite"],
            "min_match": 2,
            "risk_level": "critical",
            "action": "Usually fatal. Vaccinate flock. Avoid frosted pastures. Clostridial vaccine.",
            "source": "ICAR-IVRI Clostridial Disease Guidelines",
        },
        {
            "disease": "Louping Ill",
            "symptoms": ["fever", "tremors", "incoordination", "paralysis", "convulsions"],
            "min_match": 3,
            "risk_level": "high",
            "action": "No specific treatment. Supportive care. Tick control. Vaccinate in endemic areas.",
            "source": "ICAR-IVRI Tick-Borne Disease Guidelines",
        },
        {
            "disease": "Scrapie",
            "symptoms": ["itching", "wool_loss", "incoordination", "weight_loss", "behavioral_changes", "tremors"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "No treatment or cure. Cull affected animals. Genetic selection for resistance.",
            "source": "ICAR-IVRI Prion Disease Advisory",
        },
    ],
    "poultry": [
        {
            "disease": "Newcastle Disease (Ranikhet)",
            "symptoms": ["respiratory_distress", "greenish_diarrhea", "twisted_neck", "paralysis", "drop_in_egg_production", "sudden_death"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "No treatment. Cull affected birds. Vaccinate rest. Disinfect premises. Report to authorities.",
            "source": "ICAR-IVRI Newcastle Disease Control",
        },
        {
            "disease": "Marek's Disease",
            "symptoms": ["paralysis", "weight_loss", "grey_iris", "leg_weakness", "drooping_wings"],
            "min_match": 3,
            "risk_level": "high",
            "action": "No treatment. Vaccinate day-old chicks. Cull affected birds. Biosecurity.",
            "source": "ICAR-IVRI Marek's Disease Advisory",
        },
        {
            "disease": "Avian Influenza (Bird Flu)",
            "symptoms": ["sudden_death", "respiratory_distress", "swollen_head", "cyanosis_comb", "drop_in_egg_production", "diarrhea"],
            "min_match": 3,
            "risk_level": "critical",
            "action": "REPORT IMMEDIATELY to authorities. Cull all birds. Quarantine. Zoonotic risk.",
            "source": "DAHD-ICAR Avian Influenza Emergency Response",
        },
        {
            "disease": "Infectious Bronchitis",
            "symptoms": ["cough", "sneezing", "nasal_discharge", "drop_in_egg_production", "watery_eyes", "wet_droppings"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Supportive care. Antibiotics for secondary infection. Vaccinate. Improve ventilation.",
            "source": "ICAR-IVRI IB Control Guidelines",
        },
        {
            "disease": "Coccidiosis (Poultry)",
            "symptoms": ["bloody_droppings", "weight_loss", "ruffled_feathers", "lethargy", "dehydration"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Amprolium in water. Sulfonamides. Improve litter management. Coccidiostat in feed.",
            "source": "ICAR-IVRI Coccidiosis Control",
        },
        {
            "disease": "Fowl Pox",
            "symptoms": ["wart_like_lesions", "scabs_on_comb", "drop_in_egg_production", "difficulty_breathing", "lesions_mouth"],
            "min_match": 2,
            "risk_level": "medium",
            "action": "Apply iodine on lesions. Antibiotics for secondary infection. Vaccinate flock.",
            "source": "ICAR-IVRI Fowl Pox Advisory",
        },
        {
            "disease": "Infectious Bursal Disease (Gumboro / IBD)",
            "symptoms": ["ruffled_feathers", "watery_diarrhea", "trembling", "loss_of_appetite", "dehydration", "sudden_death"],
            "min_match": 3,
            "risk_level": "high",
            "action": "No specific treatment. Supportive care. Electrolytes. Vaccinate. Biosecurity.",
            "source": "ICAR-IVRI IBD Control",
        },
        {
            "disease": "Fowl Cholera (Pasteurellosis)",
            "symptoms": ["sudden_death", "swollen_wattles", "greenish_diarrhea", "difficulty_breathing", "loss_of_appetite"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Sulfonamides or tetracycline. Improve sanitation. Vaccinate. Rodent control.",
            "source": "ICAR-IVRI Fowl Cholera Guidelines",
        },
        {
            "disease": "Mycoplasma Gallisepticum (CRD)",
            "symptoms": ["cough", "nasal_discharge", "sneezing", "swollen_sinuses", "drop_in_egg_production", "foamy_eyes"],
            "min_match": 3,
            "risk_level": "medium",
            "action": "Tylosin or enrofloxacin antibiotics. Improve ventilation. Reduce stress.",
            "source": "ICAR-IVRI Mycoplasma Advisory",
        },
        {
            "disease": "E. coli Infection (Colibacillosis)",
            "symptoms": ["diarrhea", "ruffled_feathers", "lethargy", "swollen_joints", "respiratory_distress", "sudden_death"],
            "min_match": 3,
            "risk_level": "high",
            "action": "Antibiotic sensitivity test. Enrofloxacin or gentamicin. Improve water hygiene.",
            "source": "ICAR-IVRI E. coli Control Advisory",
        },
    ],
}


def evaluate_symptoms(species: str, symptoms: list[str]) -> dict:
    """Match reported symptoms against rules for the given species.

    Returns:
        dict with keys: matches (top 3), risk_level, risk_score, recommended_action
    """
    species_lower = species.lower()
    rules = DISEASE_RULES.get(species_lower, [])

    if not rules:
        return {
            "matches": [],
            "risk_level": "unknown",
            "risk_score": 0.0,
            "recommended_action": f"No rules available for species '{species}'. Consult a veterinarian.",
        }

    symptom_set = {s.lower().strip() for s in symptoms}
    scored: list[dict] = []

    for rule in rules:
        rule_symptoms = {s.lower() for s in rule["symptoms"]}
        matched = symptom_set & rule_symptoms
        match_count = len(matched)

        if match_count >= rule["min_match"]:
            score = match_count / len(rule["symptoms"])
            scored.append(
                {
                    "disease": rule["disease"],
                    "match_count": match_count,
                    "total_symptoms": len(rule["symptoms"]),
                    "match_score": round(score, 3),
                    "matched_symptoms": sorted(matched),
                    "risk_level": rule["risk_level"],
                    "action": rule["action"],
                    "source": rule["source"],
                }
            )

    # Sort by match_score descending, then by risk severity
    risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    scored.sort(key=lambda x: (-x["match_score"], risk_order.get(x["risk_level"], 4)))

    top_matches = scored[:3]

    if top_matches:
        overall_risk = top_matches[0]["risk_level"]
        risk_score_map = {"critical": 0.9, "high": 0.7, "medium": 0.4, "low": 0.2}
        base_risk = risk_score_map.get(overall_risk, 0.1)
        # Adjust score based on how many symptoms matched the top disease
        risk_score = min(1.0, base_risk + (top_matches[0]["match_score"] * 0.1))
        recommended_action = top_matches[0]["action"]
    else:
        overall_risk = "low"
        risk_score = 0.1
        recommended_action = "No matching disease pattern found. Monitor animal and consult vet if symptoms persist."

    return {
        "matches": top_matches,
        "risk_level": overall_risk,
        "risk_score": round(risk_score, 2),
        "recommended_action": recommended_action,
    }
