CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    genre_id INT REFERENCES genres(id),
    duration_minutes INT NOT NULL,
    release_date DATE,
    rating NUMERIC(3,1),
    poster_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS halls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    rows_count INT,
    seats_per_row INT
);
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    movie_id INT REFERENCES movies(id),
    hall_id INT REFERENCES halls(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sessions_start ON sessions (start_time);
CREATE INDEX IF NOT EXISTS idx_sessions_movie ON sessions (movie_id);

CREATE TABLE IF NOT EXISTS seats (
    id SERIAL PRIMARY KEY,
    hall_id INT REFERENCES halls(id),
    row_num INT NOT NULL,
    seat_num INT NOT NULL,
    seat_type VARCHAR(50) DEFAULT 'standard'
);
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    password_hash TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'customer',
    registered_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    seat_id INT REFERENCES seats(id),
    user_id INT REFERENCES users(id),
    booking_code UUID DEFAULT gen_random_uuid(),
    status VARCHAR(50) NOT NULL DEFAULT 'available',
    price DECIMAL(10,2) NOT NULL,
    booked_at TIMESTAMP,
    paid_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_tickets_session_status ON tickets (session_id, status);
CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets (user_id);

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    ticket_id INT REFERENCES tickets(id),
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE tickets ADD CONSTRAINT unique_session_seat UNIQUE (session_id, seat_id);
