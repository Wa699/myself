package com.resume.agent.service;

import com.resume.agent.client.PythonClient;
import com.resume.agent.model.*;
import com.resume.agent.repository.ChatLogRepository;
import com.resume.agent.repository.SessionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class ChatService {
    private final SessionRepository sessionRepository;
    private final ChatLogRepository chatLogRepository;
    private final PythonClient pythonClient;

    private static final int MAX_HISTORY_ROUNDS = 20;

    public ChatService(SessionRepository sessionRepository, ChatLogRepository chatLogRepository, PythonClient pythonClient) {
        this.sessionRepository = sessionRepository;
        this.chatLogRepository = chatLogRepository;
        this.pythonClient = pythonClient;
    }

    @Transactional
    public ChatResponse processQuestion(ChatRequest request) {
        // 1. Get or create session
        String sessionId = request.getSessionId();
        if (sessionId == null || sessionId.isEmpty()) {
            sessionId = UUID.randomUUID().toString();
        }
        final String finalSessionId = sessionId;
        sessionRepository.findBySessionId(sessionId).orElseGet(() -> {
            Session s = new Session();
            s.setSessionId(finalSessionId);
            return sessionRepository.save(s);
        });

        // 2. Fetch conversation history from DB
        List<ChatLog> recentLogs = chatLogRepository.findBySessionIdOrderByCreatedAtAsc(finalSessionId);
        List<Map<String, String>> history = new ArrayList<>();
        int start = Math.max(0, recentLogs.size() - MAX_HISTORY_ROUNDS * 2);
        for (int i = start; i < recentLogs.size(); i++) {
            ChatLog log = recentLogs.get(i);
            Map<String, String> userMsg = new HashMap<>();
            userMsg.put("role", "user");
            userMsg.put("content", log.getQuestion());
            history.add(userMsg);

            Map<String, String> assistantMsg = new HashMap<>();
            assistantMsg.put("role", "assistant");
            assistantMsg.put("content", log.getAnswer());
            history.add(assistantMsg);
        }

        // 3. Call Python service with history
        PythonChatRequest pyReq = new PythonChatRequest(request.getQuestion());
        pyReq.setHistory(history);
        PythonChatResponse pyResp;
        ChatLog log = new ChatLog();
        log.setSessionId(finalSessionId);
        log.setQuestion(request.getQuestion());

        try {
            pyResp = pythonClient.chat(pyReq);
        } catch (Exception e) {
            log.setStatus("error");
            log.setErrorSummary(truncate(e.getMessage(), 500));
            chatLogRepository.save(log);

            ChatResponse resp = new ChatResponse();
            resp.setSessionId(finalSessionId);
            resp.setAnswer("服务暂不可用，请稍后重试");
            resp.setCitations(List.of());
            resp.setEvidenceSufficient(false);
            resp.setDurationMs(0);
            return resp;
        }

        // 3. Build response
        ChatResponse resp = new ChatResponse();
        resp.setSessionId(finalSessionId);
        resp.setAnswer(pyResp.getAnswer());
        resp.setCitations(pyResp.getCitations() != null ? pyResp.getCitations() : List.of());
        resp.setEvidenceSufficient(pyResp.isEvidence_sufficient());
        resp.setDurationMs(pyResp.getDuration_ms());

        // 4. Log
        log.setAnswer(pyResp.getAnswer());
        log.setStatus(pyResp.isEvidence_sufficient() ? "success" : "insufficient_data");
        log.setDurationMs(pyResp.getDuration_ms());
        chatLogRepository.save(log);

        return resp;
    }

    private String truncate(String s, int maxLen) {
        return s != null && s.length() > maxLen ? s.substring(0, maxLen) : s;
    }
}
