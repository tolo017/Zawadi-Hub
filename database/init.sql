-- Runas Zawadihub – Schema & Seed Data (Tier‑based)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    loyalty_card_number VARCHAR(20) UNIQUE NOT NULL DEFAULT substring(md5(random()::text) for 12),
    points_balance INTEGER NOT NULL DEFAULT 0,
    tier VARCHAR(20) NOT NULL DEFAULT 'bronze' CHECK (tier IN ('bronze','silver','gold','platinum')),
    total_spent NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    items JSONB NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    category VARCHAR(10) NOT NULL DEFAULT 'food' CHECK (category IN ('drink','food','combo')),
    points_earned INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    reward_description TEXT NOT NULL,
    discount_percent INTEGER NOT NULL,
    item_target VARCHAR(100),
    is_personalized BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    redeemed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE redemptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reward_id UUID NOT NULL REFERENCES rewards(id),
    redeemed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ======= SEED DATA =======
-- Password for all seed users is "password123" (bcrypt – generated with Python)
INSERT INTO customers (id, name, email, password_hash, loyalty_card_number, points_balance, tier, total_spent) VALUES
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Mango Lover', 'mango@example.com',
     '$2b$12$q6XJi.V9tOEoKXGZ6HpO1uZPq3JjLQL/Fm7J.ySfEHSH5nZqtYaAq', 'LOYAL-MANGO-1', 150, 'gold', 350.00),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Latte Fan', 'latte@example.com',
     '$2b$12$q6XJi.V9tOEoKXGZ6HpO1uZPq3JjLQL/Fm7J.ySfEHSH5nZqtYaAq', 'LOYAL-LATTE-2', 80, 'silver', 180.00),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'Combo Cruiser', 'combo@example.com',
     '$2b$12$q6XJi.V9tOEoKXGZ6HpO1uZPq3JjLQL/Fm7J.ySfEHSH5nZqtYaAq', 'LOYAL-COMBO-3', 200, 'bronze', 50.00),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a44', 'Newbie', 'newbie@example.com',
     '$2b$12$q6XJi.V9tOEoKXGZ6HpO1uZPq3JjLQL/Fm7J.ySfEHSH5nZqtYaAq', 'LOYAL-NEW-4', 10, 'bronze', 5.00);

-- Transactions for Mango Lover ( 4 x Mango Smoothie in last 12 days)
INSERT INTO transactions (id, customer_id, items, total_amount, category, points_earned, created_at) VALUES
    (uuid_generate_v4(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '["Mango Smoothie"]', 5.00, 'drink', 8, NOW() - INTERVAL '10 days'),
    (uuid_generate_v4(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '["Mango Smoothie"]', 5.00, 'drink', 8, NOW() - INTERVAL '7 days'),
    (uuid_generate_v4(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '["Mango Smoothie"]', 5.00, 'drink', 8, NOW() - INTERVAL '4 days'),
    (uuid_generate_v4(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '["Mango Smoothie"]', 5.00, 'drink', 8, NOW() - INTERVAL '1 day');

-- Transactions for Latte Fan (2x Latte + Croissant combo in 10 days)
INSERT INTO transactions (id, customer_id, items, total_amount, category, points_earned, created_at) VALUES
    (uuid_generate_v4(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '["Latte", "Croissant"]', 8.50, 'combo', 11, NOW() - INTERVAL '8 days'),
    (uuid_generate_v4(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '["Latte", "Croissant"]', 8.50, 'combo', 11, NOW() - INTERVAL '4 days');

-- Transactions for Combo Cruiser (mix)
INSERT INTO transactions (id, customer_id, items, total_amount, category, points_earned, created_at) VALUES
    (uuid_generate_v4(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', '["Latte", "Croissant"]', 8.50, 'combo', 10, NOW() - INTERVAL '20 days'),
    (uuid_generate_v4(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', '["Espresso"]', 3.00, 'drink', 3, NOW() - INTERVAL '15 days'),
    (uuid_generate_v4(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', '["Banana Bread"]', 4.00, 'food', 4, NOW() - INTERVAL '2 days');