-- Supabase Database Schema for Redwood Bingo QR Game
-- Run this in your Supabase SQL Editor to create the required tables

-- Create games table
CREATE TABLE IF NOT EXISTS games (
    id BIGSERIAL PRIMARY KEY,
    game_id VARCHAR(6) UNIQUE NOT NULL,
    host_name VARCHAR(255) NOT NULL,
    current_calls JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT false,
    winner VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create players table
CREATE TABLE IF NOT EXISTS players (
    id BIGSERIAL PRIMARY KEY,
    player_id UUID UNIQUE NOT NULL,
    game_id VARCHAR(6) REFERENCES games(game_id) ON DELETE CASCADE,
    player_name VARCHAR(255) NOT NULL,
    card JSONB NOT NULL,
    marked JSONB DEFAULT '[false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false]'::jsonb,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_games_game_id ON games(game_id);
CREATE INDEX IF NOT EXISTS idx_players_game_id ON players(game_id);
CREATE INDEX IF NOT EXISTS idx_players_player_id ON players(player_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) - optional but recommended
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE players ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust as needed for your security requirements)
CREATE POLICY "Allow all operations on games" ON games
    FOR ALL USING (true);

CREATE POLICY "Allow all operations on players" ON players
    FOR ALL USING (true);

-- Grant necessary permissions
GRANT ALL ON games TO anon, authenticated;
GRANT ALL ON players TO anon, authenticated;
GRANT USAGE ON SEQUENCE games_id_seq TO anon, authenticated;
GRANT USAGE ON SEQUENCE players_id_seq TO anon, authenticated;