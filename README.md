  📝 Note Storing Application (FastAPI + MongoDB)
A secure, full-stack Note Storing Web Application built using FastAPI, MongoDB, Jinja2, and HTML/CSS.
Users can create, view, edit, delete, and summarize notes using Google Gemini AI, with authentication handled via JWT tokens stored in HTTP-only cookies.

Features
🔐 Authentication & User Management
    User registration with validation
    Secure password hashing using bcrypt
    Login & logout functionality
    JWT-based authentication
    HTTP-only cookies for session security
    Change password feature with strength validation
🗒️ Notes Management (CRUD)
    Create new notes
    View all notes on dashboard
    View individual note details
    Edit existing notes
    Delete notes
    Each user has isolated personal notes storage
🤖 AI-Powered Note Summarization
    Uses Google Gemini API
    Generates summaries under 150 words
    Helps users quickly understand long notes
🖥️ Server-Side Rendering
    Jinja2 templates
    HTML & CSS only (no JavaScript frontend)
    Clean separation of templates and static files
    
## 🛠️ Tech Stack

| Layer                 | Technology                    |
| --------------------- | ----------------------------- |
| Backend               | FastAPI                       |
| Database              | MongoDB                       |
| Templating            | Jinja2                        |
| Authentication        | JWT (JSON Web Tokens)         |
| Password Hashing      | Custom hashing module (bcrypt)|
| AI Integration        | Google Gemini API             |
| Environment Variables | python-dotenv                 |
    
🔐 Security Practices
    Passwords are never stored in plain text
    Secure hashing for all passwords
    JWT tokens used for authentication
    Tokens stored in HTTP-only cookies
    Unauthorized access redirects to login
    Per-user database collections prevent data leakage
    Password strength validation enforced
📄 License
    This project is licensed under the MIT License.
    MIT License
      Copyright (c) 2025
      
      Permission is hereby granted, free of charge, to any person obtaining a copy
      of this software and associated documentation files...
👨‍💻 Author
    
    Masud Mallik
    Backend Developer | FastAPI | MongoDB

