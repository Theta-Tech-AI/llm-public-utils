CREATE TABLE learner (
    id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE
);

CREATE TABLE course (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title       text NOT NULL,
    seats_left  integer NOT NULL CHECK (seats_left >= 0),
    price_cents integer NOT NULL CHECK (price_cents >= 0),
    pass_mark   integer NOT NULL CHECK (pass_mark BETWEEN 0 AND 100),
    archived_at timestamptz
);

CREATE TABLE lesson (
    id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id uuid NOT NULL REFERENCES course(id) ON DELETE CASCADE,
    position  integer NOT NULL CHECK (position >= 1),
    title     text NOT NULL,
    UNIQUE (course_id, position)
);

CREATE TABLE enrolment (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id  uuid NOT NULL REFERENCES course(id) ON DELETE CASCADE,
    learner_id uuid NOT NULL REFERENCES learner(id) ON DELETE CASCADE,
    role       text NOT NULL CHECK (role IN ('learner', 'tutor')),
    status     text NOT NULL CHECK (status IN ('active', 'paused', 'completed')),
    expires_at timestamptz,
    UNIQUE (course_id, learner_id)
);
CREATE INDEX idx_enrolment_learner_status ON enrolment (learner_id, status);

CREATE TABLE lesson_result (
    enrolment_id uuid NOT NULL REFERENCES enrolment(id) ON DELETE CASCADE,
    lesson_id    uuid NOT NULL REFERENCES lesson(id) ON DELETE CASCADE,
    score        integer NOT NULL CHECK (score BETWEEN 0 AND 100),
    finished_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (enrolment_id, lesson_id)
);
CREATE INDEX idx_lesson_result_lesson ON lesson_result (lesson_id);

CREATE TABLE certificate (
    enrolment_id uuid PRIMARY KEY REFERENCES enrolment(id) ON DELETE CASCADE,
    issued_at    timestamptz NOT NULL DEFAULT now(),
    pdf          bytea NOT NULL
);

CREATE TABLE announcement (
    id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id uuid NOT NULL REFERENCES course(id) ON DELETE CASCADE,
    body      text NOT NULL,
    posted_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_announcement_course_posted ON announcement (course_id, posted_at DESC);

CREATE TABLE reply (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id uuid NOT NULL REFERENCES learner(id) ON DELETE CASCADE,
    body       text NOT NULL,
    posted_at  timestamptz NOT NULL DEFAULT now(),
    read_at    timestamptz
);
CREATE INDEX idx_reply_learner_posted ON reply (learner_id, posted_at DESC);

CREATE TABLE grade_notice (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id uuid NOT NULL REFERENCES learner(id) ON DELETE CASCADE,
    body       text NOT NULL,
    posted_at  timestamptz NOT NULL DEFAULT now(),
    read_at    timestamptz
);
CREATE INDEX idx_grade_notice_learner_posted ON grade_notice (learner_id, posted_at DESC);

CREATE TABLE reminder (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id   uuid NOT NULL REFERENCES learner(id) ON DELETE CASCADE,
    body         text NOT NULL,
    posted_at    timestamptz NOT NULL DEFAULT now(),
    dismissed_at timestamptz
);
CREATE INDEX idx_reminder_learner_posted ON reminder (learner_id, posted_at DESC);

CREATE TABLE waitlist (
    course_id  uuid NOT NULL REFERENCES course(id) ON DELETE CASCADE,
    learner_id uuid NOT NULL REFERENCES learner(id) ON DELETE CASCADE,
    joined_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (course_id, learner_id)
);
CREATE INDEX idx_waitlist_learner ON waitlist (learner_id);

CREATE TABLE purchase (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id  uuid NOT NULL REFERENCES course(id) ON DELETE RESTRICT,
    learner_id uuid NOT NULL REFERENCES learner(id) ON DELETE RESTRICT,
    paid_cents integer NOT NULL CHECK (paid_cents >= 0),
    paid_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_purchase_course ON purchase (course_id);
CREATE INDEX idx_purchase_learner ON purchase (learner_id);
