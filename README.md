# ☁️ Cloud Storage API

A Google-Drive-style file & folder storage backend built with **FastAPI** — with user accounts, nested folders, file management, and granular per-user sharing permissions (read/edit), all backed by **PostgreSQL**.

🔗 **Live demo:** [cloud-storage-app-vsgf.onrender.com](https://cloud-storage-app-vsgf.onrender.com)

---

## 🎯 Why I built this

This is a learning project. I wanted to properly learn **FastAPI**, relational database design, and backend authorization/security concepts by building something with real complexity — not just a CRUD toy. A Drive clone forces you to deal with things like:

- hierarchical data (folders inside folders inside folders)
- permission inheritance (if I share a folder with you, do you get my files inside it too?)
- authorization bugs that are easy to get wrong (IDOR, trusting client-supplied IDs, etc.)

So instead of a tutorial project, I designed the schema myself, made (and broke, and fixed) my own architectural decisions, and tested the authorization logic until it held up.

---

## 🧠 What it does

- 🔐 **Auth** — signup/login with hashed passwords (Argon2) and JWT-based sessions
- 📁 **Folders** — create, rename, move, delete, nested to any depth
- 📄 **Files** — create, rename, move, delete, scoped to folders or the root
- 🤝 **Sharing** — share a folder or file with another user as `READ` or `EDIT`
- 🪜 **Permission inheritance** — sharing a folder grants access to everything inside it; access is resolved by checking the resource itself, then walking up its parent chain
- 🛡️ **Authorization hardening** — every resource lookup is scoped by both ID *and* ownership/access (no IDOR), with generic 404s instead of 403s to avoid leaking resource existence
- ✅ **56 automated tests** covering auth, CRUD, ownership, sharing, inheritance, cascade deletes, and circular-folder-hierarchy prevention

---

## 🖥️ Frontend

The `app/static/` folder has a minimal single-page frontend (login/register + file & folder browser) so the API is actually usable in a browser, not just through Swagger docs.

> **Note:** the frontend was *vibecoded* — every line was written by me, but with heavy guidance and pairing from Claude (AI). The backend (schema, models, routes, auth, permission logic) was designed and written by me on my own, with Claude acting strictly as a reviewer/teacher, not a code generator.

---

## 🏗️ Tech stack

| Layer          | Tech                                      |
|----------------|--------------------------------------------|
| Framework      | [FastAPI](https://fastapi.tiangolo.com/)   |
| Database       | PostgreSQL                                 |
| ORM            | SQLAlchemy 2.0 (declarative, typed)        |
| Validation     | Pydantic v2                                |
| Auth           | JWT (`python-jose`) + Argon2 password hashing |
| Testing        | Pytest + FastAPI `TestClient`              |
| Deployment     | Docker + Render                            |
| Frontend       | Vanilla HTML/CSS/JS (no framework)         |

---

## 📂 Project structure

```
Cloud_Project/
├── app/
│   ├── main.py              # FastAPI app, router registration, health check
│   ├── database.py          # SQLAlchemy engine/session setup
│   ├── security.py          # JWT creation + current-user dependency
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── users.py
│   │   ├── folders.py
│   │   ├── files.py
│   │   ├── foldershare.py
│   │   └── fileshare.py
│   ├── schemas/               # Pydantic request/response schemas
│   ├── routers/                # API route handlers
│   │   ├── users.py
│   │   ├── folders.py
│   │   └── files.py
│   └── static/                # Frontend (served at "/")
├── First_Init.sql            # Raw SQL schema
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🔑 Core design decisions

- **Folders are a self-referencing tree** (`parent_folder_id`) rather than a materialized path — simpler to reason about, at the cost of needing a walk-up for permission checks.
- **Sharing is modeled as separate `FileShare` / `FolderShare` junction tables** rather than one polymorphic table — trades a bit of duplication for much simpler, type-safe queries.
- **Permission resolution:** check the resource's own share first → if none, walk up the folder ancestry → first match wins → deny once the root is reached with no match.
- **Ownership is enforced server-side, never trusted from the client** — every write checks `resource.user_id == current_user.id` or runs it through the permission-check helper; nothing is authorized by a client-supplied ID alone.

---

## 🚀 Running it locally

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd Cloud_Project

# 2. Set up environment variables (see .env.example)
cp .env.example .env

# 3. Start Postgres + the API with Docker
docker compose up --build

# App will be available at:
# http://localhost:8000        (frontend)
# http://localhost:8000/docs   (Swagger UI)
```

---

## 🧪 Running tests

```bash
pytest
```

All 56 tests should pass — covering authentication, folder/file CRUD, ownership boundaries, sharing, permission inheritance, and cascade deletion.

---

## 📌 Known limitations (v1, by design)

- No soft-delete/trash — deletes cascade immediately at the database level
- Only the resource **owner** can create/manage shares (an EDIT-permission holder can't re-share)
- `GET /folders` and `GET /files` list owned + *directly*-shared resources — inheritance via an ancestor's share isn't reflected in the listing yet, only in access checks
- No dedicated password-change flow

---

## 👤 Author

Built by **Mohamed Amine Menouer** — CS student (cybersecurity focus) at Al Akhawayn University, as a learning project to get hands-on with FastAPI, relational schema design, and backend security fundamentals.
