CREATE DATABASE reference;
\c reference;

-- Схема 2: Автопрокат
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
    driver_license_number VARCHAR(50) UNIQUE NOT NULL, -- Есть только в схеме 2
    credit_score INTEGER DEFAULT 700
);

CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    manufacture_year INTEGER,
    daily_rate DECIMAL(10, 2) NOT NULL, -- Есть только в схеме 2
    mileage INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'available'
);

CREATE TABLE insurance_plans ( -- Есть только в схеме 2
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL,
    coverage_amount DECIMAL(12, 2) NOT NULL,
    deductible DECIMAL(10, 2) DEFAULT 500.00,
    daily_cost DECIMAL(8, 2) NOT NULL
);

-- Связи схемы 2 (нет явных внешних ключей между этими таблицами)