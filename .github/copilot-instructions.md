# Copilot Context — ai-tutor-prompts

## Repo Purpose

System prompts and curricula for AI-powered education agents. Target: Rishaan (age 13, entering Grade 9),
preparing for AP, IB, SASMO, and AMC exams with the goal of admission to top US/UK/EU universities.

## Student Profile

| Field | Value |
|---|---|
| Name | Rishaan |
| Age | 13 (entering Grade 9) |
| Daily study time | 60 minutes |
| Target exams | AP (5+ subjects), IB Diploma, SASMO, AMC 10/12 |
| University targets | Top 20 US, Oxbridge, ETH Zurich, TU Delft |
| Chinese | Active learning — Mandarin grammar, HSK |

## Teacher Agent Roster

| Agent | Subject | Model | Backend |
|---|---|---|---|
| MathTeacher | AP Calc, AMC, SASMO, IB Math AA/AI | Qwen3-Next-80B | GX10 vLLM |
| ScienceTeacher | AP Physics/Chem/Bio, IB Sciences | Qwen3-Next-80B | GX10 vLLM |
| EnglishTeacher | AP English Lang/Lit, IB English A/B | Qwen3-Next-80B | GX10 vLLM |
| ChineseTeacher | Mandarin grammar, composition, HSK | Qwen3-Next-80B | GX10 vLLM |
| HistoryTeacher | AP World/US/Euro, IB History | Qwen3-Next-80B | GX10 vLLM |
| LearningCoach | Multi-subject progress, study schedule | Qwen3-Next-80B | GX10 vLLM |

All teachers run on GX10 vLLM with **thinking mode** (`/think`) for deep reasoning.
Chinese teacher benefits from Qwen's native Chinese training.

## Multi-Repo Architecture

| Repo | Domain |
|---|---|
| **ai-tutor-prompts** (this) | System prompts, profiles, curricula, schedules |
| **ai-agent-roles** | Teacher agent definitions, tool permissions, routing |
| **k8s-home-lab** | OpenClaw deployment manifests (ai-agents namespace) |

## Directory Layout

```
ai-tutor-prompts/
  prompts/
    math/         AP Calc, AMC, SASMO, IB Math
    science/      AP Physics, Chemistry, Biology, IB Sciences
    english/      AP English Lang/Lit, IB English A/B
    chinese/      Mandarin, HSK
    history/      AP World/US/Euro, IB History
  profiles/
    student.yml   Rishaan's profile, gaps, learning style
    gangadhar.yml Personal learning context
    sameena.yml   Family context
    family_facts.yml  Shared family facts used by agents
  configs/
    routing.yml   Subject → model routing
    schedule.yml  Study schedule + exam calendar
  scripts/
    provision_openwebui.py   Register prompts in Open-WebUI
  tests/          Prompt validation + regression tests
```

## Interface

- **Primary**: Open-WebUI (`openwebui.lab`) — agents registered as system prompt presets
- Provisioned via `scripts/provision_openwebui.py` (calls Open-WebUI API)
- `configs/schedule.yml` drives daily subject rotation and exam prep windows

## Conventions

- Prompts are Markdown files with YAML frontmatter (model, temperature, tags)
- All personally identifying info in `profiles/` — never hardcode in prompts
- Tests: `pytest tests/` from repo root
- Push to Gitea → ArgoCD deploys Open-WebUI config changes via k8s ConfigMaps
