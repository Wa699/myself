package com.resume.agent.config;

import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import java.io.IOException;
import java.util.concurrent.ConcurrentHashMap;

@Component
@Order(1)
public class RateLimitFilter implements Filter {
    private final ConcurrentHashMap<String, RateLimitEntry> requestCounts = new ConcurrentHashMap<>();

    @Value("${resume.rate-limit.max-requests-per-minute}")
    private int maxRequestsPerMinute;

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;
        HttpServletResponse response = (HttpServletResponse) res;

        String ip = request.getRemoteAddr();
        long now = System.currentTimeMillis();

        RateLimitEntry entry = requestCounts.compute(ip, (k, v) -> {
            if (v == null || now - v.windowStart > 60000) {
                return new RateLimitEntry(now, 1);
            }
            v.count++;
            return v;
        });

        if (entry.count > maxRequestsPerMinute) {
            response.setStatus(429);
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write("{\"answer\":\"请求过于频繁，请稍后再试\",\"citations\":[],\"sessionId\":null,\"evidenceSufficient\":false,\"durationMs\":0}");
            return;
        }

        chain.doFilter(req, res);
    }

    private static class RateLimitEntry {
        long windowStart;
        int count;
        RateLimitEntry(long ws, int c) { windowStart = ws; count = c; }
    }
}
