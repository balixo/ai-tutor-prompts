"""Unit tests for ai-tutor-prompts configuration validation."""

from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
CONFIGS_DIR = PROJECT_ROOT / "configs"
PROFILES_DIR = PROJECT_ROOT / "profiles"

EXPECTED_SUBJECTS = {"math", "science", "english", "chinese", "history"}
REQUIRED_PROMPT_FIELDS = ["role", "name", "model", "system_prompt", "exam_targets"]
VALID_BACKENDS = {"gx10", "minillm", "jetson", "desktop"}


class TestPromptFiles:
    """Validate all teacher system prompts."""

    def test_all_subjects_have_prompts(self):
        for subject in EXPECTED_SUBJECTS:
            prompt_file = PROMPTS_DIR / subject / "system.yml"
            assert prompt_file.exists(), f"Missing prompt for {subject}"

    def test_all_prompts_valid_yaml(self):
        for subject in EXPECTED_SUBJECTS:
            prompt_file = PROMPTS_DIR / subject / "system.yml"
            with open(prompt_file) as f:
                config = yaml.safe_load(f)
            assert isinstance(config, dict), f"{subject}: root must be mapping"

    def test_all_prompts_have_required_fields(self):
        for subject in EXPECTED_SUBJECTS:
            prompt_file = PROMPTS_DIR / subject / "system.yml"
            with open(prompt_file) as f:
                config = yaml.safe_load(f)
            for field in REQUIRED_PROMPT_FIELDS:
                assert field in config, f"{subject}: missing '{field}'"

    def test_prompt_role_matches_directory(self):
        for subject in EXPECTED_SUBJECTS:
            prompt_file = PROMPTS_DIR / subject / "system.yml"
            with open(prompt_file) as f:
                config = yaml.safe_load(f)
            assert config["role"] == f"{subject}-teacher", (
                f"{subject}: role '{config['role']}' != '{subject}-teacher'"
            )

    def test_all_prompts_have_valid_backend(self):
        for subject in EXPECTED_SUBJECTS:
            prompt_file = PROMPTS_DIR / subject / "system.yml"
            with open(prompt_file) as f:
                config = yaml.safe_load(f)
            backend = config.get("model", {}).get("backend", "")
            assert backend in VALID_BACKENDS, f"{subject}: unknown backend '{backend}'"

    def test_system_prompt_not_empty(self):
        for subject in EXPECTED_SUBJECTS:
            prompt_file = PROMPTS_DIR / subject / "system.yml"
            with open(prompt_file) as f:
                config = yaml.safe_load(f)
            prompt = config.get("system_prompt", "")
            assert len(prompt.strip()) > 100, f"{subject}: system_prompt too short"

    def test_exam_targets_not_empty(self):
        for subject in EXPECTED_SUBJECTS:
            prompt_file = PROMPTS_DIR / subject / "system.yml"
            with open(prompt_file) as f:
                config = yaml.safe_load(f)
            targets = config.get("exam_targets", [])
            assert len(targets) >= 2, f"{subject}: need at least 2 exam targets"


class TestMathTeacherSpecific:
    """Math teacher uses 32B with thinking mode for AMC/AIME."""

    @pytest.fixture
    def config(self):
        with open(PROMPTS_DIR / "math" / "system.yml") as f:
            return yaml.safe_load(f)

    def test_uses_32b_model(self, config):
        assert "32b" in config["model"]["primary"]

    def test_thinking_mode_enabled(self, config):
        assert config["model"]["thinking_mode"] is True

    def test_mentions_amc(self, config):
        prompt = config["system_prompt"]
        assert "AMC" in prompt

    def test_mentions_socratic(self, config):
        prompt = config["system_prompt"]
        assert "Socratic" in prompt


class TestScienceTeacherSpecific:
    """Science teacher uses 32B with thinking mode for derivations."""

    @pytest.fixture
    def config(self):
        with open(PROMPTS_DIR / "science" / "system.yml") as f:
            return yaml.safe_load(f)

    def test_uses_32b_model(self, config):
        assert "32b" in config["model"]["primary"]

    def test_thinking_mode_enabled(self, config):
        assert config["model"]["thinking_mode"] is True


class TestChineseTeacherSpecific:
    """Chinese teacher leverages Qwen's native Chinese strength."""

    @pytest.fixture
    def config(self):
        with open(PROMPTS_DIR / "chinese" / "system.yml") as f:
            return yaml.safe_load(f)

    def test_uses_7b_model(self, config):
        assert "7b" in config["model"]["primary"]

    def test_mentions_pinyin(self, config):
        assert "pinyin" in config["system_prompt"].lower()

    def test_mentions_hsk(self, config):
        assert "HSK" in config["system_prompt"]


class TestStudentProfile:
    """Validate student profile structure."""

    @pytest.fixture
    def profile(self):
        with open(PROFILES_DIR / "student.yml") as f:
            return yaml.safe_load(f)

    def test_has_student_section(self, profile):
        assert "student" in profile

    def test_age_is_13(self, profile):
        assert profile["student"]["age"] == 13

    def test_daily_minutes_is_60(self, profile):
        assert profile["student"]["daily_study_minutes"] == 60

    def test_has_university_targets(self, profile):
        assert "university_targets" in profile
        targets = profile["university_targets"]
        assert "us_top_20" in targets
        assert "uk" in targets
        assert "europe" in targets

    def test_has_current_profile(self, profile):
        assert "current_profile" in profile
        for subject in EXPECTED_SUBJECTS:
            assert subject in profile["current_profile"], f"Missing {subject} in current_profile"

    def test_has_bridge_plan(self, profile):
        assert "bridge_plan" in profile


class TestRoutingConfig:
    """Validate routing configuration for all teachers."""

    @pytest.fixture
    def routing(self):
        with open(CONFIGS_DIR / "routing.yml") as f:
            return yaml.safe_load(f)

    def test_all_teachers_have_routing(self, routing):
        agents = routing["routing"]["agents"]
        for subject in EXPECTED_SUBJECTS:
            agent_name = f"{subject}-teacher"
            assert agent_name in agents, f"Missing routing for {agent_name}"

    def test_math_science_use_32b(self, routing):
        agents = routing["routing"]["agents"]
        assert "32b" in agents["math-teacher"]["model"]
        assert "32b" in agents["science-teacher"]["model"]

    def test_math_science_thinking_enabled(self, routing):
        agents = routing["routing"]["agents"]
        assert agents["math-teacher"]["thinking_mode"] is True
        assert agents["science-teacher"]["thinking_mode"] is True

    def test_english_chinese_history_use_7b(self, routing):
        agents = routing["routing"]["agents"]
        assert "7b" in agents["english-teacher"]["model"]
        assert "7b" in agents["chinese-teacher"]["model"]
        assert "7b" in agents["history-teacher"]["model"]


class TestScheduleConfig:
    """Validate study schedule."""

    @pytest.fixture
    def schedule(self):
        with open(CONFIGS_DIR / "schedule.yml") as f:
            return yaml.safe_load(f)

    def test_daily_minutes(self, schedule):
        assert schedule["schedule"]["daily_minutes"] == 60

    def test_all_weekdays_assigned(self, schedule):
        weekly = schedule["schedule"]["weekly"]
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            assert day in weekly, f"Missing {day}"

    def test_sunday_is_rest(self, schedule):
        assert schedule["schedule"]["weekly"]["sunday"] == "rest"

    def test_exam_calendar_has_all_grades(self, schedule):
        calendar = schedule["exam_calendar"]
        for grade in ["grade_9", "grade_10", "grade_11", "grade_12"]:
            assert grade in calendar, f"Missing {grade}"
