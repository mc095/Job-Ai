
```
Agentic-Job-AI
├─ ai_job_helper
│  ├─ accounts
│  │  ├─ admin.py
│  │  ├─ apps.py
│  │  ├─ forms.py
│  │  ├─ migrations
│  │  │  ├─ 0001_initial.py
│  │  │  ├─ 0002_auto_20250811_2352.py
│  │  │  ├─ 0003_auto_20250910_1837.py
│  │  │  └─ __init__.py
│  │  ├─ models.py
│  │  ├─ urls.py
│  │  ├─ views.py
│  │  └─ __init__.py
│  ├─ ai_agents
│  │  ├─ agno_agent.py
│  │  ├─ ai_service.py
│  │  ├─ gemini_agent.py
│  │  ├─ management
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ ai_job_helper
│  │  ├─ asgi.py
│  │  ├─ resume
│  │  │  └─ static
│  │  │     └─ resume
│  │  │        ├─ css
│  │  │        └─ js
│  │  ├─ settings.py
│  │  ├─ urls.py
│  │  ├─ wsgi.py
│  │  └─ __init__.py
│  ├─ analysis
│  │  ├─ admin.py
│  │  ├─ apps.py
│  │  ├─ forms.py
│  │  ├─ migrations
│  │  │  ├─ 0001_initial.py
│  │  │  ├─ 0002_analysisresult.py
│  │  │  ├─ 0003_agentmemory.py
│  │  │  └─ __init__.py
│  │  ├─ models.py
│  │  ├─ urls.py
│  │  ├─ views.py
│  │  └─ __init__.py
│  ├─ ats
│  │  ├─ admin.py
│  │  ├─ apps.py
│  │  ├─ forms.py
│  │  ├─ migrations
│  │  │  ├─ 0001_initial.py
│  │  │  └─ __init__.py
│  │  ├─ models.py
│  │  ├─ services.py
│  │  ├─ templatetags
│  │  │  ├─ ats_filters.py
│  │  │  └─ __init__.py
│  │  ├─ urls.py
│  │  ├─ views.py
│  │  └─ __init__.py
│  ├─ exam
│  │  ├─ admin.py
│  │  ├─ apps.py
│  │  ├─ forms.py
│  │  ├─ migrations
│  │  │  ├─ 0001_initial.py
│  │  │  ├─ 0002_answer_is_correct.py
│  │  │  ├─ 0003_question_explanation.py
│  │  │  └─ __init__.py
│  │  ├─ models.py
│  │  ├─ signals.py
│  │  ├─ urls.py
│  │  ├─ views.py
│  │  └─ __init__.py
│  ├─ interview
│  │  ├─ admin.py
│  │  ├─ apps.py
│  │  ├─ migrations
│  │  │  ├─ 0001_initial.py
│  │  │  └─ __init__.py
│  │  ├─ models.py
│  │  ├─ urls.py
│  │  ├─ views.py
│  │  └─ __init__.py
│  ├─ manage.py
│  ├─ media
│  │  └─ profiles
│  │     ├─ photos
│  │     │  └─ 1755830015892.jpeg
│  │     └─ resumes
│  │        ├─ ganesh_resume.pdf
│  │        ├─ ganesh_resume_cHpn36w.pdf
│  │        ├─ ganesh_resume_jjEpO8R.pdf
│  │        ├─ ganesh_resume_m0yKvBY.pdf
│  │        ├─ ganesh_resume_wk9RHA8.pdf
│  │        ├─ ganesh_resume_x6p4KNF.pdf
│  │        ├─ Manikanta_Sairam_Adapa.docx
│  │        └─ Manikanta_Sairam_Adapa_hy1LczH.docx
│  ├─ portfolio
│  │  ├─ admin.py
│  │  ├─ apps.py
│  │  ├─ forms.py
│  │  ├─ migrations
│  │  │  ├─ 0001_initial.py
│  │  │  ├─ 0002_auto_20250913_1005.py
│  │  │  └─ __init__.py
│  │  ├─ models.py
│  │  ├─ portfolio_generator.py
│  │  ├─ tests.py
│  │  ├─ urls.py
│  │  ├─ views.py
│  │  └─ __init__.py
│  ├─ resume
│  │  ├─ admin.py
│  │  ├─ apps.py
│  │  ├─ forms.py
│  │  ├─ management
│  │  │  └─ commands
│  │  ├─ migrations
│  │  │  ├─ 0001_initial.py
│  │  │  └─ __init__.py
│  │  ├─ models.py
│  │  ├─ services.py
│  │  ├─ static
│  │  │  └─ resume
│  │  │     ├─ css
│  │  │     │  └─ builder.css
│  │  │     └─ js
│  │  ├─ urls.py
│  │  ├─ views.py
│  │  └─ __init__.py
│  ├─ templates
│  │  ├─ accounts
│  │  │  └─ profile.html
│  │  ├─ analysis
│  │  │  └─ home.html
│  │  ├─ ats
│  │  │  └─ home.html
│  │  ├─ base.html
│  │  ├─ exam
│  │  │  ├─ error.html
│  │  │  ├─ home.html
│  │  │  ├─ loading.html
│  │  │  ├─ result.html
│  │  │  └─ test.html
│  │  ├─ home.html
│  │  ├─ interview
│  │  │  ├─ chat.html
│  │  │  ├─ error.html
│  │  │  └─ home.html
│  │  ├─ portfolio
│  │  │  ├─ create.html
│  │  │  ├─ dashboard.html
│  │  │  └─ select_template.html
│  │  ├─ registration
│  │  │  ├─ login.html
│  │  │  └─ signup.html
│  │  ├─ resume
│  │  │  └─ builder.html
│  │  └─ training
│  │     ├─ chat.html
│  │     ├─ error.html
│  │     └─ home.html
│  └─ training
│     ├─ admin.py
│     ├─ apps.py
│     ├─ migrations
│     │  ├─ 0001_initial.py
│     │  └─ __init__.py
│     ├─ models.py
│     ├─ urls.py
│     ├─ views.py
│     └─ __init__.py
├─ README.md
└─ requirements.txt

```