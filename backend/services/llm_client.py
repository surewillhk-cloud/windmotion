"""OpenRouter LLM Client - Unified API for all model tiers.

OpenRouter provides access to DeepSeek-R1, DeepSeek-V3, Qwen-Turbo, etc.
through a single OpenAI-compatible API endpoint.

API: https://openrouter.ai/api/v1/chat/completions
Docs: https://openrouter.ai/docs
"""
import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any

import httpx

logger = logging.getLogger(__name__)

# OpenRouter API (OpenAI-compatible)
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# Model ID mapping for OpenRouter
OPENROUTER_MODELS = {
    # Heavy tier - reasoning models
    "deepseek-r1": "deepseek/deepseek-r1",
    "deepseek-r1-distill": "deepseek/deepseek-r1-distill-llama-70b",
    # Medium tier - general models
    "deepseek-v3": "deepseek/deepseek-chat-v3-0324",
    "deepseek-chat": "deepseek/deepseek-chat",
    "qwen-max": "qwen/qwen-max",
    "qwen-plus": "qwen/qwen-plus",
    # Light tier - fast/cheap models
    "qwen-turbo": "qwen/qwen-turbo",
    "qwen-turbo-latest": "qwen/qwen-turbo-latest",
    "gpt-4o-mini": "openai/gpt-4o-mini",
}


