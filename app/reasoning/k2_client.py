"""
K2 Think API Client
"""
from typing import List, Dict, Any, Optional
import httpx


class K2ThinkClient:
    """Client pour K2 Think API (OpenAI Compatible)"""
    
    def __init__(self, api_key: str, api_url: str = "https://api.k2think.ai/v1"):
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=300.0
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "MBZUAI-IFM/K2-Think-v2",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Envoie une requête de chat completion à K2 Think
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = await self.client.post(
                f"{self.api_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ValueError(f"K2 Think API error: {str(e)}")

