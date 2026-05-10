-- MFM Corporation Multi-Team Automation System
-- Database Schema for Supabase
-- Version: 3.0.0

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE workflow_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
CREATE TYPE task_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
CREATE TYPE team_type AS ENUM ('research', 'planning', 'development', 'management', 'innovation', 'marketing', 'media', 'technology', 'mcp_llm', 'market_intelligence', 'legal', 'operations');
CREATE TYPE notification_type AS ENUM ('email', 'sms', 'slack', 'webhook', 'in_app');
CREATE TYPE notification_priority AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE meeting_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
CREATE TYPE report_type AS ENUM ('team_performance', 'system_health', 'executive_dashboard', 'compliance', 'custom');
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'team_member', 'viewer');
CREATE TYPE agent_status AS ENUM ('active', 'idle', 'busy', 'offline', 'maintenance', 'error');
CREATE TYPE legal_area AS ENUM ('contract_law', 'corporate_law', 'employment_law', 'intellectual_property', 'taxation_law', 'compliance', 'litigation', 'regulatory', 'cyber_law', 'real_estate', 'banking_finance', 'environmental_law');

-- =============================================================================
-- USERS AND AUTHENTICATION
-- =============================================================================

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role user_role DEFAULT 'team_member',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User profiles table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    team_affiliation team_type,
    avatar_url TEXT,
    bio TEXT,
    preferences JSONB DEFAULT '{}',
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- WORKFLOWS AND TASKS
-- =============================================================================

-- Workflows table
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status workflow_status DEFAULT 'pending',
    priority INTEGER DEFAULT 1,
    created_by UUID REFERENCES users(id),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    team_name team_type NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    status task_status DEFAULT 'pending',
    priority INTEGER DEFAULT 1,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- TEAMS AND AGENTS
-- =============================================================================

-- Teams table
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name team_type UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    configuration JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agents table (for Operations Manager)
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    agent_type team_type NOT NULL,
    status agent_status DEFAULT 'active',
    current_task_id UUID REFERENCES tasks(id),
    tasks_completed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0,
    average_task_time FLOAT DEFAULT 0.0,
    utilization_rate FLOAT DEFAULT 0.0,
    performance_score FLOAT DEFAULT 0.0,
    last_active TIMESTAMP WITH TIME ZONE,
    skills TEXT[],
    capacity INTEGER DEFAULT 5,
    current_load INTEGER DEFAULT 0,
    error_rate FLOAT DEFAULT 0.0,
    response_time_ms FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- NOTIFICATIONS
-- =============================================================================

-- Notifications table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type notification_type DEFAULT 'in_app',
    priority notification_priority DEFAULT 'medium',
    is_read BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    external_id VARCHAR(255), -- For tracking external notifications
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notification settings table
CREATE TABLE notification_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    notification_type notification_type NOT NULL,
    is_enabled BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, notification_type)
);

-- =============================================================================
-- MEETINGS AND SCHEDULING
-- =============================================================================

-- Meetings table
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    organizer_id UUID REFERENCES users(id),
    status meeting_status DEFAULT 'scheduled',
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    location VARCHAR(255),
    meeting_url TEXT,
    calendar_id VARCHAR(255),
    external_meeting_id VARCHAR(255),
    attendees UUID[] DEFAULT '{}',
    agenda TEXT[],
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Meeting reminders table
CREATE TABLE meeting_reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES meetings(id) ON DELETE CASCADE,
    reminder_time TIMESTAMP WITH TIME ZONE NOT NULL,
    reminder_type VARCHAR(50) DEFAULT 'email',
    is_sent BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- REPORTING AND ANALYTICS
-- =============================================================================

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type report_type NOT NULL,
    description TEXT,
    parameters JSONB DEFAULT '{}',
    data JSONB,
    format VARCHAR(50) DEFAULT 'json',
    file_path TEXT,
    generated_by UUID REFERENCES users(id),
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Team metrics table
CREATE TABLE team_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_name team_type NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(50),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- System metrics table
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(50),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- =============================================================================
-- LEGAL TEAM SPECIFIC
-- =============================================================================

