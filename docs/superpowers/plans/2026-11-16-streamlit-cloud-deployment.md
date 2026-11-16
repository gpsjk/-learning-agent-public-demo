# Streamlit Community Cloud Public Deployment Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Publish the upgraded learning agent as an anonymously accessible Streamlit Community Cloud demo without uploading local student data or secrets.

**Architecture:** Keep the existing single-process Streamlit application and SQLite storage. When `PUBLIC_DEMO=true`, route SQLite to the system temporary directory and render a persistent privacy warning. Publish only a sanitized source tree to a private GitHub repository; Streamlit Community Cloud serves the app publicly.

**Tech Stack:** Python 3.12, Streamlit, SQLite, pytest, GitHub, Streamlit Community Cloud.

---

### Task 1: Lock public-demo safety behavior with tests

**Files:**
- Create: `tests/test_public_demo.py`
- Modify: `database.py`
- Modify: `app.py`

**Steps:**
1. Add a failing test proving `PUBLIC_DEMO=true` sends the default database outside the project tree and into the system temporary directory.
2. Add a failing Streamlit AppTest proving every public-demo page displays a warning not to upload real student names, answers, or photos.
3. Run the focused tests and confirm the expected failures.
4. Implement the smallest environment helper and banner needed to pass.
5. Run the focused tests again.

### Task 2: Make the repository cloud-safe

**Files:**
- Modify: `.streamlit/config.toml`
- Modify: `.gitignore`
- Create: `data/.gitkeep`
- Create: `.streamlit/secrets.example.toml`
- Untrack only: `data/mistakes.db`

**Steps:**
1. Remove the fixed local bind address from Streamlit configuration.
2. Ignore SQLite files and real Streamlit secrets while keeping a placeholder example.
3. Stop tracking `data/mistakes.db` without deleting the local working copy.
4. Audit tracked files for databases, `.env`, secrets, uploaded images, virtual environments, and caches.

### Task 3: Document the public deployment contract

**Files:**
- Modify: `README.md`
- Create: `部署说明-Streamlit-Cloud.md`

**Steps:**
1. Document `PUBLIC_DEMO=true`, temporary shared data, public visibility, and the privacy prohibition.
2. Document the required model settings using placeholders only.
3. Document the GitHub/Streamlit deployment fields: branch `main`, entrypoint `app.py`, Python 3.12.
4. State that the free demo is not a persistent or production student-information system.

### Task 4: Verify and commit the sanitized deployment source

**Files:** all source and test files touched above.

**Steps:**
1. Run the complete pytest suite.
2. Run `compileall`.
3. Start with `PUBLIC_DEMO=true` and verify HTTP 200 locally.
4. Re-run the tracked-file privacy audit.
5. Commit only source, tests, configuration, documentation, and the database untracking change; never stage the local database contents.

### Task 5: Publish source and deploy

**External systems:** GitHub and Streamlit Community Cloud.

**Steps:**
1. Create a private GitHub repository named `learning-agent-public-demo`.
2. Publish the sanitized source on branch `main`.
3. Create the Streamlit app using `app.py` and Python 3.12.
4. Configure `PUBLIC_DEMO="true"` and model secrets through Streamlit's Secrets UI; never commit or echo real credentials.
5. Set app visibility to public.
6. Verify the public URL, privacy warning, navigation, and image-upload entry point.

## Review Focus

- `data/mistakes.db`, `.env`, and `.streamlit/secrets.toml` are absent from tracked and published files.
- Public-demo mode uses a temporary database and never the local project database.
- No shared-password pseudo-authentication is introduced.
- The fixed `127.0.0.1` server address is removed.
- No real student photos, names, or answers are published.
- The final app is anonymously reachable and clearly marked as a temporary public demo.
