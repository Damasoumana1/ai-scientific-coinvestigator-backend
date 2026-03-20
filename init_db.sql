-- ==========================================
-- EXTENSIONS
-- ==========================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================
-- USERS
-- ==========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    institution TEXT,
    role TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- PROJECTS
-- ==========================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    research_field TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- RESEARCH PAPERS
-- ==========================================

CREATE TABLE research_papers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT,
    authors TEXT,
    journal TEXT,
    publication_year INT,
    pdf_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- PAPER CHUNKS (RAG)
-- ==========================================

CREATE TABLE paper_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id UUID REFERENCES research_papers(id) ON DELETE CASCADE,
    chunk_index INT,
    content TEXT,
    section TEXT,
    metadata JSONB
);

-- ==========================================
-- ANALYSIS RUNS
-- ==========================================

CREATE TABLE analysis_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    model_used TEXT,
    status TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- ==========================================
-- CONTRADICTIONS
-- ==========================================

CREATE TABLE contradictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_runs(id) ON DELETE CASCADE,
    paper_a UUID REFERENCES research_papers(id),
    paper_b UUID REFERENCES research_papers(id),
    variable TEXT,
    statement_a TEXT,
    statement_b TEXT,
    confidence_score FLOAT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- RESEARCH GAPS
-- ==========================================

CREATE TABLE research_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_runs(id) ON DELETE CASCADE,
    description TEXT,
    importance_score FLOAT,
    suggested_direction TEXT
);

-- ==========================================
-- EXPERIMENTAL PROTOCOLS
-- ==========================================

CREATE TABLE experimental_protocols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_runs(id) ON DELETE CASCADE,
    hypothesis TEXT,
    independent_variables JSONB,
    dependent_variables JSONB,
    control_variables JSONB,
    methodology TEXT,
    risk_analysis TEXT,
    estimated_cost TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- REASONING TRACES
-- ==========================================

CREATE TABLE reasoning_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_runs(id) ON DELETE CASCADE,
    step_number INT,
    reasoning TEXT,
    source_chunks JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- EXPORTS
-- ==========================================

CREATE TABLE exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_runs(id) ON DELETE CASCADE,
    format TEXT,
    file_path TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- ACTIVITY LOGS
-- ==========================================

CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_papers_project ON research_papers(project_id);
CREATE INDEX idx_chunks_paper ON paper_chunks(paper_id);
CREATE INDEX idx_analysis_project ON analysis_runs(project_id);
CREATE INDEX idx_contradictions_analysis ON contradictions(analysis_id);
CREATE INDEX idx_protocols_analysis ON experimental_protocols(analysis_id);
CREATE INDEX idx_reasoning_analysis ON reasoning_traces(analysis_id);
