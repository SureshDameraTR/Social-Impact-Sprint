-- PashuRaksha ERP — Comprehensive Seed Data
-- Run: docker exec -i pashu-erp-db-1 psql -U pashu -d pashuraksha < seed-data.sql

-- Clear existing data (keep users)
DELETE FROM insurance_claims;
DELETE FROM insurance_policies;
DELETE FROM medicine_administrations;
DELETE FROM milk_collection_records;
DELETE FROM yield_logs;
DELETE FROM health_events;
DELETE FROM vaccinations;
DELETE FROM vet_consultations;
DELETE FROM community_alerts;
DELETE FROM transactions;
DELETE FROM sell_records;
DELETE FROM weather_alerts;
DELETE FROM animals;
DELETE FROM milk_collection_centers;
DELETE FROM govt_schemes;
DELETE FROM advisory_tips;
DELETE FROM feed_ingredients;
DELETE FROM traditional_remedies;
DELETE FROM medicines;
DELETE FROM shg_groups;

-- ============== ANIMALS (18 across 9 farmers) ==============
-- Farmer 1: Lakshmi Devi (+919876543213)
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00100001', 'Lakshmi', 'cattle'::species, 'Hallikar', 'indigenous'::breed_type, 'female'::animal_sex, '2020-03-15', 3, 3.5, true, now()-interval '80 days', now() FROM users WHERE phone='+919876543213';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00100002', 'Ganga', 'cattle'::species, 'HF Cross', 'crossbreed'::breed_type, 'female'::animal_sex, '2019-06-20', 4, 4.0, true, now()-interval '80 days', now() FROM users WHERE phone='+919876543213';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00100003', 'Shyama', 'goat'::species, 'Osmanabadi', 'indigenous'::breed_type, 'female'::animal_sex, '2022-04-12', 2, 3.2, false, now()-interval '80 days', now() FROM users WHERE phone='+919876543213';

-- Farmer 2: Raju Gowda (+919876543214)
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00200001', 'Nandi', 'cattle'::species, 'Amrit Mahal', 'indigenous'::breed_type, 'male'::animal_sex, '2021-01-10', NULL, 3.0, false, now()-interval '55 days', now() FROM users WHERE phone='+919876543214';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00200002', 'Parvathi', 'cattle'::species, 'Jersey Cross', 'crossbreed'::breed_type, 'female'::animal_sex, '2018-09-05', 5, 3.8, true, now()-interval '55 days', now() FROM users WHERE phone='+919876543214';

-- Farmer 3: Savitha B (+919876543215)
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00300001', 'Champa', 'cattle'::species, 'Sahiwal', 'indigenous'::breed_type, 'female'::animal_sex, '2019-02-14', 4, 4.2, true, now()-interval '40 days', now() FROM users WHERE phone='+919876543215';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00300002', 'Meena', 'sheep'::species, 'Bannur', 'indigenous'::breed_type, 'female'::animal_sex, '2021-11-20', 1, 3.0, false, now()-interval '40 days', now() FROM users WHERE phone='+919876543215';

-- Farmer 4: Manjunath H (+919876543216)
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00400001', 'Raja', 'cattle'::species, 'Khillari', 'indigenous'::breed_type, 'male'::animal_sex, '2020-07-08', NULL, 3.5, false, now()-interval '25 days', now() FROM users WHERE phone='+919876543216';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00400002', 'Tulsi', 'cattle'::species, 'Gir', 'indigenous'::breed_type, 'female'::animal_sex, '2020-11-15', 3, 3.8, true, now()-interval '25 days', now() FROM users WHERE phone='+919876543216';

-- Farmer 5-9: one animal each
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00500001', 'Kamala', 'cattle'::species, 'Red Sindhi', 'indigenous'::breed_type, 'female'::animal_sex, '2021-05-22', 2, 3.4, false, now()-interval '20 days', now() FROM users WHERE phone='+919876543217';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00600001', 'Durga', 'cattle'::species, 'Tharparkar', 'indigenous'::breed_type, 'female'::animal_sex, '2019-08-10', 5, 4.0, true, now()-interval '15 days', now() FROM users WHERE phone='+919876543218';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00700001', 'Bhagya', 'cattle'::species, 'Deoni', 'indigenous'::breed_type, 'female'::animal_sex, '2021-04-18', 2, 3.3, false, now()-interval '10 days', now() FROM users WHERE phone='+919876543219';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00800001', 'Priya', 'cattle'::species, 'Kangayam', 'indigenous'::breed_type, 'female'::animal_sex, '2020-10-30', 3, 3.7, true, now()-interval '8 days', now() FROM users WHERE phone='+919876543220';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00900001', 'Gomathi', 'cattle'::species, 'Ongole', 'indigenous'::breed_type, 'female'::animal_sex, '2019-12-01', 4, 4.1, true, now()-interval '3 days', now() FROM users WHERE phone='+919876543221';
INSERT INTO animals (id, user_id, pashu_aadhaar_id, name, species, breed, breed_type, sex, date_of_birth, lactation_number, body_condition_score, is_insured, created_at, updated_at)
SELECT gen_random_uuid(), id, 'KA00900002', 'Kali', 'poultry'::species, 'Kadaknath', 'indigenous'::breed_type, 'female'::animal_sex, '2023-07-20', NULL, NULL, false, now()-interval '3 days', now() FROM users WHERE phone='+919876543221';

