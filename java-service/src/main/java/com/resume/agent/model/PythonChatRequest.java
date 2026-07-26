package com.resume.agent.model;

public class PythonChatRequest {
    private String question;

    public PythonChatRequest() {}

    public PythonChatRequest(String question) {
        this.question = question;
    }

    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }
}
