--This is the first draft for the sql tables
--Project: Cloud Storage Project
--Name: Menouer Mohamed Amine

DROP DATABASE IF EXISTS drive;
CREATE DATABASE drive;
\c drive

CREATE TABLE users(
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(200) NOT NULL,

    CONSTRAINT uq_username
    UNIQUE (username),

    CONSTRAINT uq_email
    UNIQUE (email)
);

CREATE TABLE folder(
    folder_id SERIAL PRIMARY KEY, 
    folder_name VARCHAR(100) NOT NULL,
    parent_folder_id INT,
    user_id INT NOT NULL,

    CONSTRAINT fk_parent_folder
    FOREIGN KEY (parent_folder_id)
    REFERENCES folder(folder_id)
    ON DELETE CASCADE,

    CONSTRAINT fk_user_id
    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE,

    CONSTRAINT uq_folder_name
    UNIQUE (user_id, parent_folder_id, folder_name)
);

CREATE UNIQUE INDEX uq_root_folder_name
ON folder(user_id, folder_name)
WHERE parent_folder_id IS NULL;

CREATE TABLE files(
    file_id SERIAL PRIMARY KEY,
    file_name VARCHAR(100) NOT NULL,
    file_size INT NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    folder_id INT,
    user_id INT NOT NULL,

    CONSTRAINT uq_file_name
    UNIQUE (user_id, folder_id, file_name),

    CONSTRAINT fk_folder
    FOREIGN KEY (folder_id)
    REFERENCES folder(folder_id)
    ON DELETE CASCADE,

    CONSTRAINT fk_user_id_file
    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE,

    CONSTRAINT chk_size
    CHECK(file_size>=0)
);

CREATE UNIQUE INDEX uq_root_file_name
ON files(user_id, file_name)
WHERE folder_id IS NULL;

CREATE TYPE perm_type AS ENUM (
    'read',
    'edit',
    'no access'
);

CREATE TABLE foldershare(
    folder_id INT,
    to_user_id INT,
    permission perm_type NOT NULL,

    CONSTRAINT fk_folder_share
    FOREIGN KEY (folder_id)
    REFERENCES folder(folder_id)
    ON DELETE CASCADE,

    CONSTRAINT fk_user_foldershare
    FOREIGN KEY (to_user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE,

    CONSTRAINT pk_fldr_share
    PRIMARY KEY(folder_id, to_user_id)
);

CREATE TABLE fileshare(
    file_id INT,
    to_user_id INT,
    permission perm_type NOT NULL,

    CONSTRAINT fk_file_share
    FOREIGN KEY (file_id)
    REFERENCES files(file_id)
    ON DELETE CASCADE,

    CONSTRAINT fk_user_fileshare
    FOREIGN KEY (to_user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE,

    CONSTRAINT pk_file_share
    PRIMARY KEY(file_id, to_user_id)
);

CREATE INDEX ON folder(parent_folder_id);
CREATE INDEX ON folder(user_id);
CREATE INDEX ON files(folder_id);
CREATE INDEX ON files(user_id);
CREATE INDEX ON foldershare(to_user_id);
CREATE INDEX ON fileshare(to_user_id);









