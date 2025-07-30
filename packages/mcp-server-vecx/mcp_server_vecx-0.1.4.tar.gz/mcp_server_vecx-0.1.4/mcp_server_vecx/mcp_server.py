import sys
from typing import Any, Dict, List, TypedDict
from fastmcp import Context, FastMCP
from pydantic import Field
from vecx.vectorx import VectorX 
from mcp_server_vecx.settings import VectorXSettings
from fastmcp.server.dependencies import get_http_headers

class VectorItem(TypedDict):
    id: str
    vector: List[float]
    meta: Dict[str,Any]


class VecXMCPServer(FastMCP):
    def __init__(
        self,
        vectorx_settings: VectorXSettings,
        name: str = "vecx-mcp-server",
        instructions: str | None = None,
        **settings: Any,
    ):
        self.vectorx_settings=vectorx_settings
        self.db_client=None
        if vectorx_settings.api_key is not None:
            self.db_client = VectorX(vectorx_settings.api_key)

        super().__init__(
            name=name, 
            instructions=instructions, 
            stateless_http=True, 
            json_response=True,
            **settings
        )
        
        self.setup_tools()
    
    def get_api_key(self) -> str:
        """Get API key from settings or headers"""
        if self.vectorx_settings.api_key:
            return self.vectorx_settings.api_key
        
        headers = get_http_headers()
        api_key = headers.get("vecx_api_key")
        
        if not api_key:
            raise ValueError("VectorX API key not found in environment or headers")
        
        return api_key

    def setup_tools(self):
        @self.tool()
        def create_index(name: str, dimension: int, space_type: str, is_encrypted: bool = False) -> dict:
            """Create an Index"""
            api_key = self.get_api_key()

            if self.db_client is None:
                self.db_client=VectorX(api_key)

            try:
                print(f"Creating index: {name}", file=sys.stderr)
                key = None
                if is_encrypted :
                    key=self.db_client.generate_key()
                self.db_client.create_index(
                    name=name,
                    dimension=dimension,
                    space_type=space_type,
                    key=key
                )
                print("Index created successfully", file=sys.stderr)
                return {
                    "status": "Success",
                    "message": "Index created successfully",
                    "data": {
                        "name": name,
                        "dimension": dimension,
                        "space_type": space_type,
                        "key": key
                    }
                }
            except Exception as e:
                print(f"Error while creating the index: {e}", file=sys.stderr)
                return {
                    "status": "Error",
                    "message": "Error creating Index",
                    "error": str(e)
                }
            
        @self.tool()
        def upsert_vectors(vector_list: List[VectorItem], index_name: str, encryption_key:str|None = None) -> dict:
            """Upsert vectors into an index"""
            api_key = self.get_api_key()

            if self.db_client is None:
                self.db_client=VectorX(api_key)
            try:
                index = self.db_client.get_index(index_name,encryption_key)
                index.upsert(vector_list)
                print("Upserted payload successfully", file=sys.stderr)
                return {
                    "status": "Success",
                    "message": f"Upserted {len(vector_list)} vectors in index {index_name} successfully"
                }
            except Exception as e:
                return {
                    "status": "Error",
                    "message": "Error upserting vectors",
                    "error": str(e)
                }

        @self.tool()
        def query_index(query_vector: List[float], top_k: int, index_name: str, encryption_key:str|None = None) -> dict:
            """Query an index with a vector"""
            api_key = self.get_api_key()

            if self.db_client is None:
                self.db_client=VectorX(api_key)
            
            try:
                index = self.db_client.get_index(index_name,encryption_key)
                result = index.query(
                    vector=query_vector,
                    top_k=top_k,
                )
                return {
                    "status": "Success",
                    "message": "Query successfull",
                    "data": {
                        "index_name": index_name,
                        "count": len(result),
                        "results": [{
                            "id": r["id"],
                            "similarity": r["similarity"],
                            "meta": r["meta"]
                        } for r in result]
                    }
                }
            except Exception as e:
                return {
                    "status": "Error",
                    "message": "Error querying index",
                    "error": str(e)
                }

        @self.tool()
        def delete_index(index_name: str) -> dict:
            """Delete an index"""
            api_key = self.get_api_key()

            if self.db_client is None:
                self.db_client=VectorX(api_key)

            try:
                self.db_client.delete_index(index_name)
                return {
                    "status": "success",
                    "message": f"Deleted index {index_name} successfully"
                }
            except Exception as e:
                return {
                    "status": "Error",
                    "message": f"Error deleting index {index_name}",
                    "error": str(e)
                }

        @self.tool()
        def test_connection() -> dict:
            """Test tool to verify the server is responding"""
            print("test tool called", file=sys.stderr)
            return {
                "status": "success",
                "message": "Server is working correctly",
                "client_status": "initialized" if self.db_client is not None else "not initialized"
            }

