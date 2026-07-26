package com.resume.agent.model;

public class Citation {
    private String title;
    private String category;
    private String excerpt;

    public Citation() {}

    public Citation(String title, String category, String excerpt) {
        this.title = title;
        this.category = category;
        this.excerpt = excerpt;
    }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getExcerpt() { return excerpt; }
    public void setExcerpt(String excerpt) { this.excerpt = excerpt; }
}
