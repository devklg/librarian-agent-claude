"""
Bridge Connector - Connect to Universal Memory Bridge
(Optional component for connecting to existing database infrastructure)
"""

from typing import Dict, List, Optional
import sys

class BridgeConnector:
    """
    Connects the agent to the Universal Memory Bridge for database operations.
    This is an optional component that can be enabled when the Universal Memory
    Bridge is available.
    """
    
    def __init__(self, bridge_path: Optional[str] = None):
        """
        Initialize bridge connector
        
        Args:
            bridge_path: Optional path to Universal Memory Bridge module
        """
        self.bridge = None
        self.connected = False
        
        if bridge_path:
            try:
                sys.path.append(bridge_path)
                from universal_memory_bridge import UniversalMemoryBridge
                self.bridge = UniversalMemoryBridge()
                self.bridge.connect()
                self.connected = True
                print("✅ Connected to Universal Memory Bridge")
            except ImportError:
                print("⚠️  Universal Memory Bridge not found - running without database bridge")
            except Exception as e:
                print(f"⚠️  Failed to connect to Universal Memory Bridge: {e}")
    
    def is_connected(self) -> bool:
        """Check if bridge is connected"""
        return self.connected
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search the knowledge base
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.connected or not self.bridge:
            print("⚠️  Bridge not connected - returning empty results")
            return []
        
        try:
            return self.bridge.query_knowledge(query, n_results=n_results)
        except Exception as e:
            print(f"❌ Bridge search error: {e}")
            return []
    
    def store(self, module_data: dict) -> bool:
        """
        Store new knowledge module
        
        Args:
            module_data: Module data to store
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.bridge:
            print("⚠️  Bridge not connected - cannot store data")
            return False
        
        try:
            self.bridge.store_module(**module_data)
            return True
        except Exception as e:
            print(f"❌ Bridge store error: {e}")
            return False
    
    def get_health(self) -> Dict:
        """
        Check database health
        
        Returns:
            Health status dict
        """
        if not self.connected or not self.bridge:
            return {
                "status": "disconnected",
                "databases": {}
            }
        
        try:
            return self.bridge.get_health_status()
        except Exception as e:
            print(f"❌ Bridge health check error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "databases": {}
            }
    
    def query_specific_db(self, db_name: str, query: str) -> List[Dict]:
        """
        Query a specific database
        
        Args:
            db_name: Database name (chromadb, mongodb, neo4j, neon)
            query: Query string
            
        Returns:
            Query results
        """
        if not self.connected or not self.bridge:
            print(f"⚠️  Bridge not connected - cannot query {db_name}")
            return []
        
        try:
            if hasattr(self.bridge, f'query_{db_name}'):
                query_method = getattr(self.bridge, f'query_{db_name}')
                return query_method(query)
            else:
                print(f"⚠️  Database {db_name} not supported")
                return []
        except Exception as e:
            print(f"❌ Query {db_name} error: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Get bridge statistics
        
        Returns:
            Statistics dict
        """
        if not self.connected or not self.bridge:
            return {
                "connected": False,
                "total_modules": 0,
                "databases": {}
            }
        
        try:
            return {
                "connected": True,
                "total_modules": getattr(self.bridge, 'total_modules', 0),
                "databases": self.get_health().get("databases", {})
            }
        except Exception as e:
            print(f"❌ Bridge stats error: {e}")
            return {
                "connected": True,
                "error": str(e)
            }