-- Legal assessments table
CREATE TABLE legal_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    area legal_area NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    compliance_score FLOAT NOT NULL,
    legal_issues TEXT[],
    recommendations TEXT[],
    required_actions TEXT[],
    deadlines TIMESTAMP WITH TIME ZONE[],
    supporting_documents TEXT[],
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    next_review TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Compliance checks table
CREATE TABLE compliance_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    regulation VARCHAR(255) NOT NULL,
    compliance_status BOOLEAN NOT NULL,
    gaps TEXT[],
    remediation_steps TEXT[],
    priority VARCHAR(20) NOT NULL,
    responsible_party VARCHAR(255),
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Legal documents table
CREATE TABLE legal_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    parameters JSONB DEFAULT '{}',
    validation JSONB,
    file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- OPERATIONS MANAGER SPECIFIC
-- =============================================================================

-- Optimization recommendations table
CREATE TABLE optimization_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(100) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    target_agents TEXT[],
    expected_improvement TEXT,
    implementation_steps TEXT[],
    estimated_time_minutes INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workload distribution table
CREATE TABLE workload_distribution (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    total_tasks INTEGER NOT NULL,
    distributed_tasks INTEGER NOT NULL,
    pending_tasks INTEGER NOT NULL,
    agent_loads JSONB DEFAULT '{}',
    bottlenecks TEXT[],
    underutilized_agents TEXT[],
    optimal_distribution JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- ERROR RECOVERY AND LOGGING
-- =============================================================================

-- Error logs table
CREATE TABLE error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    component VARCHAR(100),
    severity VARCHAR(20) DEFAULT 'medium',
    context JSONB DEFAULT '{}',
    user_id UUID REFERENCES users(id),
    workflow_id UUID REFERENCES workflows(id),
    task_id UUID REFERENCES tasks(id),
    resolved BOOLEAN DEFAULT false,
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recovery sessions table
CREATE TABLE recovery_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    error_id UUID REFERENCES error_logs(id),
    team_name team_type,
    operation_name VARCHAR(255),
    attempt_count INTEGER DEFAULT 1,
    max_attempts INTEGER DEFAULT 3,
    status VARCHAR(20) DEFAULT 'active',
    recovery_strategy TEXT,
    outcome TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- =============================================================================
-- FILE STORAGE REFERENCES
-- =============================================================================

-- File references table
CREATE TABLE file_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    bucket_name VARCHAR(255),
    storage_url TEXT,
    uploaded_by UUID REFERENCES users(id),
    associated_type VARCHAR(100), -- 'workflow', 'task', 'report', 'legal_document', etc.
    associated_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- SYSTEM CONFIGURATION
-- =============================================================================

-- System settings table
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feature flags table
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    is_enabled BOOLEAN DEFAULT false,
    description TEXT,
    rollout_percentage FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Workflows indexes
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_created_at ON workflows(created_at);
CREATE INDEX idx_workflows_created_by ON workflows(created_by);

-- Tasks indexes
CREATE INDEX idx_tasks_workflow_id ON tasks(workflow_id);
CREATE INDEX idx_tasks_team_name ON tasks(team_name);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

-- Agents indexes
CREATE INDEX idx_agents_agent_type ON agents(agent_type);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_performance_score ON agents(performance_score);

-- Notifications indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- Meetings indexes
CREATE INDEX idx_meetings_organizer_id ON meetings(organizer_id);
CREATE INDEX idx_meetings_start_time ON meetings(start_time);
CREATE INDEX idx_meetings_status ON meetings(status);

-- Reports indexes
CREATE INDEX idx_reports_type ON reports(type);
CREATE INDEX idx_reports_created_at ON reports(created_at);

-- Metrics indexes
CREATE INDEX idx_team_metrics_team_name ON team_metrics(team_name);
CREATE INDEX idx_team_metrics_recorded_at ON team_metrics(recorded_at);
CREATE INDEX idx_system_metrics_recorded_at ON system_metrics(recorded_at);

-- Legal team indexes
CREATE INDEX idx_legal_assessments_area ON legal_assessments(area);
CREATE INDEX idx_legal_assessments_assessment_date ON legal_assessments(assessment_date);
CREATE INDEX idx_compliance_checks_due_date ON compliance_checks(due_date);

-- Error logs indexes
CREATE INDEX idx_error_logs_created_at ON error_logs(created_at);
CREATE INDEX idx_error_logs_severity ON error_logs(severity);
CREATE INDEX idx_error_logs_resolved ON error_logs(resolved);

-- =============================================================================
-- TRIGGERS AND FUNCTIONS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meetings_updated_at BEFORE UPDATE ON meetings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_settings_updated_at BEFORE UPDATE ON notification_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feature_flags_updated_at BEFORE UPDATE ON feature_flags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_references ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- RLS Policies for user_sessions
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own sessions" ON user_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for workflows
CREATE POLICY "Users can view own workflows" ON workflows
    FOR SELECT USING (created_by = auth.uid());

CREATE POLICY "Users can create workflows" ON workflows
    FOR INSERT WITH CHECK (created_by = auth.uid());

CREATE POLICY "Users can update own workflows" ON workflows
    FOR UPDATE USING (created_by = auth.uid());

-- RLS Policies for notifications
CREATE POLICY "Users can view own notifications" ON notifications
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can update own notifications" ON notifications
    FOR UPDATE USING (user_id = auth.uid());

-- RLS Policies for meetings
CREATE POLICY "Users can view meetings they're attending" ON meetings
    FOR SELECT USING (organizer_id = auth.uid() OR auth.uid() = ANY(attendees));

-- RLS Policies for reports
CREATE POLICY "Users can view own reports" ON reports
    FOR SELECT USING (generated_by = auth.uid() OR is_public = true);

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Insert default teams
INSERT INTO teams (name, display_name, description) VALUES
('research', 'Research Team', 'Conducts comprehensive research and analysis'),
('planning', 'Planning Team', 'Creates strategic plans and roadmaps'),
('development', 'Development Team', 'Develops and implements solutions'),
('management', 'Management Team', 'Oversees project management and quality'),
('innovation', 'Innovation Team', 'Tracks trends and drives innovation'),
('marketing', 'Marketing Team', 'Handles marketing and promotion'),
('media', 'Media Team', 'Manages media content and communications'),
('technology', 'Technology Team', 'Tracks technology and tools'),
('mcp_llm', 'MCP/LLM Team', 'Integrates AI and language models'),
('market_intelligence', 'Market Intelligence Team', 'Analyzes market trends'),
('legal', 'Legal Team', 'Handles legal compliance and documentation'),
('operations', 'Operations Manager', 'Optimizes agent performance');

-- Insert default system settings
INSERT INTO system_settings (key, value, description, is_public) VALUES
('app_name', 'MFM Corporation Multi-Team Automation', 'Application name', true),
('app_version', '3.0.0', 'Application version', true),
('max_concurrent_workflows', '10', 'Maximum concurrent workflows', false),
('workflow_timeout_minutes', '60', 'Workflow timeout in minutes', false),
('error_retry_attempts', '3', 'Maximum error retry attempts', false);

-- Insert default feature flags
INSERT INTO feature_flags (name, is_enabled, description, rollout_percentage) VALUES
('enable_legal_team', true, 'Enable Legal Team functionality', 100.0),
('enable_operations_manager', true, 'Enable Operations Manager functionality', 100.0),
('enable_innovation_team', true, 'Enable Innovation Team functionality', 100.0),
('enable_market_intelligence', true, 'Enable Market Intelligence functionality', 100.0),
('enable_technology_tracking', true, 'Enable Technology Tracking functionality', 100.0),
('enable_mcp_llm_integration', true, 'Enable MCP/LLM integration', 100.0),
('enable_marketing_team', true, 'Enable Marketing Team functionality', 100.0),
('enable_media_team', true, 'Enable Media Team functionality', 100.0);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- View for workflow statistics
CREATE VIEW workflow_stats AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(duration_seconds) as avg_duration,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_execution_time
FROM workflows 
WHERE started_at IS NOT NULL 
GROUP BY status;

-- View for team performance
CREATE VIEW team_performance AS
SELECT 
    t.name as team_name,
    COUNT(ta.id) as total_tasks,
    COUNT(CASE WHEN ta.status = 'completed' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN ta.status = 'failed' THEN 1 END) as failed_tasks,
    AVG(ta.duration_seconds) as avg_task_duration,
    AVG(ta.retry_count) as avg_retries
FROM teams t
LEFT JOIN tasks ta ON t.name = ta.team_name
GROUP BY t.name, t.display_name;

-- View for user activity
CREATE VIEW user_activity AS
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(w.id) as workflows_created,
    COUNT(n.id) as notifications_received,
    MAX(u.last_login) as last_login
FROM users u
LEFT JOIN workflows w ON u.id = w.created_by
LEFT JOIN notifications n ON u.id = n.user_id
GROUP BY u.id, u.username, u.email;
