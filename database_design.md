# Phase 2: Database Design - MBSTU CP Ranking System

## Normalization (3NF)
- **1NF**: Atomic values.
- **2NF**: No partial dependencies (Attributes depend on the whole PK).
- **3NF**: No transitive dependencies (Attributes depend only on the PK).

## Schema Definition

```sql
-- Departments & Batches (Lookup Tables)
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    short_code VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_number INT NOT NULL UNIQUE
);

-- Core Student Table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(15) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    dept_id INT NOT NULL,
    batch_id INT NOT NULL,
    section CHAR(1),
    profile_pic VARCHAR(255),
    github_url VARCHAR(255),
    linkedin_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    website_url VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(id) ON DELETE RESTRICT,
    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE RESTRICT
);

-- Platform Definitions
CREATE TABLE cp_platforms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    api_base_url VARCHAR(255)
);

-- Accounts mapping
CREATE TABLE student_cp_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    platform_id INT NOT NULL,
    username VARCHAR(100) NOT NULL,
    last_synced_at TIMESTAMP NULL,
    UNIQUE KEY unique_student_platform (student_id, platform_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (platform_id) REFERENCES cp_platforms(id) ON DELETE CASCADE
);

-- Historical Model for Stats (Time-Series)
CREATE TABLE cp_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    total_solved INT NOT NULL,
    current_rating INT NOT NULL,
    max_rating INT NOT NULL,
    contest_count INT NOT NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES student_cp_accounts(id) ON DELETE CASCADE,
    INDEX idx_history_lookup (account_id, captured_at)
);

-- Snapshot Table (For performance in Rankings)
CREATE TABLE cp_current_stats (
    account_id INT PRIMARY KEY,
    total_solved INT DEFAULT 0,
    current_rating INT DEFAULT 0,
    max_rating INT DEFAULT 0,
    contest_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES student_cp_accounts(id) ON DELETE CASCADE
);

-- Achievements & Certificates
CREATE TABLE achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE,
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE certifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    organization VARCHAR(100),
    issue_date DATE,
    verification_url VARCHAR(255),
    image_path VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
```

## Indexing Strategy
- `students(email)`, `students(student_id)`: B-Tree unique index for O(log n) lookups.
- `cp_history(account_id, captured_at)`: Composite index for range queries (progress charts).
- `cp_current_stats(current_rating DESC)`: To keep ranking queries fast.
