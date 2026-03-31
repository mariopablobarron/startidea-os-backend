CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE IF NOT EXISTS core.projects (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'startidea_core',
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    estado VARCHAR(20) DEFAULT 'planning', 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.ideas (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'startidea_core',
    user_id VARCHAR(50) NOT NULL,
    project_id INTEGER REFERENCES core.projects(id) ON DELETE SET NULL,
    raw_input TEXT NOT NULL,
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(50),
    accion_sugerida TEXT,
    estado VARCHAR(20) DEFAULT 'capturada', 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.tasks (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) DEFAULT 'startidea_core',
    idea_id INTEGER REFERENCES core.ideas(id) ON DELETE SET NULL, 
    project_id INTEGER REFERENCES core.projects(id) ON DELETE CASCADE, 
    titulo VARCHAR(150) NOT NULL,
    asignado_a VARCHAR(50) DEFAULT 'system', 
    estado VARCHAR(20) DEFAULT 'todo', 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ideas_state_tenant ON core.ideas(estado, tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_state_tenant ON core.tasks(estado, tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON core.tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_ideas_project ON core.ideas(project_id);

CREATE OR REPLACE FUNCTION core.update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_core_projects_modtime BEFORE UPDATE ON core.projects FOR EACH ROW EXECUTE FUNCTION core.update_modified_column();
CREATE TRIGGER update_core_ideas_modtime BEFORE UPDATE ON core.ideas FOR EACH ROW EXECUTE FUNCTION core.update_modified_column();
CREATE TRIGGER update_core_tasks_modtime BEFORE UPDATE ON core.tasks FOR EACH ROW EXECUTE FUNCTION core.update_modified_column();
