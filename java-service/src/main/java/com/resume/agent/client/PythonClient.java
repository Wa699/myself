package com.resume.agent.client;

import com.resume.agent.model.PythonChatRequest;
import com.resume.agent.model.PythonChatResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class PythonClient {
    private final RestTemplate restTemplate;
    private final String pythonUrl;

    public PythonClient(@Value("${python.service.url}") String pythonUrl) {
        this.restTemplate = new RestTemplate();
        this.pythonUrl = pythonUrl;
    }

    public PythonChatResponse chat(PythonChatRequest request) {
        return restTemplate.postForObject(
            pythonUrl + "/internal/ai/chat",
            request,
            PythonChatResponse.class
        );
    }
}
