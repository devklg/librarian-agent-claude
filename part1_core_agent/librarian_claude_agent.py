"""
Librarian Claude Agent - Core Engine
Powered by Claude SDK with Prompt Caching (Hooks) and Skills Integration
"""

import os
import time
import json
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from agent_tools import AgentTools
from skill_manager import SkillManager
from conversation_manager import ConversationManager


class LibrarianClaudeAgent:
    """
    Intelligent Librarian Agent that:
    - Uses Claude SDK for natural language understanding
    - Leverages Prompt Caching (Hooks) for 90% cost savings
    - Integrates Skills for expert guidance
    - Connects to Universal Memory Bridge (4 databases)
    - Manages conversation context
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Librarian Agent"""
        
        # Claude SDK
        self.claude = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        
        # Components
        self.skill_manager = SkillManager()
        self.tools = AgentTools()
        self.conversation_manager = ConversationManager()
        
        # Load skills at startup (these will be cached!)
        self.skills = self.skill_manager.load_all_skills()
        
        # System prompt (cached with hooks)
        self.system_prompt = self._build_system_prompt()
        
        print(f"✅ Librarian Agent initialized with {len(self.skills)} skills")
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with skill list"""
        
        skill_list = "\n".join([
            f"- {name}: {skill['description']}"
            for name, skill in self.skills.items()
        ])
        
        return f"""You are the Librarian Agent, the intelligent keeper of all knowledge in the Universal Memory Bridge.

🎯 YOUR ROLE:
- Help users find and understand documentation
- Provide expert guidance using specialized skills
- Search across 4 databases (ChromaDB, MongoDB, Neo4j, Neon PostgreSQL)
- Create, edit, and analyze documents (DOCX, PPTX, XLSX, PDF)
- Synthesize information from multiple sources
- Ask clarifying questions when needed
- Track conversation context

🛠️ AVAILABLE SKILLS:
{skill_list}

💡 HOW TO USE SKILLS:
1. When a user asks about creating/editing documents, query the relevant skill first
2. Follow the skill's best practices exactly
3. Combine multiple skills when needed (e.g., docx + theme-factory)
4. Always cite which skills you used

🎨 PERSONALITY:
- Knowledgeable but approachable
- Patient and thorough
- Cite sources always (both docs and skills)
- Admit uncertainty when appropriate
- Proactive - suggest better approaches

📊 TOOLS YOU HAVE:
- search_documentation: Search the knowledge base
- load_documentation: Ingest new docs into system
- query_skill: Get detailed skill guidance
- update_knowledge_graph: Add relationships to Neo4j
- get_catalog: List all available knowledge modules

