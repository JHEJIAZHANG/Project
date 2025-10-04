import os
from typing import Optional

from openai import OpenAI


def _get_api_key() -> str:
	"""取得 DeepSeek API Key。
	支援環境變數名稱：DEEPSEEK（建議）、DEEPSEEK_API_KEY、DeepSeek_API_KEY。
	"""
	key = (
		os.getenv("DEEPSEEK")
		or os.getenv("DEEPSEEK_API_KEY")
		or os.getenv("DeepSeek_API_KEY")
	)
	if not key:
		raise RuntimeError("DeepSeek API key not found. Set 'DEEPSEEK'.")
	return key


def is_available() -> bool:
	return bool(os.getenv("DEEPSEEK") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("DeepSeek_API_KEY"))


def _client() -> OpenAI:
	base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
	return OpenAI(api_key=_get_api_key(), base_url=base_url)


def generate_json(prompt: str, system: Optional[str] = None, model: Optional[str] = None) -> str:
	"""以 DeepSeek 產生嚴格 JSON 字串（非流式）。"""
	client = _client()
	model_name = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
	sys_msg = (system or "") + "\nYou must output STRICT JSON only. No prose, no markdown."
	r = client.chat.completions.create(
		model=model_name,
		messages=[
			{"role": "system", "content": sys_msg},
			{"role": "user", "content": prompt},
		],
		stream=False,
	)
	text = (r.choices[0].message.content or "").strip()
	if text.startswith("```") and text.endswith("```"):
		text = text.strip("`\n")
		first_nl = text.find("\n")
		if first_nl != -1:
			text = text[first_nl + 1 :]
	return text



