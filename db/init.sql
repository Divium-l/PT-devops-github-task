CREATE TABLE emails (
    email_id INT PRIMARY KEY,
    email VARCHAR(255)         
);
CREATE SEQUENCE email_id_seq OWNED BY emails.email_id;
ALTER TABLE emails ALTER COLUMN email_id SET DEFAULT nextval('email_id_seq');

CREATE TABLE phones (
    phone_id INT PRIMARY KEY,
    phone VARCHAR(24)
);
CREATE SEQUENCE phone_id_seq OWNED BY phones.phone_id;
ALTER TABLE phones ALTER COLUMN phone_id SET DEFAULT nextval('phone_id_seq');

INSERT INTO emails (email_id, email) VALUES 
    (DEFAULT, 'generated_1@email.me'), 
    (DEFAULT, 'generated_2@email.me');

INSERT INTO phones (phone_id, phone) VALUES 
    (DEFAULT, '8 800 555 35 35'), 
    (DEFAULT, '+7 911 228 14 87');