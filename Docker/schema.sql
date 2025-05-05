-- 1) UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2) ENUM types
CREATE TYPE accreditation_status AS ENUM ('pending','approved','revoked');
CREATE TYPE booking_status       AS ENUM ('requested','confirmed','cancelled','completed','rebooking');
CREATE TYPE payment_status       AS ENUM ('pending','paid','failed');
CREATE TYPE payment_method       AS ENUM ('card','paypal','bank_transfer','other');

-- 3) USERS
CREATE TABLE users (
  user_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  first_name      VARCHAR(50),
  last_name       VARCHAR(50),
  email_id        VARCHAR(255) UNIQUE NOT NULL,
  mobile          VARCHAR(20),
  two_factor_auth BOOLEAN DEFAULT FALSE
);

-- 4) CLINICS
CREATE TABLE clinics (
  clinic_id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  clinic_name          VARCHAR(100) NOT NULL,
  location_city        VARCHAR(50),
  location_country     VARCHAR(50),
  email_id             VARCHAR(255) UNIQUE,
  mobile               VARCHAR(20),
  address              VARCHAR(250),
  two_factor_auth      BOOLEAN DEFAULT FALSE,
  accreditation_status accreditation_status
);

-- 5) SERVICES
CREATE TABLE services (
  service_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  clinic_id    UUID NOT NULL
                REFERENCES clinics(clinic_id) ON DELETE CASCADE,
  service_name VARCHAR(100) NOT NULL,
  pricestart   DECIMAL(10,2) NOT NULL,
  priceend     DECIMAL(10,2) NOT NULL,
  currency     VARCHAR(5)     NOT NULL DEFAULT 'USD',
  description  VARCHAR(255),
  about        VARCHAR(255)
);

-- 6) DOCTORS
CREATE TABLE doctors (
  doctor_id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  clinic_id           UUID NOT NULL
                      REFERENCES clinics(clinic_id) ON DELETE CASCADE,
  service_id          UUID NOT NULL
                      REFERENCES services(service_id) ON DELETE CASCADE,
  doctor_name         VARCHAR(100) NOT NULL,
  qualification       VARCHAR(100) NOT NULL,
  years_of_experience INTEGER       DEFAULT 0,
  specialization      VARCHAR(100)
);

-- 7) WISHLISTS
CREATE TABLE wishlists (
  wishlist_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id     UUID NOT NULL
              REFERENCES users(user_id) ON DELETE CASCADE,
  clinic_id   UUID NOT NULL
              REFERENCES clinics(clinic_id) ON DELETE CASCADE,
  service     VARCHAR(100),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 8) BOOKINGS
CREATE TABLE bookings (
  booking_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id           UUID NOT NULL
                    REFERENCES users(user_id) ON DELETE CASCADE,
  clinic_id         UUID NOT NULL
                    REFERENCES clinics(clinic_id) ON DELETE CASCADE,
  service_id        UUID NOT NULL
                    REFERENCES services(service_id) ON DELETE CASCADE,
  doctor_id         UUID
                    REFERENCES doctors(doctor_id),
  appointment_start TIMESTAMPTZ NOT NULL,
  appointment_end   TIMESTAMPTZ NOT NULL,
  booking_status    booking_status NOT NULL DEFAULT 'requested',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9) REVIEWS
CREATE TABLE reviews (
  review_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id        UUID NOT NULL
                 REFERENCES users(user_id) ON DELETE CASCADE,
  clinic_id      UUID NOT NULL
                 REFERENCES clinics(clinic_id) ON DELETE CASCADE,
  service_id     UUID
                 REFERENCES services(service_id),
  doctor_id      UUID
                 REFERENCES doctors(doctor_id),
  booking_id     UUID
                 REFERENCES bookings(booking_id),
  rating         SMALLINT CHECK (rating BETWEEN 1 AND 5),
  review_comment TEXT,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10) PAYMENTS
CREATE TABLE payments (
  payment_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  booking_id          UUID NOT NULL
                      REFERENCES bookings(booking_id) ON DELETE CASCADE,
  user_id             UUID NOT NULL
                      REFERENCES users(user_id)    ON DELETE CASCADE,
  amount_paid         DECIMAL(10,2) NOT NULL,
  payment_status      payment_status NOT NULL DEFAULT 'pending',
  payment_method      payment_method NOT NULL DEFAULT 'card',
  payment_reference_id VARCHAR(100),
  paid_at             TIMESTAMPTZ,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 11) RLS Policies (example for wishlists; repeat for bookings, reviews, payments)
--ALTER TABLE wishlists ENABLE ROW LEVEL SECURITY;
--CREATE POLICY wishlists_own
--  ON wishlists FOR ALL
--  USING ( auth.uid()::UUID = user_id );

-- (similarly: bookings_own, reviews_own, payments_select for SELECT-only)
