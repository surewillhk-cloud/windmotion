"""S9: Context Manage - Manages context windows and compression for agent interactions."""
import json
import time
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class ContextManage(BaseSkill):
    """Manages context windows for agent interactions, including compression and summarization."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S9_ContextManage"
        self.max_context_tokens = self.config.get("max_context_tokens", 8000)

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        action = inputs.get("action", "compress")
        llm_caller = context.get("llm_caller") if context else None

        if action == "compress":
            messages = inputs.get("messages", [])
            target_tokens = inputs.get("target_tokens", self.max_context_tokens)
            return await self._compress_context(messages, target_tokens, llm_caller, start_time)

        elif action == "merge":
            contexts = inputs.get("contexts", [])
            return self._merge_contexts(contexts, start_time)

        elif action == "summarize":
            text = inputs.get("text", "")
            return await self._summarize(text, llm_caller, start_time)

        return self._create_result(False, {}, f"Unknown action: {action}", start_time)

    async def _compress_context(self, messages: List[Dict], target_tokens: int,
                                 llm_caller, start_time: float) -> SkillResult:
        total_chars = sum(len(m.get("content", "")) for m in messages)
        estimated_tokens = total_chars // 3  # Rough estimate for Chinese text

        if estimated_tokens <= target_tokens:
            return self._create_result(True, {
                "action": "compress",
                "compressed_messages": messages,
                "original_tokens": estimated_tokens,
                "compressed_tokens": estimated_tokens,
                "compression_ratio": 1.0,
                "truncated": False
            }, start_time=start_time)

        if llm_caller:
            messages_text = "\n\n".join(
                f"[{m.get('role', 'user')}]: {m.get('content', '')[:500]}"
                for m in messages[-10:]
            )
            compress_prompt = f"""请压缩以下对话上下文，保留关键信息，控制在{target_tokens}个token以内。

{messages_text}

输出压缩后的摘要，保留所有关键事实、数据和决策。"""

            result = await llm_caller(
                model_tier="light",
                system_prompt="你是上下文压缩专家。保留关键信息，去除冗余。",
                user_message=compress_prompt,
                task_type="context_compression"
            )

            if result.get("success"):
                compressed = result.get("data", {}).get("summary", messages_text[:target_tokens * 3])
                return self._create_result(True, {
                    "action": "compress",
                    "compressed_messages": [{"role": "system", "content": compressed}],
                    "original_tokens": estimated_tokens,
                    "compressed_tokens": len(compressed) // 3,
                    "compression_ratio": round(len(compressed) / total_chars, 2),
                    "truncated": True
                }, start_time=start_time)

        # Fallback: simple truncation
        kept_messages = []
        current_chars = 0
        for msg in reversed(messages):
            msg_chars = len(msg.get("content", ""))
            if current_chars + msg_chars > target_tokens * 3:
                break
            kept_messages.insert(0, msg)
            current_chars += msg_chars

        return self._create_result(True, {
            "action": "compress",
            "compressed_messages": kept_messages,
            "original_tokens": estimated_tokens,
            "compressed_tokens": current_chars // 3,
            "compression_ratio": round(current_chars / total_chars, 2) if total_chars > 0 else 1.0,
            "truncated": True
        }, start_time=start_time)

    def _merge_contexts(self, contexts: List[Dict], start_time: float) -> SkillResult:
        merged = {}
        for ctx in contexts:
            for key, value in ctx.items():
                if key not in merged:
                    merged[key] = value
                elif isinstance(merged[key], list) and isinstance(value, list):
                    merged[key].extend(value)
                elif isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key].update(value)

        return self._create_result(True, {
            "action": "merge",
            "merged_context": merged,
            "sources_merged": len(contexts)
        }, start_time=start_time)

    async def _summarize(self, text: str, llm_caller, start_time: float) -> SkillResult:
        if llm_caller and len(text) > 2000:
            result = await llm_caller(
                model_tier="light",
                system_prompt="你是文本摘要专家。用简洁的中文概括核心内容。",
                user_message=f"请总结以下内容的核心要点（200字以内）：\n\n{text[:5000]}",
                task_type="context_compression"
            )
            if result.get("success"):
                summary = result.get("data", {}).get("summary", text[:500])
                return self._create_result(True, {
                    "action": "summarize",
                    "original_length": len(text),
                    "summary": summary,
                    "summary_length": len(summary)
                }, start_time=start_time)

        return self._create_result(True, {
            "action": "summarize",
            "original_length": len(text),
            "summary": text[:500] + "..." if len(text) > 500 else text,
            "summary_length": min(len(text), 500)
        }, start_time=start_time)

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "action" not in inputs:
            return False, "Missing 'action' in inputs"
        if inputs["action"] not in ("compress", "merge", "summarize"):
            return False, "action must be 'compress', 'merge', or 'summarize'"
        if inputs["action"] == "compress" and "messages" not in inputs:
            return False, "Missing 'messages' for compress action"
        if inputs["action"] == "merge" and "contexts" not in inputs:
            return False, "Missing 'contexts' for merge action"
        if inputs["action"] == "summarize" and "text" not in inputs:
            return False, "Missing 'text' for summarize action"
        return True, None
