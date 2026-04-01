# AI Tutor Prompts

System prompts and curricula for AI-powered education agents targeting a 13-year-old
student preparing for AP, IB, SASMO, and AMC exams with the goal of admission to
top US, UK, and European universities.

## Architecture

```
Teacher Agents (5)           Router/LB
  ├── math-teacher    ──→  GX10 vLLM 32B  (thinking mode, deep reasoning)
  ├── science-teacher ──→  GX10 vLLM 32B  (thinking mode, experiments)
  ├── english-teacher ──→  GX10 vLLM 7B   (writing quality, fast feedback)
  ├── chinese-teacher ──→  GX10 vLLM 7B   (native Qwen strength)
  └── history-teacher ──→  GX10 vLLM 7B   (factual recall, essay analysis)
```

## Directory Structure

```
ai-tutor-prompts/
├── prompts/              System prompts per subject
│   ├── math/             AP Calc, AMC, SASMO, IB Math AA/AI
│   ├── science/          AP Physics, Chemistry, Biology, IB Sciences
│   ├── english/          AP English Lang/Lit, IB English A/B
│   ├── chinese/          Mandarin grammar, composition, HSK
│   └── history/          AP World/US/Euro History, IB History
├── profiles/             Student profile & gap analysis
├── configs/              Model routing, study schedule, exam calendar
├── scripts/              Progress tracking, quiz generation
└── tests/                Prompt validation tests
```

## Student Profile

- **Age**: 13 (entering Grade 9)
- **Target grades**: 9, 10, 11, 12
- **Daily study time**: 60 minutes
- **Target exams**: AP (5+ subjects), IB Diploma, SASMO, AMC 10/12
- **University targets**: Top 20 US, Oxbridge, EU (ETH Zurich, TU Delft)

## Inference Backend

All teacher agents run on the GX10 (NVIDIA Blackwell GB10, 128GB) via vLLM:
- **Math & Science**: Qwen3.5-32B-AWQ with thinking mode (`enable_thinking=True`)
  for step-by-step proofs and problem solving
- **English, Chinese, History**: Qwen3.5-7B for fast, high-quality feedback
- **Fallback**: Desktop Ollama (RTX 5070 Ti, 16GB) for interactive Q&A
