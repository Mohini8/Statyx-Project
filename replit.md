# Statyx AI

## Overview

Statyx AI is a modern research and data analysis SaaS platform. It uses a **hybrid architecture**:
- **React + Vite** frontend for landing page, authentication, dashboard layout/navigation
- **Streamlit (Python)** as the core analytics engine, embedded inside React via iframe through a reverse proxy

## Architecture

### Services

| Service | Port | Path | Purpose |
|---------|------|------|---------|
| React Frontend | 23845 | `/` | Landing page, auth, dashboard shell |
| Express API | 8080 | `/api`, `/streamlit` | REST API + Streamlit reverse proxy |
| Streamlit Analytics | 8501 | `/streamlit` (proxied) | Analytics engine (upload, clean, stats, viz, reports) |

### Integration Pattern
- React calls `/api/streamlit-url` to get the Streamlit URL
- React embeds Streamlit via `<iframe src="/streamlit?page=upload">` etc.
- Each dashboard sub-route passes a `?page=<module>` query param to show the right Streamlit page
- The Express server proxies `/streamlit/*` to `localhost:8501` (Streamlit)
- React provides the persistent sidebar/topbar; Streamlit fills the content area

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **Frontend**: React 18, Vite, TailwindCSS v4, Framer Motion, Wouter
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Analytics**: Streamlit 1.41, Pandas, NumPy, Plotly, SciPy, scikit-learn
- **Reports**: ReportLab (PDF), python-docx (Word)
- **Auth**: bcryptjs + express-session (cookie-based)

## Folder Structure

```
artifacts/
  api-server/         Express API + Streamlit proxy
  statyx-ai/          React frontend (landing, auth, dashboard)
  streamlit-app/      Python analytics engine
    app.py            Main entry with page routing (?page=)
    pages/            Upload, Cleaning, Statistics, Visualizations, AI_Analysis, Cross_Tabulation, Reports
    services/         Dataset_Service, Statistics_Service, AI_Service, Report_Service, Cleaning_Service
    utils/            Dataframe_Utils, Column_Utils, File_Utils
    assets/Styles.css Custom CSS matching React design

lib/
  api-spec/           OpenAPI spec (source of truth)
  api-client-react/   Generated React Query hooks
  api-zod/            Generated Zod validation schemas
  db/                 Drizzle ORM schema (users, datasets tables)
```

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes
- `pnpm --filter @workspace/api-server run dev` — run API server locally

## Streamlit Pages

Navigate via `?page=<name>`:
- `upload` — CSV/Excel upload + data preview
- `clean` — Missing values, duplicates, type conversion, drop columns
- `statistics` — Descriptive stats, correlation matrix, statistical tests (t-test, ANOVA, chi-square, normality)
- `visualizations` — Bar, line, scatter, histogram, box, violin, pie, heatmap, scatter matrix
- `ai-analysis` — Auto-generated insights from data profiling
- `cross-tabulation` — Cross tabs + pivot tables
- `reports` — Download PDF or Word report

## Authentication

- Session-based auth via `express-session`
- Passwords hashed with bcryptjs
- `POST /api/auth/register` — create account
- `POST /api/auth/login` — login, sets session cookie
- `POST /api/auth/logout` — destroy session
- `GET /api/auth/me` — get current user (protected)

## Database Schema

- `users` — id, name, email, password_hash, created_at
- `datasets` — id, user_id, name, file_name, file_path, file_size, row_count, column_count, status, uploaded_at
