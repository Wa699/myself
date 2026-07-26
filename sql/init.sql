-- ============================================================
-- Personal Resume Q&A Agent - MySQL Init Schema
-- Auto-executed on first container startup
-- ============================================================

CREATE DATABASE IF NOT EXISTS resume_agent
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE resume_agent;

-- Session table: tracks anonymous visitor sessions
CREATE TABLE IF NOT EXISTS session (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id  VARCHAR(36)  NOT NULL UNIQUE,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chat log table: records every Q&A interaction
CREATE TABLE IF NOT EXISTS chat_log (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id   VARCHAR(36)  NOT NULL,
    question     TEXT         NOT NULL,
    answer       TEXT,
    status       VARCHAR(20)  NOT NULL DEFAULT 'success',
    duration_ms  INT,
    error_summary VARCHAR(500),
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at),
    CONSTRAINT fk_chat_log_session
        FOREIGN KEY (session_id) REFERENCES session(session_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
