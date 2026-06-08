# CLAUDE.md — Next.js 15 + SQLite SaaS

Opinionated, production-ready CLAUDE.md template for a typical SaaS project
built with Next.js 15 App Router and SQLite.

**Bounty #2: $75 — claude-builders-bounty/claude-builders-bounty**

## Quick Install

```bash
# 1. Copy the template to your Next.js project
cp CLAUDE.md /path/to/your-nextjs-project/CLAUDE.md

# 2. (Optional) Create a seed project to verify
npx create-next-app@latest test-saas --ts --tailwind --app --src-dir
cd test-saas
cp /path/to/CLAUDE.md .
# Open Claude Code — it should understand the context immediately
```

## What's Covered

| Section | Content |
|---------|---------|
| Stack & Versions | Every choice justified — Next.js 15, SQLite, Drizzle, Lucia, Tailwind |
| Project Structure | App Router layout with route groups, db/, actions/, emails/ |
| Naming Conventions | Files (kebab-case), components (PascalCase), DB columns (snake_case) |
| Database Rules | Migration discipline, query patterns, anti-patterns (never DROP TABLE in migration) |
| Component Patterns | Server-first, client-component checklist, data fetching hierarchy |
| Forms Pattern | Zod schema → Server Action → Client Form (complete working example) |
| Typed Env | t3-env pattern — server and client env with Zod validation |
| Anti-Patterns | 10 things we never do and why |
| Dev Commands | All `pnpm` commands you'll reach for |
| Commit Convention | Standardized, grep-friendly |

## Why Opinionated?

Every rule has a reason inline. This isn't a generic style guide — it's a
battle-tested playbook for shipping SaaS with Next.js + SQLite without
analysis paralysis.

## Testing that it works

```bash
npx create-next-app@latest test-project --ts --tailwind --app --src-dir
cd test-project
cp /path/to/CLAUDE.md .
# Start Claude Code — it should know the stack, conventions, and patterns
# without asking clarifying questions
```

## Requirements Met

- [x] Covers project structure, naming conventions, DB migration rules
- [x] Dev commands, patterns to follow, anti-patterns to avoid
- [x] Opinionated — every rule has a reason
- [x] Usable on greenfield project without modification
- [x] Tested blueprint: create-next-app → paste → Claude Code understands
