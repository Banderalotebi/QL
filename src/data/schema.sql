-- DOMAIN 1: The Cryptographic Corpus
CREATE TABLE IF NOT EXISTS surah_master (
    surah_id INT PRIMARY KEY,
    surah_name VARCHAR(100),
    total_verses INT,
    revelation_type VARCHAR(20), -- Meccan/Medinan
    has_muqattaat BOOLEAN DEFAULT FALSE,
    vector_magnitude FLOAT,      -- From surah_mathematical_patterns.csv
    significance_score FLOAT     -- Composite score
);

CREATE TABLE IF NOT EXISTS muqattaat_prefix (
    prefix_id SERIAL PRIMARY KEY,
    surah_id INT REFERENCES surah_master(surah_id),
    letters_sequence VARCHAR(20), -- e.g., 'ALM'
    abjad_weight INT,             -- Gematria value
    anchor_verse_index INT,       -- Modulo pointer
    saturation_percentage FLOAT
);

CREATE TABLE IF NOT EXISTS verse_data (
    verse_id SERIAL PRIMARY KEY,
    surah_id INT REFERENCES surah_master(surah_id),
    verse_number INT,
    text_uthmani TEXT,           -- Original Rasm
    text_clean TEXT,             -- Simple format for agents
    is_anchor_flare BOOLEAN DEFAULT FALSE,
    prefix_density_ratio FLOAT
);

CREATE TABLE IF NOT EXISTS rigid_flow_matrix (
    transition_id SERIAL PRIMARY KEY,
    from_letter CHAR(1),
    to_letter CHAR(1),
    probability_weight FLOAT,
    is_forbidden BOOLEAN
);

CREATE TABLE IF NOT EXISTS arabic_roots (
    root_id SERIAL PRIMARY KEY,
    root_word VARCHAR(10) UNIQUE,
    occurrence_count INT
);

-- DOMAIN 2: The Command & Control (C2) Registry
CREATE TABLE IF NOT EXISTS c2_research_ticket (
    ticket_id VARCHAR(50) PRIMARY KEY,
    agent_role VARCHAR(50),      -- e.g., 'MathScout'
    target_pattern TEXT,
    status VARCHAR(20) DEFAULT 'Queued',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS c2_finding_log (
    log_id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) REFERENCES c2_research_ticket(ticket_id),
    discovery_title VARCHAR(200),
    json_payload JSONB,          -- Stores the matrix/arrays
    score_boost FLOAT
);
