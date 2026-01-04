"""
Unit tests for SkillManager
"""

import pytest
from pathlib import Path
from skill_manager import SkillManager


class TestSkillManager:
    """Tests for SkillManager class"""

    def test_init_default_path(self):
        """Test initialization with default path"""
        manager = SkillManager()
        assert manager.skills_base_path is not None
        assert "skills" in manager.skills_base_path

    def test_init_custom_path(self, tmp_path):
        """Test initialization with custom path"""
        custom_path = str(tmp_path / "custom_skills")
        manager = SkillManager(skills_base_path=custom_path)
        assert manager.skills_base_path == custom_path

    def test_load_all_skills(self, temp_skills_dir):
        """Test loading all skills from directory"""
        manager = SkillManager(skills_base_path=str(temp_skills_dir))
        skills = manager.load_all_skills()

        # Should return a dictionary
        assert isinstance(skills, dict)

    def test_detect_needed_skills_docx(self):
        """Test skill detection for document keywords"""
        manager = SkillManager()

        # Test docx detection
        skills = manager.detect_needed_skills("I need to create a Word document")
        assert "docx" in skills

        skills = manager.detect_needed_skills("Help me with a .docx file")
        assert "docx" in skills

    def test_detect_needed_skills_xlsx(self):
        """Test skill detection for spreadsheet keywords"""
        manager = SkillManager()

        skills = manager.detect_needed_skills("Create an Excel spreadsheet")
        assert "xlsx" in skills

        skills = manager.detect_needed_skills("I need a workbook for data")
        assert "xlsx" in skills

    def test_detect_needed_skills_pptx(self):
        """Test skill detection for presentation keywords"""
        manager = SkillManager()

        skills = manager.detect_needed_skills("Make a PowerPoint presentation")
        assert "pptx" in skills

        skills = manager.detect_needed_skills("I need slides for my talk")
        assert "pptx" in skills

    def test_detect_needed_skills_pdf(self):
        """Test skill detection for PDF keywords"""
        manager = SkillManager()

        skills = manager.detect_needed_skills("Convert this to PDF")
        assert "pdf" in skills

    def test_detect_needed_skills_frontend(self):
        """Test skill detection for frontend keywords"""
        manager = SkillManager()

        skills = manager.detect_needed_skills("Build a React UI component")
        assert "frontend-design" in skills

        skills = manager.detect_needed_skills("Create an HTML interface")
        assert "frontend-design" in skills

    def test_detect_needed_skills_multiple(self):
        """Test detection of multiple skills"""
        manager = SkillManager()

        skills = manager.detect_needed_skills(
            "Create a Word document with data from Excel"
        )
        assert "docx" in skills
        assert "xlsx" in skills

    def test_detect_needed_skills_empty(self):
        """Test skill detection with no matching keywords"""
        manager = SkillManager()

        skills = manager.detect_needed_skills("Tell me a joke")
        assert len(skills) == 0

    def test_detect_needed_skills_case_insensitive(self):
        """Test that skill detection is case insensitive"""
        manager = SkillManager()

        skills_lower = manager.detect_needed_skills("create a word document")
        skills_upper = manager.detect_needed_skills("CREATE A WORD DOCUMENT")
        skills_mixed = manager.detect_needed_skills("Create A Word Document")

        assert "docx" in skills_lower
        assert "docx" in skills_upper
        assert "docx" in skills_mixed

    def test_get_skill(self, mock_skill_content):
        """Test getting a specific skill"""
        manager = SkillManager()
        manager.skills_cache = mock_skill_content

        skill = manager.get_skill("docx")
        assert skill is not None
        assert "content" in skill
        assert "description" in skill

    def test_get_skill_not_found(self):
        """Test getting a skill that doesn't exist"""
        manager = SkillManager()
        manager.skills_cache = {}

        skill = manager.get_skill("nonexistent")
        assert skill == {}

    def test_get_all_skill_names(self, mock_skill_content):
        """Test getting all skill names"""
        manager = SkillManager()
        manager.skills_cache = mock_skill_content

        names = manager.get_all_skill_names()
        assert "docx" in names
        assert "xlsx" in names
        assert len(names) == 2

    def test_search_skills(self, mock_skill_content):
        """Test searching skills by content"""
        manager = SkillManager()
        manager.skills_cache = mock_skill_content

        results = manager.search_skills("Word")
        assert "docx" in results

        results = manager.search_skills("Excel")
        assert "xlsx" in results

        results = manager.search_skills("Python")
        assert len(results) == 0

    def test_load_skill_file_not_found(self, tmp_path):
        """Test loading a skill file that doesn't exist"""
        manager = SkillManager(skills_base_path=str(tmp_path))
        content = manager._load_skill_file("/nonexistent/path/SKILL.md")
        assert content == ""