Remember: Skills are your superpower! Use them to provide expert-level guidance."""

    async def chat(
        self, 
        message: str, 
        session_id: str,
        requester_id: str = "user",
        requester_type: str = "human"
    ) -> Dict[str, Any]:
        """
        Main chat interface with Skills + Hooks optimization
        
        Args:
            message: User's message
            session_id: Unique session identifier
            requester_id: ID of the requester
            requester_type: Type (human/agent/application)
            
        Returns:
            Response with message, tool calls, costs, and cache stats
        """
        
        start_time = time.time()
        
        # Get conversation history
        conversation = self.conversation_manager.get_conversation(session_id)
        
        # Detect needed skills based on message
        needed_skills = self.skill_manager.detect_needed_skills(message)
        
        # Build skill context (will be cached!)
        skill_context = self._build_skill_context(needed_skills)
        
        # Get relevant documentation (will be cached per session!)
        doc_context = await self._get_documentation_context(message, session_id)
        
        # Build messages with caching
        messages = self._build_cached_messages(
            message=message,
            conversation=conversation,
            skill_context=skill_context,
            doc_context=doc_context
        )
        
        # Call Claude with Hooks
        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            
            # 🎣 CACHE CONTROL: System prompt
            system=[{
                "type": "text",
                "text": self.system_prompt,
                "cache_control": {"type": "ephemeral"}
            }],
            
            # 🎣 CACHE CONTROL: Tools
            tools=self._get_cached_tools(),
            
            # Messages with cached contexts
            messages=messages
        )
        
        # Process response
        result = await self._process_response(
            response=response,
            session_id=session_id,
            message=message,
            start_time=start_time,
            needed_skills=needed_skills
        )
        
        # Save conversation turn
        self.conversation_manager.add_turn(
            session_id=session_id,
            user_message=message,
            agent_response=result['message'],
            tool_calls=result.get('tool_calls', []),
            skills_used=needed_skills
        )
        
        return result
    
    def _build_skill_context(self, needed_skills: List[str]) -> str:
        """Build context from needed skills"""
        
        if not needed_skills:
            return ""
        
        contexts = []
        for skill_name in needed_skills:
            if skill_name in self.skills:
                skill = self.skills[skill_name]
                contexts.append(f"=== SKILL: {skill_name} ===\n{skill['content']}\n")
        
        return "\n".join(contexts)
    
    async def _get_documentation_context(
        self, 
        query: str, 
        session_id: str
    ) -> str:
        """Get relevant documentation (cached per session)"""
        
        # Check session cache
        cached = self.conversation_manager.get_session_cache(session_id, 'docs')
        if cached:
            return cached
        
        # Query documentation
        results = await self.tools.search_documentation(query, n_results=5)
        
        # Format for context
        context = self._format_docs_for_cache(results)
        
        # Cache for session
        self.conversation_manager.set_session_cache(session_id, 'docs', context)
        
        return context
    
    def _format_docs_for_cache(self, results: Dict) -> str:
        """Format search results for caching"""
        
        if not results or not results.get('results'):
            return ""
        
        formatted = []
        for i, result in enumerate(results['results']):
            source = results['sources'][i] if i < len(results['sources']) else {}
            formatted.append(
                f"[DOC {i+1}] {source.get('module', 'Unknown')}\n{result}\n"
            )
        
        return "\n".join(formatted)
    
    def _build_cached_messages(
        self,
        message: str,
        conversation: List[Dict],
        skill_context: str,
        doc_context: str
    ) -> List[Dict]:
        """Build message array with strategic caching"""
        
        messages = []
        
        # Add previous conversation (older messages can be cached)
        if conversation:
            # Cache older conversation turns
            for turn in conversation[:-2]:  # All but last 2 turns
                messages.append({
                    "role": "user",
                    "content": turn['user_message']
                })
                messages.append({
                    "role": "assistant",
                    "content": turn['agent_response']
                })
            
            # Recent turns (not cached)
            for turn in conversation[-2:]:
                messages.append({
                    "role": "user",
                    "content": turn['user_message']
                })
                messages.append({
                    "role": "assistant",
                    "content": turn['agent_response']
                })
        
        # Add skill context (CACHED!)
        if skill_context:
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"📚 SKILL CONTEXT:\n\n{skill_context}"
                    },
                    {
                        "type": "text",
                        "text": "Skills loaded and ready.",
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
            })
            messages.append({
                "role": "assistant",
                "content": "I've reviewed the skills and I'm ready to apply them."
            })
        
        # Add documentation context (CACHED!)
        if doc_context:
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"📖 DOCUMENTATION:\n\n{doc_context}"
                    },
                    {
                        "type": "text",
                        "text": "Documentation loaded.",
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
            })
            messages.append({
                "role": "assistant",
                "content": "I've reviewed the documentation."
            })
        
        # Add current user message (NOT cached - always fresh)
        messages.append({
            "role": "user",
            "content": message
        })
        
        return messages
    
    def _get_cached_tools(self) -> List[Dict]:
        """Get tool definitions with cache control"""
        
        tools = self.tools.get_tool_definitions()
        
        # Add cache control to last tool (caches all tools)
        if tools:
            tools[-1]["cache_control"] = {"type": "ephemeral"}
        
        return tools
    
    async def _process_response(
        self,
        response: Any,
        session_id: str,
        message: str,
        start_time: float,
        needed_skills: List[str]
    ) -> Dict[str, Any]:
        """Process Claude's response and handle tool calls"""
        
        # Extract text response
        text_response = ""
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                text_response += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
        
        # Handle tool calls if present
        if response.stop_reason == "tool_use" and tool_calls:
            tool_results = await self._execute_tools(tool_calls)
            
            # Continue conversation with tool results
            # (This would need another Claude call in production)
            # For now, just log them
            text_response += f"\n\n[Tool Results: {len(tool_results)} tools executed]"
        
        # Calculate costs with cache breakdown
        usage = response.usage
        cost_info = self._calculate_cost_with_cache(usage)
        
        # Response time
        response_time = time.time() - start_time
        
        return {
            "message": text_response,
            "tool_calls": tool_calls,
            "skills_used": needed_skills,
            "cost": cost_info,
            "usage": {
                "input_tokens": usage.input_tokens,
                "cache_creation_tokens": getattr(usage, 'cache_creation_input_tokens', 0),
                "cache_read_tokens": getattr(usage, 'cache_read_input_tokens', 0),
                "output_tokens": usage.output_tokens
            },
            "response_time": response_time,
            "cache_hit": getattr(usage, 'cache_read_input_tokens', 0) > 0
        }
    
    async def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute tool calls"""
        
        results = []
        for tool_call in tool_calls:
            result = await self.tools.execute(
                tool_name=tool_call['name'],
                tool_input=tool_call['input']
            )
            results.append({
                "tool_call_id": tool_call['id'],
                "result": result
            })
        
        return results
    
    def _calculate_cost_with_cache(self, usage: Any) -> Dict[str, Any]:
        """Calculate cost with cache pricing breakdown"""
        
        # Claude Sonnet 4.5 pricing
        PROMPT_PRICE = 3.00 / 1_000_000
        CACHE_WRITE_PRICE = 3.75 / 1_000_000  # 25% more
        CACHE_READ_PRICE = 0.30 / 1_000_000   # 90% less!
        OUTPUT_PRICE = 15.00 / 1_000_000
        
        cache_creation = getattr(usage, 'cache_creation_input_tokens', 0)
        cache_read = getattr(usage, 'cache_read_input_tokens', 0)
        
        costs = {
            "prompt": usage.input_tokens * PROMPT_PRICE,
            "cache_write": cache_creation * CACHE_WRITE_PRICE,
            "cache_read": cache_read * CACHE_READ_PRICE,
            "output": usage.output_tokens * OUTPUT_PRICE
        }
        
        total_cost = sum(costs.values())
        
        # Calculate savings from caching
        savings = 0
        if cache_read > 0:
            would_have_paid = cache_read * PROMPT_PRICE
            actually_paid = cache_read * CACHE_READ_PRICE
            savings = would_have_paid - actually_paid
        
        return {
            "total": total_cost,
            "breakdown": costs,
            "savings": savings,
            "savings_percentage": (savings / (total_cost + savings) * 100) if savings > 0 else 0
        }
    
    def get_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get agent statistics"""
        
        if session_id:
            return self.conversation_manager.get_session_stats(session_id)
        
        return {
            "total_skills": len(self.skills),
            "skills_loaded": list(self.skills.keys()),
            "tools_available": len(self.tools.get_tool_definitions()),
            "active_sessions": self.conversation_manager.get_active_session_count()
        }
