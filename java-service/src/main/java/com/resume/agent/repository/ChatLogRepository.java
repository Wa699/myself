package com.resume.agent.repository;

import com.resume.agent.model.ChatLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ChatLogRepository extends JpaRepository<ChatLog, Long> {
    List<ChatLog> findBySessionIdOrderByCreatedAtAsc(String sessionId);
}