-- ============== MILK COLLECTION CENTER ==============
INSERT INTO milk_collection_centers (id, name, code, district, village_code, manager_user_id, is_active, created_at, updated_at)
SELECT gen_random_uuid(), 'Tumkur Central DCS', 'TUM-DCS-001', 'Tumkur', 'TUMK-001', id, true, now()-interval '90 days', now()
FROM users WHERE phone='+919876543212';

-- ============== YIELD LOGS (30 days x 2 sessions x 2 cows) ==============
INSERT INTO yield_logs (id, animal_id, user_id, quantity_liters, session, recorded_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, 4.5 + random()*2, 'morning'::milk_session, now()-interval '1 day' * d, now()
FROM animals a, generate_series(0,29) d WHERE a.pashu_aadhaar_id = 'KA00100001';

INSERT INTO yield_logs (id, animal_id, user_id, quantity_liters, session, recorded_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, 3.8 + random()*1.5, 'evening'::milk_session, now()-interval '1 day' * d + interval '10 hours', now()
FROM animals a, generate_series(0,29) d WHERE a.pashu_aadhaar_id = 'KA00100001';

INSERT INTO yield_logs (id, animal_id, user_id, quantity_liters, session, recorded_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, 6.0 + random()*3, 'morning'::milk_session, now()-interval '1 day' * d, now()
FROM animals a, generate_series(0,29) d WHERE a.pashu_aadhaar_id = 'KA00100002';

INSERT INTO yield_logs (id, animal_id, user_id, quantity_liters, session, recorded_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, 5.2 + random()*2, 'evening'::milk_session, now()-interval '1 day' * d + interval '10 hours', now()
FROM animals a, generate_series(0,29) d WHERE a.pashu_aadhaar_id = 'KA00100002';

-- ============== MILK COLLECTION RECORDS ==============
INSERT INTO milk_collection_records (id, center_id, farmer_user_id, quantity_liters, fat_pct, snf_pct, rate_per_liter, total_amount, shift, collected_at, updated_at)
SELECT gen_random_uuid(), c.id, u.id, 8.0+random()*4, 3.5+random()*2, 7.5+random()*1.5, 38+random()*8, (8+random()*4)*(38+random()*8), 'morning'::milk_session, now()-interval '1 day' * d, now()
FROM milk_collection_centers c, users u, generate_series(0,29) d WHERE u.phone='+919876543213' AND c.code='TUM-DCS-001';

INSERT INTO milk_collection_records (id, center_id, farmer_user_id, quantity_liters, fat_pct, snf_pct, rate_per_liter, total_amount, shift, collected_at, updated_at)
SELECT gen_random_uuid(), c.id, u.id, 6.0+random()*3, 4.0+random()*1.5, 8.0+random()*1, 40+random()*6, (6+random()*3)*(40+random()*6), 'morning'::milk_session, now()-interval '1 day' * d, now()
FROM milk_collection_centers c, users u, generate_series(0,14) d WHERE u.phone='+919876543214' AND c.code='TUM-DCS-001';

INSERT INTO milk_collection_records (id, center_id, farmer_user_id, quantity_liters, fat_pct, snf_pct, rate_per_liter, total_amount, shift, collected_at, updated_at)
SELECT gen_random_uuid(), c.id, u.id, 5.5+random()*2, 3.8+random()*1.8, 7.8+random()*1.2, 39+random()*7, (5.5+random()*2)*(39+random()*7), 'evening'::milk_session, now()-interval '1 day' * d + interval '10 hours', now()
FROM milk_collection_centers c, users u, generate_series(0,20) d WHERE u.phone='+919876543215' AND c.code='TUM-DCS-001';

INSERT INTO milk_collection_records (id, center_id, farmer_user_id, quantity_liters, fat_pct, snf_pct, rate_per_liter, total_amount, shift, collected_at, updated_at)
SELECT gen_random_uuid(), c.id, u.id, 7.0+random()*3, 4.2+random()*1, 8.2+random()*0.8, 42+random()*5, (7+random()*3)*(42+random()*5), 'morning'::milk_session, now()-interval '1 day' * d, now()
FROM milk_collection_centers c, users u, generate_series(0,10) d WHERE u.phone='+919876543219' AND c.code='TUM-DCS-001';

-- ============== HEALTH EVENTS ==============
INSERT INTO health_events (id, animal_id, event_type, description, symptoms, ai_risk_score, recommended_action, probable_diseases, recorded_by, event_date, updated_at)
SELECT gen_random_uuid(), a.id, 'symptom'::health_event_type, 'Reduced milk yield and slight fever', '["reduced_appetite", "fever", "low_milk_yield"]'::jsonb, 0.72, 'Consult veterinarian immediately', '["Mastitis", "Milk Fever"]'::jsonb, a.user_id, now()-interval '5 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00100001';

INSERT INTO health_events (id, animal_id, event_type, description, symptoms, ai_risk_score, recommended_action, probable_diseases, recorded_by, event_date, updated_at)
SELECT gen_random_uuid(), a.id, 'checkup'::health_event_type, 'Routine health checkup - all normal', '[]'::jsonb, 0.12, 'No action needed', '[]'::jsonb, (SELECT id FROM users WHERE phone='+919876543211'), now()-interval '10 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00100002';

INSERT INTO health_events (id, animal_id, event_type, description, symptoms, ai_risk_score, recommended_action, probable_diseases, recorded_by, event_date, updated_at)
SELECT gen_random_uuid(), a.id, 'symptom'::health_event_type, 'Limping on right hind leg', '["lameness", "swelling"]'::jsonb, 0.55, 'Rest and anti-inflammatory', '["Foot Rot", "Joint Infection"]'::jsonb, a.user_id, now()-interval '3 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00200001';

INSERT INTO health_events (id, animal_id, event_type, description, symptoms, ai_risk_score, recommended_action, probable_diseases, recorded_by, event_date, updated_at)
SELECT gen_random_uuid(), a.id, 'emergency'::health_event_type, 'Difficulty breathing, nasal discharge', '["nasal_discharge", "coughing", "labored_breathing"]'::jsonb, 0.89, 'Emergency vet visit required', '["Pneumonia", "IBR"]'::jsonb, a.user_id, now()-interval '1 day', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00200002';

INSERT INTO health_events (id, animal_id, event_type, description, symptoms, ai_risk_score, recommended_action, probable_diseases, recorded_by, event_date, updated_at)
SELECT gen_random_uuid(), a.id, 'treatment'::health_event_type, 'Deworming completed with Albendazole', '[]'::jsonb, 0.05, 'Follow-up in 3 months', '[]'::jsonb, (SELECT id FROM users WHERE phone='+919876543211'), now()-interval '15 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00300001';

INSERT INTO health_events (id, animal_id, event_type, description, symptoms, ai_risk_score, recommended_action, probable_diseases, recorded_by, event_date, updated_at)
SELECT gen_random_uuid(), a.id, 'symptom'::health_event_type, 'Skin lesions on back and neck', '["skin_lesion", "hair_loss", "itching"]'::jsonb, 0.65, 'Skin scraping test recommended', '["Dermatophytosis", "Mange"]'::jsonb, a.user_id, now()-interval '7 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00400001';

INSERT INTO health_events (id, animal_id, event_type, description, symptoms, ai_risk_score, recommended_action, probable_diseases, recorded_by, event_date, updated_at)
SELECT gen_random_uuid(), a.id, 'symptom'::health_event_type, 'Diarrhea for 2 days', '["diarrhea", "dehydration"]'::jsonb, 0.58, 'ORS and veterinary consultation', '["Enterotoxemia", "Parasitic"]'::jsonb, a.user_id, now()-interval '2 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00100003';

INSERT INTO health_events (id, animal_id, event_type, description, symptoms, ai_risk_score, recommended_action, probable_diseases, recorded_by, event_date, updated_at)
SELECT gen_random_uuid(), a.id, 'checkup'::health_event_type, 'Pregnancy check - 6 months confirmed', '[]'::jsonb, 0.08, 'Extra nutrition, reduce work', '[]'::jsonb, (SELECT id FROM users WHERE phone='+919876543211'), now()-interval '20 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00400002';

-- ============== VACCINATIONS ==============
INSERT INTO vaccinations (id, animal_id, vaccine_name, administered_on, next_due, batch_number, recorded_by, created_at, updated_at)
SELECT gen_random_uuid(), a.id, v.vaccine, v.admin_date::date, v.due_date::date, v.batch, (SELECT id FROM users WHERE phone='+919876543211'), now()-interval '30 days', now()
FROM animals a, (VALUES
  ('KA00100001', 'FMD Vaccine', current_date-30, current_date+150, 'FMD-2026-001'),
  ('KA00100001', 'HS Vaccine', current_date-60, current_date+120, 'HS-2026-001'),
  ('KA00100002', 'FMD Vaccine', current_date-30, current_date+150, 'FMD-2026-002'),
  ('KA00100002', 'Brucellosis', current_date-90, current_date+275, 'BRU-2026-001'),
  ('KA00200001', 'FMD Vaccine', current_date-45, current_date+135, 'FMD-2026-003'),
  ('KA00200002', 'BQ Vaccine', current_date-20, current_date+160, 'BQ-2026-001'),
  ('KA00200002', 'FMD Vaccine', current_date-20, current_date+160, 'FMD-2026-004'),
  ('KA00300001', 'Anthrax', current_date-10, current_date+355, 'ANT-2026-001'),
  ('KA00400001', 'FMD Vaccine', current_date-15, current_date+165, 'FMD-2026-005'),
  ('KA00400002', 'HS Vaccine', current_date-25, current_date+155, 'HS-2026-002'),
  ('KA00100003', 'PPR Vaccine', current_date-40, current_date+140, 'PPR-2026-001')
) AS v(animal_tag, vaccine, admin_date, due_date, batch)
WHERE a.pashu_aadhaar_id = v.animal_tag;

-- ============== VET CONSULTATIONS ==============
INSERT INTO vet_consultations (id, animal_id, farmer_id, vet_id, status, priority, channel, farmer_notes, diagnosis, prescription, follow_up_date, district, created_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, (SELECT id FROM users WHERE phone='+919876543211'),
  'pending'::consultation_status, 'urgent'::consultation_priority, 'photo'::consultation_channel,
  'Cow not eating properly, milk reduced by half since 2 days', NULL, NULL, NULL, 'Tumkur', now()-interval '2 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00100001';

INSERT INTO vet_consultations (id, animal_id, farmer_id, vet_id, status, priority, channel, farmer_notes, diagnosis, prescription, follow_up_date, district, created_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, (SELECT id FROM users WHERE phone='+919876543211'),
  'pending'::consultation_status, 'emergency'::consultation_priority, 'referral'::consultation_channel,
  'Difficulty breathing, very weak, please come urgently', NULL, NULL, NULL, 'Tumkur', now()-interval '1 day', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00200002';

INSERT INTO vet_consultations (id, animal_id, farmer_id, vet_id, status, priority, channel, farmer_notes, diagnosis, prescription, follow_up_date, district, created_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, (SELECT id FROM users WHERE phone='+919876543211'),
  'in_review'::consultation_status, 'routine'::consultation_priority, 'photo'::consultation_channel,
  'Skin patches on back, been there for a week', NULL, NULL, NULL, 'Hassan', now()-interval '5 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00400001';

INSERT INTO vet_consultations (id, animal_id, farmer_id, vet_id, status, priority, channel, farmer_notes, diagnosis, prescription, follow_up_date, district, created_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, (SELECT id FROM users WHERE phone='+919876543211'),
  'diagnosed'::consultation_status, 'urgent'::consultation_priority, 'walk_in'::consultation_channel,
  'Limping badly, cannot walk properly', 'Foot Rot - Grade II. Clean and dress the wound.', 'Oxytetracycline 10mg/kg IM x 5 days. Foot bath with CuSO4 daily.', current_date+7, 'Tumkur', now()-interval '8 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00200001';

INSERT INTO vet_consultations (id, animal_id, farmer_id, vet_id, status, priority, channel, farmer_notes, diagnosis, prescription, follow_up_date, district, created_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, (SELECT id FROM users WHERE phone='+919876543211'),
  'diagnosed'::consultation_status, 'routine'::consultation_priority, 'walk_in'::consultation_channel,
  'Routine pregnancy check', 'Confirmed pregnant - 7 months. Expected calving in ~60 days.', 'Extra concentrate feed 2kg/day. Calcium supplement.', current_date+30, 'Tumkur', now()-interval '15 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00100002';

INSERT INTO vet_consultations (id, animal_id, farmer_id, vet_id, status, priority, channel, farmer_notes, diagnosis, prescription, follow_up_date, district, created_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, (SELECT id FROM users WHERE phone='+919876543211'),
  'closed'::consultation_status, 'routine'::consultation_priority, 'walk_in'::consultation_channel,
  'Follow-up after deworming', 'Healthy. Deworming effective. Weight improved.', 'Continue regular deworming every 3 months.', current_date+75, 'Tumkur', now()-interval '25 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00300001';

INSERT INTO vet_consultations (id, animal_id, farmer_id, vet_id, status, priority, channel, farmer_notes, diagnosis, prescription, follow_up_date, district, created_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, (SELECT id FROM users WHERE phone='+919876543211'),
  'closed'::consultation_status, 'urgent'::consultation_priority, 'referral'::consultation_channel,
  'Was not eating for 3 days', 'Indigestion due to foreign body. Treated with magnet therapy.', 'Rumen magnet administered. Soft feed for 7 days.', NULL, 'Hassan', now()-interval '30 days', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00400002';

INSERT INTO vet_consultations (id, animal_id, farmer_id, vet_id, status, priority, channel, farmer_notes, diagnosis, prescription, follow_up_date, district, created_at, updated_at)
SELECT gen_random_uuid(), a.id, a.user_id, (SELECT id FROM users WHERE phone='+919876543211'),
  'pending'::consultation_status, 'urgent'::consultation_priority, 'photo'::consultation_channel,
  'Goat has diarrhea, not eating, looks weak', NULL, NULL, NULL, 'Tumkur', now()-interval '1 day', now()
FROM animals a WHERE a.pashu_aadhaar_id = 'KA00100003';

-- ============== COMMUNITY ALERTS ==============
INSERT INTO community_alerts (id, reported_by, disease_name, lat, lon, radius_km, severity, verified, expires_at, created_at, updated_at)
SELECT gen_random_uuid(), id, 'Foot and Mouth Disease', 13.3379, 77.1173, 5.0, 'severe'::community_alert_severity, true, now()+interval '14 days', now()-interval '3 days', now() FROM users WHERE phone='+919876543214';
INSERT INTO community_alerts (id, reported_by, disease_name, lat, lon, radius_km, severity, verified, expires_at, created_at, updated_at)
SELECT gen_random_uuid(), id, 'Lumpy Skin Disease', 13.0068, 76.0996, 10.0, 'critical'::community_alert_severity, true, now()+interval '21 days', now()-interval '5 days', now() FROM users WHERE phone='+919876543216';
INSERT INTO community_alerts (id, reported_by, disease_name, lat, lon, radius_km, severity, verified, expires_at, created_at, updated_at)
SELECT gen_random_uuid(), id, 'Mastitis outbreak', 13.3400, 77.1200, 3.0, 'moderate'::community_alert_severity, false, now()+interval '7 days', now()-interval '1 day', now() FROM users WHERE phone='+919876543213';
INSERT INTO community_alerts (id, reported_by, disease_name, lat, lon, radius_km, severity, verified, expires_at, created_at, updated_at)
SELECT gen_random_uuid(), id, 'Hemorrhagic Septicemia', 14.4644, 75.9218, 8.0, 'severe'::community_alert_severity, true, now()+interval '10 days', now()-interval '7 days', now() FROM users WHERE phone='+919876543218';

-- ============== GOVT SCHEMES ==============
INSERT INTO govt_schemes (id, scheme_code, name, ministry, description, eligibility_criteria, required_documents, max_subsidy_amount, subsidy_percentage, is_active, valid_from, valid_to, created_at, updated_at) VALUES
(gen_random_uuid(), 'RGM-2026', 'Rashtriya Gokul Mission', 'DAHD', 'Conservation and development of indigenous cattle breeds through selective breeding', 'Farmers owning indigenous cattle breeds', '["Aadhaar", "Land records", "Animal registration"]'::jsonb, 50000, 75, true, '2026-01-01', '2027-03-31', now()-interval '90 days', now()),
(gen_random_uuid(), 'NLM-2026', 'National Livestock Mission', 'DAHD', 'Entrepreneurship development in livestock sector', 'BPL farmers, SHG members, small/marginal farmers', '["Aadhaar", "BPL card", "SHG membership"]'::jsonb, 250000, 50, true, '2026-04-01', '2027-03-31', now()-interval '15 days', now()),
(gen_random_uuid(), 'PMKISAN', 'PM-KISAN', 'Agriculture Ministry', 'Direct income support of Rs 6000/year', 'Land-owning farmers with up to 2 hectares', '["Aadhaar", "Land records", "Bank account"]'::jsonb, 6000, 100, true, '2026-01-01', '2026-12-31', now()-interval '90 days', now()),
(gen_random_uuid(), 'LISS-2026', 'Livestock Insurance Scheme', 'DAHD', 'Insurance at subsidized premiums', 'All livestock owners', '["Aadhaar", "Animal tag ID", "Health certificate"]'::jsonb, 100000, 50, true, '2026-01-01', '2027-03-31', now()-interval '60 days', now()),
(gen_random_uuid(), 'DEDS-2026', 'Dairy Entrepreneurship Dev Scheme', 'NABARD', 'Financial assistance for dairy farming', 'Dairy farmers, SHGs, cooperatives', '["Aadhaar", "Project proposal", "Bank statement"]'::jsonb, 500000, 33, true, '2026-04-01', '2027-03-31', now()-interval '10 days', now());

-- ============== TRANSACTIONS ==============
INSERT INTO transactions (id, user_id, type, amount, category, description, status, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543213'), 'income'::transaction_type, 350+random()*200, 'milk_sale', 'Daily milk sale to DCS', 'completed'::transaction_status, now()-interval '1 day' * d, now()
FROM generate_series(0,29) d;

INSERT INTO transactions (id, user_id, type, amount, category, description, status, created_at, updated_at) VALUES
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543213'), 'expense'::transaction_type, 2500, 'feed', 'Cattle feed - 50kg bag', 'completed'::transaction_status, now()-interval '5 days', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543213'), 'expense'::transaction_type, 800, 'medicine', 'Veterinary consultation fee', 'completed'::transaction_status, now()-interval '3 days', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543213'), 'expense'::transaction_type, 1200, 'feed', 'Mineral mixture - 25kg', 'completed'::transaction_status, now()-interval '10 days', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543213'), 'income'::transaction_type, 15000, 'subsidy', 'PM-KISAN installment', 'completed'::transaction_status, now()-interval '20 days', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543214'), 'income'::transaction_type, 8500, 'animal_sale', 'Sold male calf', 'completed'::transaction_status, now()-interval '12 days', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543214'), 'expense'::transaction_type, 3000, 'veterinary', 'Foot rot treatment', 'completed'::transaction_status, now()-interval '8 days', now());

-- ============== SELL RECORDS (marketplace) ==============
INSERT INTO sell_records (id, user_id, product_type, quantity, unit, price_per_unit, total_amount, buyer_name, buyer_phone, sold_at, notes, created_at, updated_at) VALUES
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543213'), 'milk'::product_type, 10, 'liters', 45, 450, 'Local tea shop', '+919900112233', now()-interval '2 days', 'Fresh morning milk', now()-interval '2 days', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543214'), 'manure'::product_type, 500, 'kg', 3, 1500, 'Organic farm nearby', '+919900334455', now()-interval '5 days', 'Dried cow dung', now()-interval '5 days', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543215'), 'milk'::product_type, 15, 'liters', 42, 630, 'Nandini DCS', '+919900556677', now()-interval '1 day', 'Evening collection', now()-interval '1 day', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543217'), 'eggs'::product_type, 30, 'pieces', 6, 180, 'Village shop', '+919900778899', now()-interval '3 days', 'Country eggs', now()-interval '3 days', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543216'), 'milk'::product_type, 8, 'liters', 48, 384, 'Hotel Mayura', '+919900990011', now()-interval '1 day', 'Premium A2 milk', now()-interval '1 day', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543219'), 'manure'::product_type, 200, 'kg', 4, 800, 'Nursery garden', '+919900112244', now()-interval '7 days', 'Composted', now()-interval '7 days', now()),
(gen_random_uuid(), (SELECT id FROM users WHERE phone='+919876543213'), 'milk'::product_type, 12, 'liters', 44, 528, 'Sweet shop', '+919900223344', now()-interval '4 days', 'Morning milk', now()-interval '4 days', now());

-- ============== INSURANCE ==============
INSERT INTO insurance_policies (id, animal_id, provider, policy_number, premium_amount, coverage_amount, valid_from, valid_to, status, created_at, updated_at)
SELECT gen_random_uuid(), a.id, 'United India Insurance', 'UII-KA-2026-001', 2500, 50000, now()-interval '6 months', now()+interval '6 months', 'active'::policy_status, now()-interval '180 days', now()
FROM animals a WHERE a.pashu_aadhaar_id='KA00100001';
INSERT INTO insurance_policies (id, animal_id, provider, policy_number, premium_amount, coverage_amount, valid_from, valid_to, status, created_at, updated_at)
SELECT gen_random_uuid(), a.id, 'New India Assurance', 'NIA-KA-2026-001', 3000, 60000, now()-interval '3 months', now()+interval '9 months', 'active'::policy_status, now()-interval '90 days', now()
FROM animals a WHERE a.pashu_aadhaar_id='KA00100002';
INSERT INTO insurance_policies (id, animal_id, provider, policy_number, premium_amount, coverage_amount, valid_from, valid_to, status, created_at, updated_at)
SELECT gen_random_uuid(), a.id, 'United India Insurance', 'UII-KA-2026-002', 2800, 55000, now()-interval '4 months', now()+interval '8 months', 'active'::policy_status, now()-interval '120 days', now()
FROM animals a WHERE a.pashu_aadhaar_id='KA00200002';
INSERT INTO insurance_policies (id, animal_id, provider, policy_number, premium_amount, coverage_amount, valid_from, valid_to, status, created_at, updated_at)
SELECT gen_random_uuid(), a.id, 'Oriental Insurance', 'OIC-KA-2026-001', 2200, 45000, now()-interval '2 months', now()+interval '10 months', 'active'::policy_status, now()-interval '60 days', now()
FROM animals a WHERE a.pashu_aadhaar_id='KA00300001';
INSERT INTO insurance_policies (id, animal_id, provider, policy_number, premium_amount, coverage_amount, valid_from, valid_to, status, created_at, updated_at)
SELECT gen_random_uuid(), a.id, 'New India Assurance', 'NIA-KA-2026-002', 2600, 52000, now()-interval '8 months', now()-interval '2 months', 'expired'::policy_status, now()-interval '240 days', now()
FROM animals a WHERE a.pashu_aadhaar_id='KA00400002';

-- ============== INSURANCE CLAIMS ==============
INSERT INTO insurance_claims (id, policy_id, claim_type, description, status, filed_at, updated_at)
SELECT gen_random_uuid(), p.id, 'treatment', 'Mastitis treatment costs - Rs 5000', 'under_review'::claim_status, now()-interval '5 days', now()
FROM insurance_policies p WHERE p.policy_number = 'UII-KA-2026-001';

-- ============== MEDICINES ==============
INSERT INTO medicines (id, name_en, name_kn, type, withdrawal_milk_days, withdrawal_meat_days, species_applicable, created_at, updated_at) VALUES
(gen_random_uuid(), 'Oxytetracycline', 'ಆಕ್ಸಿಟೆಟ್ರಾ', 'antibiotic', 7, 28, '["cattle", "goat", "sheep"]'::jsonb, now()-interval '90 days', now()),
(gen_random_uuid(), 'Albendazole', 'ಆಲ್ಬೆಂಡಝೋಲ್', 'anthelmintic', 3, 14, '["cattle", "goat", "sheep"]'::jsonb, now()-interval '90 days', now()),
(gen_random_uuid(), 'Ivermectin', 'ಐವರ್ಮೆಕ್ಟಿನ್', 'antiparasitic', 5, 21, '["cattle", "goat", "sheep"]'::jsonb, now()-interval '90 days', now()),
(gen_random_uuid(), 'Meloxicam', 'ಮೆಲೋಕ್ಸಿಕ್ಯಾಮ್', 'anti-inflammatory', 5, 15, '["cattle", "goat"]'::jsonb, now()-interval '90 days', now()),
(gen_random_uuid(), 'Calcium Borogluconate', 'ಕ್ಯಾಲ್ಸಿಯಂ', 'supplement', 0, 0, '["cattle"]'::jsonb, now()-interval '90 days', now());

-- ============== ADVISORY TIPS ==============
INSERT INTO advisory_tips (id, title_en, title_kn, body_en, body_kn, category, species_applicable, source, priority, is_active, published_at, updated_at) VALUES
(gen_random_uuid(), 'Summer Heat Care', 'ಬೇಸಿಗೆ ಆರೈಕೆ', 'Ensure 50-60L water/day and shade during 11AM-3PM', 'ಬೇಸಿಗೆಯಲ್ಲಿ ನೀರು ಒದಗಿಸಿ', 'health'::advisory_category, '["cattle","goat","sheep"]'::jsonb, 'ICAR'::advisory_source, 1, true, now()-interval '5 days', now()),
(gen_random_uuid(), 'Deworming Schedule', 'ಜಂತು ನಿವಾರಣೆ', 'Deworm every 3 months. Use albendazole for roundworms.', 'ಪ್ರತಿ 3 ತಿಂಗಳಿಗೊಮ್ಮೆ ಜಂತುನಾಶಕ', 'health'::advisory_category, '["cattle","goat","sheep"]'::jsonb, 'ICAR'::advisory_source, 2, true, now()-interval '10 days', now()),
(gen_random_uuid(), 'FMD Vaccination Drive', 'ಎಫ್‌ಎಂಡಿ ಲಸಿಕೆ', 'Free FMD camp at Tumkur vet hospital Apr 20-25', 'ಉಚಿತ ಎಫ್‌ಎಂಡಿ ಶಿಬಿರ', 'government'::advisory_category, '["cattle","goat"]'::jsonb, 'KMF'::advisory_source, 1, true, now()-interval '2 days', now()),
(gen_random_uuid(), 'Napier Grass Cultivation', 'ನೇಪಿಯರ್ ಹುಲ್ಲು', 'Plant CO-5 for 200 tonnes/year. Free seedlings from NDDB.', 'ನೇಪಿಯರ್ ಹುಲ್ಲು ಬೆಳೆಸಿ', 'feeding'::advisory_category, '["cattle"]'::jsonb, 'NABARD'::advisory_source, 3, true, now()-interval '15 days', now()),
(gen_random_uuid(), 'Mastitis Prevention', 'ಮಾಸ್ಟೈಟಿಸ್ ತಡೆ', 'Clean udders before/after milking. Use teat dip.', 'ಕೆಚ್ಚಲು ಶುಚಿಗೊಳಿಸಿ', 'health'::advisory_category, '["cattle"]'::jsonb, 'ICAR'::advisory_source, 1, true, now()-interval '8 days', now()),
(gen_random_uuid(), 'SHG Loan at 4%', 'ಎಸ್‌ಎಚ್‌ಜಿ ಸಾಲ', 'SHG members can get dairy loans at 4% via NABARD.', 'ಡೈರಿ ಸಾಲ 4% ಬಡ್ಡಿ', 'government'::advisory_category, '["cattle"]'::jsonb, 'NABARD'::advisory_source, 2, true, now()-interval '12 days', now());

-- ============== FEED INGREDIENTS ==============
INSERT INTO feed_ingredients (id, name_en, name_kn, category, protein_pct, energy_kcal, cost_per_kg, availability_season, locally_available, created_at, updated_at) VALUES
(gen_random_uuid(), 'Ragi Straw', 'ರಾಗಿ ಹುಲ್ಲು', 'roughage'::feed_category, 4.2, 1800, 3.5, 'year-round', true, now(), now()),
(gen_random_uuid(), 'Groundnut Cake', 'ಕಡಲೆ ಹಿಂಡಿ', 'concentrate'::feed_category, 45.0, 2600, 35, 'year-round', true, now(), now()),
(gen_random_uuid(), 'Cotton Seed Cake', 'ಹತ್ತಿ ಹಿಂಡಿ', 'concentrate'::feed_category, 22.0, 2400, 25, 'Oct-Mar', true, now(), now()),
(gen_random_uuid(), 'Napier Grass', 'ನೇಪಿಯರ್ ಹುಲ್ಲು', 'roughage'::feed_category, 8.5, 2000, 2, 'year-round', true, now(), now()),
(gen_random_uuid(), 'Mineral Mixture', 'ಖನಿಜ ಮಿಶ್ರಣ', 'mineral'::feed_category, 0, 0, 80, 'year-round', true, now(), now()),
(gen_random_uuid(), 'Maize Grain', 'ಜೋಳ', 'concentrate'::feed_category, 9.0, 3300, 20, 'Oct-Feb', true, now(), now()),
(gen_random_uuid(), 'Lucerne Hay', 'ಲೂಸರ್ನ್', 'roughage'::feed_category, 18.0, 2200, 12, 'Nov-Mar', false, now(), now()),
(gen_random_uuid(), 'Rice Bran', 'ಅಕ್ಕಿ ತೌಡು', 'supplement'::feed_category, 13.0, 2800, 15, 'year-round', true, now(), now());

-- ============== TRADITIONAL REMEDIES ==============
INSERT INTO traditional_remedies (id, name_en, name_kn, plant_ingredient, preparation_method, dosage_by_species, conditions_treated, evidence_rating, safety_warnings, source_reference, created_at, updated_at) VALUES
(gen_random_uuid(), 'Turmeric Paste', 'ಅರಿಶಿನ ಲೇಪ', 'Curcuma longa', 'Mix 50g turmeric with 100ml warm coconut oil', '{"cattle":"50g topically","goat":"20g topically"}'::jsonb, '["wound_healing","skin_infection","mastitis"]'::jsonb, 'icar_validated'::evidence_rating, 'Avoid in pregnant animals', 'ICAR-IVRI Compendium', now(), now()),
(gen_random_uuid(), 'Neem Decoction', 'ಬೇವು ಕಷಾಯ', 'Azadirachta indica', 'Boil 200g neem leaves in 2L water', '{"cattle":"500ml drench","goat":"200ml drench"}'::jsonb, '["ectoparasites","skin_disease","fever"]'::jsonb, 'studied'::evidence_rating, 'Avoid in early pregnancy', 'NABARD Ethnovet Manual', now(), now()),
(gen_random_uuid(), 'Ajwain Water', 'ಅಜ್ವಾನ ನೀರು', 'Trachyspermum ammi', 'Boil 100g ajwain in 1L water', '{"cattle":"500ml 2x daily","goat":"200ml 2x daily"}'::jsonb, '["indigestion","bloat","diarrhea"]'::jsonb, 'traditional'::evidence_rating, 'Reduce if diarrhea worsens', 'KA Ethnovet Practices', now(), now()),
(gen_random_uuid(), 'Aloe Vera Gel', 'ಲೋಳೆಸರ', 'Aloe barbadensis', 'Extract fresh gel from mature leaves', '{"cattle":"100g in feed","goat":"30g in feed"}'::jsonb, '["wound_healing","heat_stress","constipation"]'::jsonb, 'studied'::evidence_rating, 'Start with small dose', 'ICAR Research 2023', now(), now());

-- ============== SHG GROUPS ==============
INSERT INTO shg_groups (id, name, district, village_code, grading, member_count, monthly_savings, bank_linkage_amount, created_at, updated_at) VALUES
(gen_random_uuid(), 'Lakshmi Mahila SHG', 'Tumkur', 'TUMK-001', 'A'::shg_grading, 12, 500, 150000, now()-interval '180 days', now()),
(gen_random_uuid(), 'Nandini Dairy SHG', 'Tumkur', 'TUMK-002', 'B'::shg_grading, 10, 300, 80000, now()-interval '120 days', now()),
(gen_random_uuid(), 'Kaveri Women SHG', 'Hassan', 'HASN-001', 'A'::shg_grading, 15, 500, 200000, now()-interval '200 days', now()),
(gen_random_uuid(), 'Gokul Farmers Group', 'Mysore', 'MYSR-001', 'ungraded'::shg_grading, 8, 200, 0, now()-interval '30 days', now());

-- ============== WEATHER ALERTS ==============
INSERT INTO weather_alerts (id, district, alert_type, severity, description, valid_from, valid_to, source, created_at, updated_at) VALUES
(gen_random_uuid(), 'Tumkur', 'heat_wave', 'severe'::alert_severity, 'Max temp 42C. Keep livestock hydrated.', now(), now()+interval '3 days', 'IMD Bengaluru', now(), now()),
(gen_random_uuid(), 'Hassan', 'heavy_rain', 'moderate'::alert_severity, 'Heavy rainfall 100-150mm expected.', now()+interval '2 days', now()+interval '5 days', 'IMD Bengaluru', now(), now()),
(gen_random_uuid(), 'Tumkur', 'thunderstorm', 'low'::alert_severity, 'Isolated thunderstorms. Lightning risk.', now()+interval '1 day', now()+interval '2 days', 'IMD Bengaluru', now(), now()),
(gen_random_uuid(), 'Davangere', 'heat_wave', 'extreme'::alert_severity, 'Extreme heat >44C. No outdoor animals 10AM-4PM.', now()-interval '1 day', now()+interval '4 days', 'IMD Bengaluru', now()-interval '1 day', now());
