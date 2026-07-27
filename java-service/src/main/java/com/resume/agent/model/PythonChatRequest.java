package com.resume.agent.model;

import java.util.List;
import java.util.Map;

public class PythonChatRequest {
    private String question;
    private List<Map<String, String>> history;

    public PythonChatRequest() {}

    public PythonChatRequest(String question) {
        this.question = question;
    }

    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }

    public List<Map<String, String>> getHistory() { return history; }
    public void setHistory(List<Map<String, String>> history) { this.history = history; }
}
