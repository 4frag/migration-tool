CREATE DATABASE target;
\c target;

-- Схема 1: Библиотека
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
    membership_type VARCHAR(20) NOT NULL DEFAULT 'standard', -- Есть только в схеме 1
    fine_amount DECIMAL(10, 2) DEFAULT 0.00
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    publication_year INTEGER,
    publisher_id INTEGER, -- Есть только в схеме 1
    available_copies INTEGER DEFAULT 1,
    total_copies INTEGER DEFAULT 1
);

CREATE TABLE library_events ( -- Есть только в схеме 1
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0
);

-- Связи схемы 1
ALTER TABLE books ADD CONSTRAINT fk_books_publisher 
    FOREIGN KEY (publisher_id) REFERENCES users(id) ON DELETE SET NULL;