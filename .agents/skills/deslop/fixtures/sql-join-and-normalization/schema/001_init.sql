CREATE TABLE customer (
    id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email   text NOT NULL,
    address text NOT NULL
);

CREATE TABLE project (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id uuid NOT NULL REFERENCES customer(id) ON DELETE CASCADE,
    name        text NOT NULL
);

-- PLANTED: project_id has no index (join + parent delete scan the child)
-- PLANTED: created_by is a bare uuid with no REFERENCES
-- PLANTED: tags is a comma-joined list (1NF)
-- PLANTED: total_tokens is maintained by application code (single source of truth)
CREATE TABLE document (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id   uuid NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    created_by   uuid,
    tags         text,
    total_tokens integer,
    created_at   timestamptz NOT NULL DEFAULT now()
);

-- PLANTED: customer_email/address copied from customer (3NF)
CREATE TABLE sales_order (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id      uuid NOT NULL REFERENCES customer(id),
    customer_email   text NOT NULL,
    customer_address text NOT NULL,
    amount           numeric NOT NULL
);

-- LEGITIMATE, must be declined: a generated column is the database owning its own derivation
CREATE TABLE document_metrics (
    document_id  uuid PRIMARY KEY REFERENCES document(id) ON DELETE CASCADE,
    input_tokens integer NOT NULL DEFAULT 0,
    output_tokens integer NOT NULL DEFAULT 0,
    total        integer GENERATED ALWAYS AS (input_tokens + output_tokens) STORED
);
