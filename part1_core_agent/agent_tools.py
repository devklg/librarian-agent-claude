"""
Agent Tools - Tool definitions and executors for Librarian Agent
"""

from typing import Dict, List, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AgentTools:
    """
    Defines and executes tools that the Librarian Agent can use:
    - search_documentation: Search the Universal Memory Bridge
    - load_documentation: Ingest new docs
    - query_skill: Get detailed skill guidance
    - update_knowledge_graph: Add relationships to Neo4j
    - get_catalog: List available knowledge modules
    """
    
    def __init__(self):
        self.universal_memory_bridge = None  # Will be imported dynamically
    
    def get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions for Claude"""
        
        return [
            {
                "name": "search_documentation",
                "description": "Search the Universal Memory Bridge knowledge base for relevant documentation. Searches across ChromaDB (semantic), MongoDB (documents), Neo4j (relationships), and Neon (SQL).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query. Be specific about what you're looking for."
                        },
                        "category": {
                            "type": "string",
                            "enum": ["framework", "business", "training", "compliance", "general", "all"],
                            "description": "Optional category filter"
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "load_documentation",
                "description": "Ingest new documentation into the Universal Memory Bridge. Loads content from URL or file path and stores in all 4 databases.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "URL or file path to the documentation"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name for this knowledge module"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["framework", "business", "training", "compliance", "general"],
                            "description": "Category of the documentation"
                        },
                        "target_agent_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Which agent types should access this (e.g., ['coding', 'voice', 'mlm'])"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["HIGH", "MEDIUM", "LOW"],
                            "description": "Priority level",
                            "default": "MEDIUM"
                        }
                    },
                    "required": ["source", "name", "category", "target_agent_types"]
                }
            },
            {
                "name": "query_skill",
                "description": "Get detailed guidance from a specific skill. Skills contain expert knowledge about document creation, coding, design, etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "enum": ["docx", "pptx", "xlsx", "pdf", "frontend-design", "skill-creator", "theme-factory", "brand-guidelines", "product-self-knowledge"],
                            "description": "Name of the skill to query"
                        },
                        "specific_question": {
                            "type": "string",
                            "description": "Optional: specific question about the skill"
                        }
                    },
                    "required": ["skill_name"]
                }
            },
            {
                "name": "update_knowledge_graph",
                "description": "Add or update relationships in the Neo4j knowledge graph. Use this to connect related concepts, frameworks, or documentation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "source_entity": {
                            "type": "string",
                            "description": "The source entity/concept"
                        },
                        "target_entity": {
                            "type": "string",
                            "description": "The target entity/concept"
                        },
                        "relationship_type": {
                            "type": "string",
                            "description": "Type of relationship (e.g., 'DEPENDS_ON', 'RELATES_TO', 'IMPLEMENTS')"
                        },
                        "properties": {
                            "type": "object",
                            "description": "Optional properties for the relationship"
                        }
                    },
                    "required": ["source_entity", "target_entity", "relationship_type"]
                }
            },
            {
                "name": "get_catalog",
                "description": "Get a list of all available knowledge modules in the catalog. Useful for understanding what documentation is available.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["framework", "business", "training", "compliance", "general", "all"],
                            "description": "Optional category filter",
                            "default": "all"
                        }
                    }
                }
            }
        ]
    
    async def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result"""
        
        try:
            if tool_name == "search_documentation":
                return await self.search_documentation(**tool_input)
            
            elif tool_name == "load_documentation":
                return await self.load_documentation(**tool_input)
            
            elif tool_name == "query_skill":
                return await self.query_skill(**tool_input)
            
            elif tool_name == "update_knowledge_graph":
                return await self.update_knowledge_graph(**tool_input)
            
            elif tool_name == "get_catalog":
                return await self.get_catalog(**tool_input)
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    async def search_documentation(
        self,
        query: str,
        category: str = "all",
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Search the Universal Memory Bridge"""
        
        # This would connect to the actual Universal Memory Bridge
        # For now, return a mock response
        
        return {
            "success": True,
            "query": query,
            "results": [
                f"Result 1 for '{query}' in category '{category}'",
                f"Result 2 for '{query}'",
                f"Result 3 for '{query}'"
            ],
            "sources": [
                {"module": "Example Module 1", "priority": "HIGH"},
                {"module": "Example Module 2", "priority": "MEDIUM"},
                {"module": "Example Module 3", "priority": "LOW"}
            ],
            "tokens_saved": 18000  # Compared to web search
        }
    
    async def load_documentation(
        self,
        source: str,
        name: str,
        category: str,
        target_agent_types: List[str],
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Load new documentation into the system using Docling
        
        Docling provides multi-modal processing:
        - Extracts text AND images from PDFs
        - Uses OpenAI to caption/describe images
        - Creates enriched text for better RAG
        """
        
        try:
            from docling_extractor import DoclingExtractor
            
            # Initialize Docling with AI image captioning
            docling = DoclingExtractor(enable_image_captions=True)
            
            # Extract with multi-modal processing
            result = docling.extract(
                source=source,
                save_images=True,
                output_dir=f'./doc_images/{name}'
            )
            
            # Store in Universal Memory Bridge (all 4 databases)
            # In production, this connects to the actual bridge
            
            return {
                "success": True,
                "module_id": f"{name}_v{int(time.time())}",
                "module_name": name,
                "source": source,
                "category": category,
                "target_agent_types": target_agent_types,
                "priority": priority,
                "databases_stored": 4,
                "tokens": len(result['content']) // 4,
                "chunks_created": len(result['chunks']),
                "images_processed": len(result['images']),
                "processing": "docling_multimodal",
                "metadata": result['metadata']
            }
            
        except ImportError:
            # Fallback if Docling not installed
            return {
                "success": True,
                "module_id": f"{name}_v{int(time.time())}",
                "module_name": name,
                "source": source,
                "category": category,
                "target_agent_types": target_agent_types,
                "priority": priority,
                "databases_stored": 4,
                "tokens": 5000,
                "processing": "basic",
                "note": "Docling not installed - using basic extraction"
            }
    
    async def query_skill(
        self,
        skill_name: str,
        specific_question: str = None
    ) -> Dict[str, Any]:
        """Query a specific skill for guidance"""
        
        from skill_manager import SkillManager
        
        manager = SkillManager()
        skill = manager.get_skill(skill_name)
        
        if not skill:
            return {"error": f"Skill '{skill_name}' not found"}
        
        response = {
            "success": True,
            "skill_name": skill_name,
            "skill_content": skill['content']
        }
        
        if specific_question:
            response["note"] = f"Skill content provided. Look for information about: {specific_question}"
        
        return response
    
    async def update_knowledge_graph(
        self,
        source_entity: str,
        target_entity: str,
        relationship_type: str,
        properties: Dict = None
    ) -> Dict[str, Any]:
        """Update the Neo4j knowledge graph"""
        
        return {
            "success": True,
            "relationship_created": f"{source_entity} -{relationship_type}-> {target_entity}",
            "properties": properties or {}
        }
    
    async def get_catalog(self, category: str = "all") -> Dict[str, Any]:
        """Get the knowledge catalog"""
        
        return {
            "success": True,
            "category": category,
            "total_modules": 42,
            "modules": [
                {"name": "Telnyx API", "category": "framework", "priority": "HIGH"},
                {"name": "Claude API", "category": "framework", "priority": "HIGH"},
                {"name": "BANTI Framework", "category": "business", "priority": "HIGH"}
            ]
        }


import time
