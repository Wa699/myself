package com.resume.agent.config;

import com.resume.agent.model.ChatResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import java.util.List;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ChatResponse> handleValidation(MethodArgumentNotValidException ex) {
        ChatResponse resp = new ChatResponse();
        String msg = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getDefaultMessage())
            .findFirst().orElse("请求参数有误");
        resp.setAnswer(msg);
        resp.setCitations(List.of());
        resp.setEvidenceSufficient(false);
        return ResponseEntity.badRequest().body(resp);
    }
}
