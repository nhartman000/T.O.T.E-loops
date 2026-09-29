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

-- A loop row is one VERSION of how to perform a behavior.
-- No loop is definitive: behavior_id names the behavior, and at most one
-- version per behavior is the CURRENT best-accepted version. Better versions
-- are added as new rows that supersede older ones; history is never deleted.
CREATE TABLE tote_loops (
    loop_id TEXT PRIMARY KEY,
    behavior_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    status TEXT NOT NULL CHECK (status IN ('CURRENT', 'CANDIDATE', 'SUPERSEDED')),
    supersedes TEXT REFERENCES tote_loops(loop_id),
    name TEXT NOT NULL,
    domain TEXT NOT NULL,
    objective TEXT NOT NULL,
    initial_test TEXT NOT NULL,
    exit_predicate TEXT NOT NULL,
    max_iterations INTEGER NOT NULL CHECK (max_iterations > 0),
    epistemic_status TEXT NOT NULL CHECK (
        epistemic_status IN ('CANONICAL', 'DERIVED', 'EXPERIMENTAL')
    ),
    source_basis TEXT NOT NULL,
    verification_tier TEXT NOT NULL CHECK (
        verification_tier IN (
            'UNSPECIFIED',
            'MACHINE_DRAFTED',
            'HUMAN_REVIEWED',
            'HUMAN_VERIFIED',
            'OBSERVATION_VERIFIED'
        )
    ),
    UNIQUE (behavior_id, version)
);

-- sense_channel records WHICH sense carries a step. For external_observe it is
-- the sense the evidence arrives through; for internal_model it is the modality
-- being imagined or recalled; 'instrument' is evidence read from a tool,
-- log, or measurement; 'none' is used where no sense applies.
CREATE TABLE tote_steps (
    loop_id TEXT NOT NULL REFERENCES tote_loops(loop_id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,
    step_label TEXT NOT NULL,
    phase TEXT NOT NULL CHECK (phase IN ('TEST', 'OPERATE', 'EXIT')),
    operator_id TEXT REFERENCES modality_operators(operator_id),
    sense_channel TEXT NOT NULL CHECK (
        sense_channel IN (
            'visual', 'auditory', 'kinesthetic', 'olfactory', 'gustatory',
            'instrument', 'internal', 'none'
        )
    ),
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
    PRIMARY KEY (loop_id, step_index),
    UNIQUE (loop_id, step_label)
);

CREATE TABLE loop_gestalts (
    loop_id TEXT NOT NULL REFERENCES tote_loops(loop_id) ON DELETE CASCADE,
    gestalt_id TEXT NOT NULL REFERENCES gestalts(gestalt_id),
    role TEXT NOT NULL,
    PRIMARY KEY (loop_id, gestalt_id, role)
);

CREATE UNIQUE INDEX idx_one_current_per_behavior
    ON tote_loops(behavior_id) WHERE status = 'CURRENT';
CREATE INDEX idx_steps_phase ON tote_steps(phase);
CREATE INDEX idx_steps_operator ON tote_steps(operator_id);
CREATE INDEX idx_steps_sense ON tote_steps(sense_channel);
CREATE INDEX idx_loops_domain ON tote_loops(domain);
CREATE INDEX idx_loops_behavior ON tote_loops(behavior_id);
