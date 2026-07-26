package com.resume.agent.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class ChatRequest {
    private String sessionId;

    @NotBlank(message = "问题不能为空")
    @Size(max = 500, message = "问题长度不能超过500字")
    private String question;

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }
}
