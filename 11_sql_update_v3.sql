ALTER TABLE core.tasks ADD COLUMN IF NOT EXISTS prioridad VARCHAR(20) DEFAULT 'media';
ALTER TABLE core.tasks ADD COLUMN IF NOT EXISTS tipo_tarea VARCHAR(50) DEFAULT 'operativa';

ALTER TABLE core.ideas ADD COLUMN IF NOT EXISTS prioridad_sugerida VARCHAR(20) DEFAULT 'media';
ALTER TABLE core.ideas ADD COLUMN IF NOT EXISTS tipo_tarea_sugerida VARCHAR(50) DEFAULT 'operativa';