class LLMClient:
    """Unified LLM client using OpenRouter API.

    Features:
    - Single API key for all models
    - Automatic retry with fallback models
    - Circuit breaker per model tier
    - Token usage tracking
    - Cost estimation
    """

    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", OPENROUTER_BASE)
        self.config = config or {}
        self.client: Optional[httpx.AsyncClient] = None

        # Usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_calls = 0
        self.total_cost_usd = 0.0

        # Circuit breakers per model
        self._circuit_breakers: Dict[str, Dict] = {}

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://windmotion.io",
                    "X-Title": "Wind Motion",
                    "Content-Type": "application/json",
                },
                timeout=120.0,
            )
        return self.client

    async def close(self):
        if self.client and not self.client.is_closed:
            await self.client.aclose()

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek/deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Send a chat completion request to OpenRouter.

        Args:
            messages: Chat messages array
            model: OpenRouter model ID (e.g. "deepseek/deepseek-r1")
            temperature: Sampling temperature
            max_tokens: Max output tokens
            response_format: JSON mode etc.

        Returns:
            Dict with: success, content, model, usage, error
        """
        # Resolve model alias
        resolved_model = OPENROUTER_MODELS.get(model, model)

        # Check circuit breaker
        if self._is_circuit_broken(resolved_model):
            fallback = self._get_fallback(resolved_model)
            if fallback:
                logger.warning(f"Circuit broken for {resolved_model}, trying fallback: {fallback}")
                resolved_model = fallback
            else:
                return {"success": False, "error": f"Circuit broken for {resolved_model}, no fallback"}

        payload = {
            "model": resolved_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }
        if response_format:
            payload["response_format"] = response_format

        start_time = time.time()
        max_retries = 2

        for attempt in range(max_retries):
            try:
                client = await self._get_client()
                resp = await client.post("/chat/completions", json=payload)

                if resp.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = int(resp.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limited, waiting {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    continue

                resp.raise_for_status()
                data = resp.json()

                # Extract response
                choice = data.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content", "")
                usage = data.get("usage", {})

                # Track usage
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens
                self.total_calls += 1

                # Record success
                self._record_success(resolved_model)

                elapsed = time.time() - start_time
                logger.info(
                    f"LLM call: {resolved_model} | "
                    f"in={input_tokens} out={output_tokens} | "
                    f"{elapsed:.1f}s"
                )

                return {
                    "success": True,
                    "content": content,
                    "model": data.get("model", resolved_model),
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                    },
                    "elapsed_s": elapsed,
                }

            except httpx.HTTPStatusError as e:
                logger.error(f"LLM API error (attempt {attempt+1}): {e.response.status_code} - {e.response.text[:200]}")
                self._record_failure(resolved_model)

                if attempt < max_retries - 1:
                    # Try fallback
                    fallback = self._get_fallback(resolved_model)
                    if fallback:
                        logger.info(f"Retrying with fallback: {fallback}")
                        resolved_model = fallback
                        payload["model"] = fallback
                    await asyncio.sleep(1)

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                logger.error(f"LLM connection error (attempt {attempt+1}): {e}")
                self._record_failure(resolved_model)

                if attempt < max_retries - 1:
                    fallback = self._get_fallback(resolved_model)
                    if fallback:
                        resolved_model = fallback
                        payload["model"] = fallback
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"LLM unexpected error: {e}")
                return {"success": False, "error": str(e)}

        return {"success": False, "error": "All retries exhausted"}

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek/deepseek-chat",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        **kwargs,
    ) -> Dict[str, Any]:
        """Chat with JSON output mode. Parses response content as JSON."""
        result = await self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            **kwargs,
        )

        if result.get("success") and result.get("content"):
            try:
                result["json"] = json.loads(result["content"])
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code block
                content = result["content"]
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                    try:
                        result["json"] = json.loads(json_str)
                    except json.JSONDecodeError:
                        result["json_parse_error"] = True
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                    try:
                        result["json"] = json.loads(json_str)
                    except json.JSONDecodeError:
                        result["json_parse_error"] = True
                else:
                    result["json_parse_error"] = True

        return result

    def _is_circuit_broken(self, model: str) -> bool:
        cb = self._circuit_breakers.get(model)
        if not cb or not cb.get("broken"):
            return False
        # Auto-recover after 30 seconds
        if time.time() - cb.get("broken_at", 0) > 30:
            cb["broken"] = False
            cb["failures"] = 0
            return False
        return True

    def _record_failure(self, model: str):
        if model not in self._circuit_breakers:
            self._circuit_breakers[model] = {"failures": 0, "broken": False}
        cb = self._circuit_breakers[model]
        cb["failures"] = cb.get("failures", 0) + 1
        if cb["failures"] >= 3:
            cb["broken"] = True
            cb["broken_at"] = time.time()
            logger.warning(f"Circuit breaker opened for {model}")

    def _record_success(self, model: str):
        if model in self._circuit_breakers:
            self._circuit_breakers[model]["failures"] = 0
            self._circuit_breakers[model]["broken"] = False

    def _get_fallback(self, model: str) -> Optional[str]:
        """Get fallback model for a given model."""
        fallback_map = {
            "deepseek/deepseek-r1": "deepseek/deepseek-chat-v3-0324",
            "deepseek/deepseek-r1-distill-llama-70b": "deepseek/deepseek-chat-v3-0324",
            "deepseek/deepseek-chat-v3-0324": "qwen/qwen-max",
            "qwen/qwen-max": "deepseek/deepseek-chat-v3-0324",
            "qwen/qwen-turbo": "deepseek/deepseek-chat-v3-0324",
            "qwen/qwen-turbo-latest": "deepseek/deepseek-chat-v3-0324",
            "openai/gpt-4o-mini": "deepseek/deepseek-chat-v3-0324",
        }
        return fallback_map.get(model)

    def get_usage_summary(self) -> Dict:
        return {
            "total_calls": self.total_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "estimated_cost_usd": self.total_cost_usd,
        }


def create_llm_caller(llm_client: LLMClient, model_router=None):
    """Create an llm_caller function compatible with skill context injection.

    The returned async function signature matches what skills expect:
        llm_caller(task_type, system_prompt, user_prompt, **kwargs) -> Dict
    """

    async def llm_caller(
        task_type: str,
        system_prompt: str,
        user_prompt: str,
        model_tier: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
        **kwargs,
    ) -> Dict:
        """LLM caller function injected into skill context.

        Args:
            task_type: Task type for model routing (e.g. "graph_draft", "b_agent_reasoning")
            system_prompt: System message
            user_prompt: User message
            model_tier: Override tier ("heavy"/"medium"/"light")
            temperature: Sampling temperature
            max_tokens: Max output tokens
            json_mode: Whether to parse response as JSON

        Returns:
            Dict with: success, data (parsed content), error
        """
        # Determine model from tier
        tier = model_tier or "medium"
        if model_router:
            tier = model_router.get_tier_for_task(task_type)

        # Map tier to OpenRouter model
        tier_models = {
            "heavy": "deepseek/deepseek-r1",
            "medium": "deepseek/deepseek-chat-v3-0324",
            "light": "qwen/qwen-turbo-latest",
        }
        model = tier_models.get(tier, "deepseek/deepseek-chat-v3-0324")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if json_mode:
            result = await llm_client.chat_json(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            result = await llm_client.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        if result.get("success"):
            data = {
                "content": result["content"],
                "model": result.get("model"),
                "usage": result.get("usage"),
            }
            if json_mode and "json" in result:
                data["parsed"] = result["json"]
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}

    return llm_caller
