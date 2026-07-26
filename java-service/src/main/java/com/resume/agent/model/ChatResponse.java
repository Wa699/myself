package com.resume.agent.model;

import java.util.List;

public class ChatResponse {
    private String sessionId;
    private String answer;
    private List<Citation> citations;
    private boolean evidenceSufficient;
    private long durationMs;

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public String getAnswer() { return answer; }
    public void setAnswer(String answer) { this.answer = answer; }

    public List<Citation> getCitations() { return citations; }
    public void setCitations(List<Citation> citations) { this.citations = citations; }

    public boolean isEvidenceSufficient() { return evidenceSufficient; }
    public void setEvidenceSufficient(boolean evidenceSufficient) { this.evidenceSufficient = evidenceSufficient; }

    public long getDurationMs() { return durationMs; }
    public void setDurationMs(long durationMs) { this.durationMs = durationMs; }
}
