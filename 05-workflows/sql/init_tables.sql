CREATE TABLE IF NOT EXISTS roles (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS locations (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS departments (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS occurred_places (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS causes (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS report_departments (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS disaster_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS injury_classifications (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS injured_parts (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  age INTEGER NOT NULL,
  role_id INTEGER REFERENCES roles(id) NOT NULL,
  department_id INTEGER REFERENCES departments(id) NOT NULL,
  phone_number VARCHAR(32),
  employment_type VARCHAR(32) NOT NULL,
  industry_experience_years INTEGER NOT NULL,
  work_qualification VARCHAR(32) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incidents (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255),
  submit_date DATE NOT NULL,
  location_id INTEGER REFERENCES locations(id) NOT NULL,
  department_id INTEGER REFERENCES departments(id) NOT NULL,
  type VARCHAR(32) NOT NULL,
  occurred_at TIMESTAMP NOT NULL,
  occurred_place_id INTEGER REFERENCES occurred_places(id) NOT NULL,
  occurred_place_detail VARCHAR(255) NOT NULL,
  cause_id INTEGER REFERENCES causes(id) NOT NULL,
  witness_id INTEGER REFERENCES users(id) NOT NULL,
  witness_manager_id INTEGER REFERENCES users(id),
  reporter_id INTEGER REFERENCES users(id) NOT NULL,
  reporter_phone_number VARCHAR(255),
  manager_id INTEGER REFERENCES users(id) NOT NULL,
  worker_id INTEGER REFERENCES users(id) NOT NULL,
  work_members VARCHAR(255) NOT NULL,
  disaster_type_id INTEGER REFERENCES disaster_types(id) NOT NULL,
  injury_classification_id INTEGER REFERENCES injury_classifications(id) NOT NULL,
  injured_part_id INTEGER REFERENCES injured_parts(id) NOT NULL,
  injury_description TEXT
);

CREATE TABLE incident_occurrences (
  id SERIAL PRIMARY KEY,
  incident_id INTEGER REFERENCES incidents(id),
  description TEXT,
  image_path VARCHAR(255)
);

-- roles table
INSERT INTO roles (name, description) VALUES
('Admin', 'Administrator role'),
('Manager', 'Manager role'),
('Employee', 'Employee role'),
('Contractor', 'Contractor role'),
('Guest', 'Guest role');

-- locations table
INSERT INTO locations (name) VALUES
('東京本社'),
('大阪支社'),
('名古屋営業所'),
('福岡支社'),
('仙台営業所');

-- departments table
INSERT INTO departments (name) VALUES
('総務部'),
('営業部'),
('技術部'),
('経理部'),
('人事部');

-- occurred_places table
INSERT INTO occurred_places (name) VALUES
('本社ビル'),
('大阪オフィス'),
('名古屋オフィス'),
('福岡オフィス'),
('仙台オフィス');

-- causes table
INSERT INTO causes (name) VALUES
('地震'),
('火災'),
('機械故障'),
('人的ミス'),
('その他');

-- report_departments table
INSERT INTO report_departments (name) VALUES
('総務部'),
('営業部'),
('技術部'),
('経理部'),
('人事部');

-- disaster_types table data
INSERT INTO disaster_types (name) VALUES
('墜落'),
('転落'),
('衝突'),
('挟まれ'),
('感電');

-- injury_classifications table data
INSERT INTO injury_classifications (name) VALUES
('骨折'),
('軽症'),
('重傷'),
('死亡');

-- injured_parts table data
INSERT INTO injured_parts (name) VALUES
('頭部'),
('顔面'),
('胸部'),
('腹部'),
('四肢');

-- users table
INSERT INTO users (name, email, age, role_id, department_id, phone_number, employment_type, industry_experience_years, work_qualification) VALUES
('佐藤 凛', 'rin.sato@example.com', 25, 1, 1, '0123456789', '直雇用', 5, 'あり'),
('鈴木 陽翔', 'hinata.suzuki@example.com', 30, 2, 2, '0987654321', '派遣', 3, 'なし'),
('田中 紬', 'tsumugi.tanaka@example.com', 28, 3, 3, '1234567890', '請負', 2, '不要'),
('高橋 蓮', 'ren.takahashi@example.com', 23, 4, 4, '2345678901', '直雇用', 1, 'あり'),
('伊藤 結菜', 'yuna.ito@example.com', 26, 5, 5, '3456789012', '派遣', 4, 'なし');

-- incidents table
INSERT INTO incidents (title, submit_date, location_id, department_id, type, occurred_at, occurred_place_id, occurred_place_detail, cause_id, witness_id, witness_manager_id, reporter_id, reporter_phone_number, manager_id, worker_id, work_members, disaster_type_id, injury_classification_id, injured_part_id, injury_description) VALUES
('東京本社火災', '2023-01-01', 1, 1, '災害', '2023-01-01 00:00:00', 1, '本社ビル', 1, 1, 2, 1, '0123456789', 2, 1, '佐藤 凛', 1, 1, 1, '軽度のやけど'),
('大阪支社機械故障', '2023-01-02', 2, 2, '事故', '2023-01-02 00:00:00', 2, '大阪オフィス', 2, 2, 3, 2, '0987654321', 3, 2, '鈴木 陽翔, 田中 紬', 2, 2, 2, '骨折'),
('名古屋営業所ヒヤリハット', '2023-01-03', 3, 3, '重大ヒヤリハット', '2023-01-03 00:00:00', 3, '名古屋オフィス', 3, 3, 4, 3, '1234567890', 4, 3, '高橋 蓮', 3, 4, 3, NULL),
('福岡支社地震', '2023-01-04', 4, 4, '災害', '2023-01-04 00:00:00', 4, '福岡オフィス', 4, 4, 5, 4, '2345678901', 5, 4, '伊藤 結菜, 佐藤 凛', 3, 1, 3, '打撲'),
('仙台営業所火災', '2023-01-05', 5, 5, '事故', '2023-01-05 00:00:00', 5, '仙台オフィス', 5, 5, 1, 5, '3456789012', 1, 5, '鈴木 陽翔', 1, 2, 4, 'やけど');

-- incident_occurrences table
INSERT INTO incident_occurrences (incident_id, description, image_path) VALUES
(1, '出火場所は本社ビルの3階です。', 'image1.png'),
(2, '機械が突然停止し、作業員が巻き込まれました。', 'image2.jpg'),
(3, '棚が倒れ、作業員が下敷きになりました。', 'image3.jpeg'),
(4, '地震により棚が倒れ、作業員が下敷きになりました。', 'image4.jpeg'),
(5, '出火場所は仙台オフィスの2階です。', 'image5.png');
