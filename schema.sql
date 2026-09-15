PRAGMA foreign_keys = ON;

CREATE TABLE modality_operators (
    operator_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    canonical_name TEXT NOT NULL,
    definition TEXT NOT NULL,
    evidence_channel TEXT NOT NULL,
    may_assert_action INTEGER NOT NULL CHECK (may_assert_action IN (0, 1))
);

CREATE TABLE gestalts (
    gestalt_id TEXT PRIMARY KEY,
    glyph TEXT,
    lexical_form TEXT NOT NULL,
    sense TEXT NOT NULL,
    route TEXT NOT NULL CHECK (route IN ('G', 'GA', 'L', 'P')),
    recoverability_note TEXT NOT NULL
);

CREATE TABLE tote_loops (
    loop_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    objective TEXT NOT NULL,
    initial_test TEXT NOT NULL,
    exit_predicate TEXT NOT NULL,
    max_iterations INTEGER NOT NULL CHECK (max_iterations > 0),
    epistemic_status TEXT NOT NULL CHECK (
        epistemic_status IN ('CANONICAL', 'DERIVED', 'EXPERIMENTAL')
    )
);

CREATE TABLE tote_steps (
    loop_id TEXT NOT NULL REFERENCES tote_loops(loop_id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,
    phase TEXT NOT NULL CHECK (phase IN ('TEST', 'OPERATE', 'EXIT')),
    operator_id TEXT REFERENCES modality_operators(operator_id),
    plain_text TEXT NOT NULL,
    nych_text TEXT NOT NULL,
    proposition_kind TEXT NOT NULL CHECK (
        proposition_kind IN ('OBSERVED', 'MODELED', 'INTENDED', 'EXECUTED', 'POSTCONDITION')
    ),
    provenance TEXT NOT NULL CHECK (
        provenance IN ('explicit', 'inferred', 'predicted', 'postcondition')
    ),
    next_on_match INTEGER,
    next_on_mismatch INTEGER,
    PRIMARY KEY (loop_id, step_index)
);

CREATE TABLE loop_gestalts (
    loop_id TEXT NOT NULL REFERENCES tote_loops(loop_id) ON DELETE CASCADE,
    gestalt_id TEXT NOT NULL REFERENCES gestalts(gestalt_id),
    role TEXT NOT NULL,
    PRIMARY KEY (loop_id, gestalt_id, role)
);

CREATE INDEX idx_steps_phase ON tote_steps(phase);
CREATE INDEX idx_steps_operator ON tote_steps(operator_id);
CREATE INDEX idx_loops_domain ON tote_loops(domain);

