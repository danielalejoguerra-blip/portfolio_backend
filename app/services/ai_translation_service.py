"""
AI-powered translation service using Google Gemini.

Translates Spanish content to English automatically.
Falls back gracefully if the API is unavailable.
"""
import json
import logging
from typing import Optional

from google import genai

from app.core.config import settings
from app.core.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

# Mapping of domain -> translatable field keys
TRANSLATABLE_FIELDS: dict[str, list[str]] = {
	"project": ["title", "description", "content"],
	"blog": ["title", "description", "content"],
	"course": ["description", "content"],
	"education": ["description", "content"],
	"experience": ["title", "description", "content"],
	"skill": ["description"],
	"personal_info": ["headline", "bio"],
}


class AITranslationService:
	"""Translates content fields from Spanish to English using Gemini."""

	def __init__(self) -> None:
		self._client: Optional[genai.Client] = None
		if settings.GEMINI_API_KEY:
			self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

	@property
	def available(self) -> bool:
		return self._client is not None

	def translate_fields(
		self,
		domain: str,
		fields: dict[str, Optional[str]],
		existing_translations: Optional[dict] = None,
		target_lang: str = "en",
	) -> dict[str, dict[str, str]]:
		"""
		Translate the given fields from Spanish to the target language.

		Args:
			domain: The content domain (e.g. "project", "blog", "skill").
			fields: Dict of field_name -> Spanish value to translate.
			existing_translations: Current translations dict from the entity.
				If a manual override exists for a field, it is preserved.
			target_lang: Target language code (default "en").

		Returns:
			Updated translations dict, e.g. {"en": {"title": "...", ...}}.
			Returns existing_translations unchanged if nothing to translate.
		"""
		if not self.available:
			logger.debug("AI translation skipped: no API key configured")
			return existing_translations or {}

		if target_lang == DEFAULT_LANGUAGE or target_lang not in SUPPORTED_LANGUAGES:
			return existing_translations or {}

		translatable_keys = TRANSLATABLE_FIELDS.get(domain, [])
		if not translatable_keys:
			return existing_translations or {}

		# Collect only non-empty fields that are translatable
		to_translate: dict[str, str] = {}
		for key in translatable_keys:
			value = fields.get(key)
			if value and isinstance(value, str) and value.strip():
				to_translate[key] = value

		if not to_translate:
			return existing_translations or {}

		# Build result from existing translations
		result = dict(existing_translations or {})
		existing_lang = result.get(target_lang, {})

		try:
			translated = self._call_gemini(to_translate, target_lang)
			# Merge: AI translations, but preserve any existing manual overrides
			# that were NOT in the current fields being translated
			merged = dict(existing_lang)
			merged.update(translated)
			result[target_lang] = merged
		except Exception:
			logger.exception("AI translation failed for domain=%s", domain)
			# Fail silently — don't break the create/update operation

		return result

	def _call_gemini(self, fields: dict[str, str], target_lang: str) -> dict[str, str]:
		"""Call Gemini API to translate field values."""
		lang_name = "English" if target_lang == "en" else target_lang

		# Build a structured prompt
		field_list = "\n".join(
			f'  "{key}": "{value}"' for key, value in fields.items()
		)

		prompt = (
			f"Translate the following JSON field values from Spanish to {lang_name}. "
			f"Return ONLY a valid JSON object with the same keys and translated values. "
			f"Do NOT translate proper nouns (company names, technology names, people names). "
			f"Keep any Markdown formatting, HTML tags, or URLs intact. "
			f"Do NOT add any explanation or extra text.\n\n"
			f"{{\n{field_list}\n}}"
		)

		response = self._client.models.generate_content(
			model="gemini-2.5-flash",
			contents=prompt,
		)

		# Parse the JSON response
		text = response.text.strip()
		# Remove markdown code block markers if present
		if text.startswith("```"):
			text = text.split("\n", 1)[1] if "\n" in text else text[3:]
		if text.endswith("```"):
			text = text[:-3].strip()
		if text.startswith("json"):
			text = text[4:].strip()

		return json.loads(text)
