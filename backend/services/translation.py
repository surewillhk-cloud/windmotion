"""Translation Service - Handles i18n for dynamic content."""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TranslationService:
    """Translates dynamic content (agent outputs, reports) to target languages."""

    SUPPORTED_LANGUAGES = ["zh-CN", "zh-TW", "en", "th", "ko", "ja", "vi"]

    # Direct translations for common terms
    TERM_TRANSLATIONS = {
        "入场时机": {"en": "Entry Timing", "th": "จังหวะเข้า", "ko": "진입 타이밍", "ja": "エントリータイミング", "vi": "Thời điểm vào"},
        "出场时机": {"en": "Exit Timing", "th": "จังหวะออก", "ko": "청산 타이밍", "ja": "イグジットタイミング", "vi": "Thời điểm ra"},
        "仓位管理": {"en": "Position Management", "th": "การจัดการตำแหน่ง", "ko": "포지션 관리", "ja": "ポジション管理", "vi": "Quản lý vị thế"},
        "Token选择": {"en": "Token Selection", "th": "การเลือก Token", "ko": "토큰 선택", "ja": "トークン選択", "vi": "Chọn Token"},
        "行为模式": {"en": "Behavior Pattern", "th": "รูปแบบพฤติกรรม", "ko": "행동 패턴", "ja": "行動パターン", "vi": "Mẫu hành vi"},
    }

    def __init__(self, llm_translate_func=None):
        self.llm_translate = llm_translate_func

    def translate_term(self, term: str, target_lang: str) -> str:
        """Translate a common term."""
        if target_lang in ("zh-CN", "zh-TW"):
            return term
        translations = self.TERM_TRANSLATIONS.get(term, {})
        return translations.get(target_lang, term)

    async def translate_text(self, text: str, target_lang: str, source_lang: str = "zh-CN") -> str:
        """Translate arbitrary text."""
        if target_lang == source_lang:
            return text
        if target_lang == "zh-TW":
            return self._simplified_to_traditional(text)

        if self.llm_translate:
            return await self.llm_translate(text, source_lang, target_lang)

        return text  # Fallback: return original

    def _simplified_to_traditional(self, text: str) -> str:
        """Convert simplified Chinese to traditional using OpenCC-style mapping."""
        # Simplified implementation - in production use opencc-python-reimplemented
        common_mappings = {
            "图": "圖", "数": "數", "据": "據", "分": "分", "析": "析",
            "报": "報", "告": "告", "链": "鏈", "交": "交", "易": "易",
            "时": "時", "机": "機", "选": "選", "择": "擇", "仓": "倉",
            "位": "位", "管": "管", "理": "理", "行": "行", "为": "為",
            "模": "模", "式": "式", "因": "因", "子": "子", "评": "評",
            "分": "分", "策": "策", "略": "略", "风": "風", "险": "險",
        }
        result = text
        for简, 繁 in common_mappings.items():
            result = result.replace(简, 繁)
        return result

    async def translate_report(self, report: Dict, target_lang: str) -> Dict:
        """Translate an entire report."""
        if target_lang in ("zh-CN",):
            return report

        translated = dict(report)
        if "summary" in report:
            translated["summary"] = await self.translate_text(report["summary"], target_lang)
        if "sections" in report:
            translated["sections"] = []
            for section in report["sections"]:
                t_section = dict(section)
                if "title" in section:
                    t_section["title"] = await self.translate_text(section["title"], target_lang)
                if "content" in section:
                    t_section["content"] = await self.translate_text(section["content"], target_lang)
                translated["sections"].append(t_section)

        return translated
