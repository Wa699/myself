package com.resume.agent.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class PythonChatResponse {
    private String answer;
    private List<Citation> citations;

    @JsonProperty("evidence_sufficient")
    private boolean evidence_sufficient;

    @JsonProperty("duration_ms")
    private int duration_ms;

    public String getAnswer() { return answer; }
    public void setAnswer(String answer) { this.answer = answer; }

    public List<Citation> getCitations() { return citations; }
    public void setCitations(List<Citation> citations) { this.citations = citations; }

    public boolean isEvidence_sufficient() { return evidence_sufficient; }
    public void setEvidence_sufficient(boolean evidence_sufficient) { this.evidence_sufficient = evidence_sufficient; }

    public int getDuration_ms() { return duration_ms; }
    public void setDuration_ms(int duration_ms) { this.duration_ms = duration_ms; }
}
