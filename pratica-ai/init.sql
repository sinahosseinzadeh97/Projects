-- === FILE: init.sql ===
-- PostgreSQL initialization for Sinistri FNOL Agent
-- Conforme IVASS Reg. 40/2018 — GDPR Art. 30
-- Region: eu-south-1 (Milano)

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Performance Indexes ───────────────────────────────────────
-- NOTE: Tables are created by SQLAlchemy at app startup.
-- These indexes are wrapped in DO blocks so that init.sql
-- succeeds even when run before the app has created the tables.

DO $$
BEGIN
    -- Sinistri table indexes
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sinistri') THEN
        CREATE INDEX IF NOT EXISTS idx_sinistri_session_id      ON sinistri(session_id);
        CREATE INDEX IF NOT EXISTS idx_sinistri_stato           ON sinistri(stato);
        CREATE INDEX IF NOT EXISTS idx_sinistri_created_at      ON sinistri(created_at);
        CREATE INDEX IF NOT EXISTS idx_sinistri_codice_fiscale  ON sinistri(codice_fiscale);
        CREATE INDEX IF NOT EXISTS idx_sinistri_claim_type      ON sinistri(claim_type);
        CREATE INDEX IF NOT EXISTS idx_sinistri_provincia       ON sinistri(provincia);

        COMMENT ON TABLE sinistri IS
            'Registro sinistri FNOL — conforme IVASS Reg. 40/2018';
    END IF;

    -- GDPR Audit Log indexes
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_log_gdpr') THEN
        CREATE INDEX IF NOT EXISTS idx_audit_log_gdpr_timestamp   ON audit_log_gdpr(timestamp);
        CREATE INDEX IF NOT EXISTS idx_audit_log_gdpr_risorsa_id  ON audit_log_gdpr(risorsa_id);
        CREATE INDEX IF NOT EXISTS idx_audit_log_gdpr_azione      ON audit_log_gdpr(azione);
        CREATE INDEX IF NOT EXISTS idx_audit_log_gdpr_operator_id ON audit_log_gdpr(operator_id);

        COMMENT ON TABLE audit_log_gdpr IS
            'Log di audit GDPR — Art. 30 registro trattamenti, Art. 5(2) accountability';
    END IF;

    -- Consensi GDPR indexes
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'consensi_gdpr') THEN
        CREATE INDEX IF NOT EXISTS idx_consensi_gdpr_session_id ON consensi_gdpr(session_id);

        COMMENT ON TABLE consensi_gdpr IS
            'Registro consensi — Art. 6, 7, 9 GDPR — immutabile';
    END IF;

    -- Trascrizioni indexes
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'trascrizioni') THEN
        CREATE INDEX IF NOT EXISTS idx_trascrizioni_sinistro_id ON trascrizioni(sinistro_id);

        COMMENT ON TABLE trascrizioni IS
            'Trascrizioni turno per turno delle sessioni di acquisizione sinistri';
    END IF;

    -- Operatori comment
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'operatori') THEN
        COMMENT ON TABLE operatori IS
            'Operatori assicurativi autorizzati — accesso controllato';
    END IF;
END $$;
