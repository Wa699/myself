package com.resume.agent.repository;

import com.resume.agent.model.Session;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface SessionRepository extends JpaRepository<Session, Long> {
    Optional<Session> findBySessionId(String sessionId);
}
