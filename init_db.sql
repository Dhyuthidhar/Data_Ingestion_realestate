-- ============================================
-- Property Agentic Engine - Database Schema
-- ============================================

-- Drop existing tables if recreating
DROP TABLE IF EXISTS properties CASCADE;

-- Main properties table
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    
    -- Location identifiers
    address VARCHAR(500) NOT NULL,
    city VARCHAR(200) NOT NULL,
    state VARCHAR(2) NOT NULL,
    
    -- Research data (JSONB for flexibility)
    research_data JSONB NOT NULL,
    
    -- Metadata
    research_time_seconds DECIMAL(10,2),
    agents_used INTEGER DEFAULT 5,
    data_quality VARCHAR(50) DEFAULT 'high',
    research_cost_cents INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Unique constraint on address
    UNIQUE(address, city, state)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_properties_location
    ON properties(city, state);

CREATE INDEX IF NOT EXISTS idx_properties_updated
    ON properties(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_properties_search
    ON properties(address, city, state);

CREATE INDEX IF NOT EXISTS idx_properties_created
    ON properties(created_at DESC);

-- GIN index for JSONB querying
CREATE INDEX IF NOT EXISTS idx_properties_research_data
    ON properties USING GIN(research_data);

-- Full-text search on address
CREATE INDEX IF NOT EXISTS idx_properties_address_fts
    ON properties USING GIN(to_tsvector('english', address));

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update timestamp on row update
DROP TRIGGER IF EXISTS update_properties_updated_at ON properties;
CREATE TRIGGER update_properties_updated_at
    BEFORE UPDATE ON properties
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for quick stats
CREATE OR REPLACE VIEW property_stats AS
SELECT
    COUNT(*) as total_properties,
    COUNT(DISTINCT city || ', ' || state) as unique_markets,
    AVG(research_time_seconds) as avg_research_time_seconds,
    SUM(research_cost_cents) as total_research_cost_cents,
    MAX(updated_at) as last_research_timestamp,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as properties_today,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as properties_this_week
FROM properties;

-- Sample query function for testing
CREATE OR REPLACE FUNCTION get_property_by_location(
    p_address VARCHAR,
    p_city VARCHAR,
    p_state VARCHAR
)
RETURNS TABLE(
    property_id INTEGER,
    address VARCHAR,
    research_data JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        id,
        properties.address,
        properties.research_data,
        properties.created_at,
        properties.updated_at
    FROM properties
    WHERE properties.address = p_address
        AND properties.city = p_city
        AND properties.state = p_state;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust user as needed)
-- GRANT ALL PRIVILEGES ON TABLE properties TO postgres;
-- GRANT ALL PRIVILEGES ON SEQUENCE properties_id_seq TO postgres;
