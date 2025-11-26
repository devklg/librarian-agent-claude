"""
Skill Manager - Loads and manages skills from /mnt/skills
"""

import os
from typing import Dict, List
from pathlib import Path


class SkillManager:
    """
    Manages the Skills Library:
    - Loads skills from /mnt/skills
    - Detects which skills are needed for a query
    - Indexes skills in Universal Memory Bridge
    """
    
    def __init__(self, skills_base_path: str = "/mnt/skills"):
        self.skills_base_path = skills_base_path
        self.skills_cache = {}
    
    def load_all_skills(self) -> Dict[str, Dict]:
        """Load all available skills"""
        
        skills = {}
        
        # Public skills (always available)
        public_skills = {
            'docx': {
                'path': f'{self.skills_base_path}/public/docx/SKILL.md',
                'description': 'Expert guide for creating and editing Word documents'
            },
            'pptx': {
                'path': f'{self.skills_base_path}/public/pptx/SKILL.md',
                'description': 'Expert guide for creating and editing PowerPoint presentations'
            },
            'xlsx': {
                'path': f'{self.skills_base_path}/public/xlsx/SKILL.md',
                'description': 'Expert guide for creating and editing Excel spreadsheets'
            },
            'pdf': {
                'path': f'{self.skills_base_path}/public/pdf/SKILL.md',
                'description': 'Expert guide for PDF manipulation and generation'
            },
            'product-self-knowledge': {
                'path': f'{self.skills_base_path}/public/product-self-knowledge/SKILL.md',
                'description': 'Authoritative info about Anthropic products and Claude'
            },
            'frontend-design': {
                'path': f'{self.skills_base_path}/public/frontend-design/SKILL.md',
                'description': 'Create distinctive, production-grade frontend interfaces'
            }
        }
        
        # Example skills (optional)
        example_skills = {
            'skill-creator': {
                'path': f'{self.skills_base_path}/examples/skill-creator/SKILL.md',
                'description': 'Guide for creating effective new skills'
            },
            'theme-factory': {
                'path': f'{self.skills_base_path}/examples/theme-factory/SKILL.md',
                'description': 'Toolkit for styling artifacts with themes'
            },
            'brand-guidelines': {
                'path': f'{self.skills_base_path}/examples/brand-guidelines/SKILL.md',
                'description': "Anthropic's official brand colors and typography"
            }
        }
        
        # Load each skill
        for skill_name, skill_info in {**public_skills, **example_skills}.items():
            content = self._load_skill_file(skill_info['path'])
            if content:
                skills[skill_name] = {
                    'content': content,
                    'description': skill_info['description'],
                    'path': skill_info['path'],
                    'category': 'public' if 'public' in skill_info['path'] else 'example'
                }
        
        self.skills_cache = skills
        return skills
    
    def _load_skill_file(self, path: str) -> str:
        """Load a single skill file"""
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️  Skill not found: {path}")
            return ""
        except Exception as e:
            print(f"❌ Error loading skill {path}: {e}")
            return ""
    
    def detect_needed_skills(self, message: str) -> List[str]:
        """
        Detect which skills are needed based on the user's message
        
        Uses keyword matching to determine relevant skills
        """
        
        message_lower = message.lower()
        needed = []
        
        # Document creation/editing keywords
        if any(word in message_lower for word in ['word', 'docx', 'document', 'doc']):
            needed.append('docx')
        
        if any(word in message_lower for word in ['powerpoint', 'pptx', 'presentation', 'slide']):
            needed.append('pptx')
        
        if any(word in message_lower for word in ['excel', 'xlsx', 'spreadsheet', 'workbook']):
            needed.append('xlsx')
        
        if any(word in message_lower for word in ['pdf', 'portable document']):
            needed.append('pdf')
        
        # Frontend/design keywords
        if any(word in message_lower for word in ['frontend', 'ui', 'interface', 'react', 'html', 'css']):
            needed.append('frontend-design')
        
        # Theme/branding keywords
        if any(word in message_lower for word in ['theme', 'style', 'color', 'brand']):
            if 'anthropic' in message_lower:
                needed.append('brand-guidelines')
            else:
                needed.append('theme-factory')
        
        # Skill creation keywords
        if any(word in message_lower for word in ['create skill', 'new skill', 'skill for']):
            needed.append('skill-creator')
        
        # Product knowledge keywords
        if any(word in message_lower for word in ['claude api', 'anthropic', 'claude code', 'pricing', 'rate limit']):
            needed.append('product-self-knowledge')
        
        return needed
    
    def get_skill(self, skill_name: str) -> Dict:
        """Get a specific skill"""
        
        return self.skills_cache.get(skill_name, {})
    
    def get_all_skill_names(self) -> List[str]:
        """Get names of all loaded skills"""
        
        return list(self.skills_cache.keys())
    
    def search_skills(self, query: str) -> List[str]:
        """Search skills by content"""
        
        query_lower = query.lower()
        matching = []
        
        for skill_name, skill_data in self.skills_cache.items():
            if query_lower in skill_data['content'].lower():
                matching.append(skill_name)
        
        return matching
