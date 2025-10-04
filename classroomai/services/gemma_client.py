import os
import json
from typing import List, Dict, Optional


def _get_api_key() -> str:
	"""取得 Google Generative AI API Key（沿用 Gemini 的 key）。
	支援環境變數名稱：Gemini_API_KEY（優先）、GEMINI_API_KEY。
	"""
	key = os.getenv("Gemini_API_KEY") or os.getenv("GEMINI_API_KEY")
	if not key:
		raise RuntimeError("Google API key not found. Set 'Gemini_API_KEY' or 'GEMINI_API_KEY'.")
	return key


def is_available() -> bool:
	return bool(os.getenv("Gemini_API_KEY") or os.getenv("GEMINI_API_KEY"))


def _get_model(model_name: Optional[str] = None):
    """回傳已設定好的 google.generativeai GenerativeModel。"""
    import google.generativeai as genai  # type: ignore
    genai.configure(api_key=_get_api_key())
    name = (
        model_name
        or os.getenv("GEMINI_MODEL")
        or os.getenv("GEMMA_MODEL")
        or "gemini-2.5-pro"
    )
    return genai.GenerativeModel(name)


def extract_timetable_from_image(image_bytes: bytes, model: Optional[str] = None) -> List[Dict]:
	"""以 Google 的 Gemma 模型解析課表圖片並回傳課程清單。"""
	if not is_available():
		raise RuntimeError("Google Generative AI Key 未設定。")

	model_inst = _get_model(model)
	system = (
		"""
		You are an assistant that extracts weekly class timetables from images and outputs STRICT JSON only.
		No markdown, no code fences, no explanations. Output must be a single JSON object.

		Schema:
		{"items":[{"title":string,"instructor":string,"classroom":string,
		"schedule":[{"day":string,"start":"HH:MM","end":"HH:MM"}]}]}
		- day: Chinese weekday name: "星期一","星期二","星期三","星期四","星期五","星期六","星期日" (required)

		Rules (CRITICAL for day/time accuracy):
		1) Day mapping: Determine correct weekday and return it as Chinese string in field "day" exactly as above.
		   Normalize variants:
		   - English: Mon/Tue/Wed/Thu/Fri/Sat/Sun (and full names)
		   - Chinese: 週/周/星期/禮拜 + 一/二/三/四/五/六/日/天
		   - Numeric 1..7 => Mon..Sun
		   If day cannot be determined with high confidence, SKIP that schedule entry (do not guess).

		2) Time extraction: Determine start/end from the timetable grid.
		   - Use row/column time headers as ground truth; convert to 24-hour HH:MM.
		   - If a cell spans multiple time slots, start = top slot start, end = bottom slot end.
		   - If explicit times appear inside the cell, prefer them when they are consistent with grid headers.
		   - Ignore seconds; always HH:MM.
		   If time is ambiguous, SKIP that schedule entry.

		3) Layout detection: Handle both horizontal and vertical timetables.
		   Correctly align class cells to their corresponding day headers and time headers.

		4) Consolidation: For the SAME day, merge contiguous or near-contiguous intervals (gap ≤ 10 minutes)
		   into one interval from earliest start to latest end.

		5) Aggregation: If title/instructor/classroom are identical, aggregate into one item and append
		   multiple schedule objects.

		6) Missing info: If instructor/classroom is absent, output empty string "" for that field.

		7) Output constraints: Valid JSON only; ensure all day_of_week are integers 0..6 and times are HH:MM.
		"""
	)

	# google.generativeai 支援以 bytes 傳入圖片
	resp = model_inst.generate_content([
		{"role": "user", "parts": [
			system,
			"Extract the timetable as structured JSON.",
			{"mime_type": "image/png", "data": image_bytes},
		]},
	])

	text = (getattr(resp, "text", None) or "").strip()
	print("[gemma.extract] model:", os.getenv("GEMINI_MODEL") or os.getenv("GEMMA_MODEL") or "gemini-2.0-flash-exp")
	print("[gemma.extract] raw_text:\n" + text)
	if text.startswith("```"):
		# 去除可能的 markdown 圍欄
		text = text.strip("`\n")
		first_nl = text.find("\n")
		if first_nl != -1:
			text = text[first_nl + 1 :]

	def _to_minutes(hm: str) -> int:
		try:
			h, m = hm.split(":")[:2]
			return int(h) * 60 + int(m)
		except Exception:
			return -1

	def _to_hm(minutes: int) -> str:
		h = minutes // 60
		m = minutes % 60
		return f"{h:02d}:{m:02d}"

	def _merge_schedules(schedules: List[Dict]) -> List[Dict]:
		# 以 day_of_week 分組，將同一天相鄰/重疊（間隔 ≤ 10 分鐘）時段合併，並保留中文星期 day
		by_day: Dict[int, List[Dict]] = {}
		for s in schedules:
			try:
				dow = int(s.get("day_of_week"))
				by_day.setdefault(dow, []).append(s)
			except Exception:
				continue
		merged: List[Dict] = []
		for dow, items in by_day.items():
			intervals = []
			for i in items:
				st = _to_minutes((i.get("start") or "").strip())
				et = _to_minutes((i.get("end") or "").strip())
				if st >= 0 and et >= 0 and et > st:
					intervals.append((st, et))
			intervals.sort(key=lambda x: x[0])
			if not intervals:
				continue
			curr_s, curr_e = intervals[0]
			for st, et in intervals[1:]:
				# 若相鄰/重疊（下一段開始 <= 當前結束 + 10 分），合併
				if st <= curr_e + 10:
					curr_e = max(curr_e, et)
				else:
					merged.append({
						"day_of_week": dow,
						"day": ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][dow],
						"start": _to_hm(curr_s),
						"end": _to_hm(curr_e),
					})
					curr_s, curr_e = st, et
			# 收尾
			merged.append({
				"day_of_week": dow,
				"day": ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][dow],
				"start": _to_hm(curr_s),
				"end": _to_hm(curr_e),
			})
		# 依 day_of_week 排序
		merged.sort(key=lambda x: int(x.get("day_of_week", 0)))
		return merged

	def _normalize_dow(value):
		# 目標：0=Mon .. 6=Sun
		if value is None:
			return None
		try:
			n = int(str(value).strip())
			if 0 <= n <= 6:
				return n
			if 1 <= n <= 7:
				return n - 1
		except Exception:
			pass
		s = str(value).strip().lower()
		map_en = {
			"mon": 0, "monday": 0,
			"tue": 1, "tues": 1, "tuesday": 1,
			"wed": 2, "wednesday": 2,
			"thu": 3, "thur": 3, "thurs": 3, "thursday": 3,
			"fri": 4, "friday": 4,
			"sat": 5, "saturday": 5,
			"sun": 6, "sunday": 6,
		}
		if s in map_en:
			return map_en[s]
		map_zh = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}
		for prefix in ["週", "周", "星期", "禮拜"]:
			if s.startswith(prefix) and len(s) >= len(prefix) + 1:
				ch = s[len(prefix):len(prefix)+1]
				if ch in map_zh:
					return map_zh[ch]
		return None

	try:
		data = json.loads(text or "{}")
		items = data.get("items", []) or []
		out: List[Dict] = []
		print("[gemma.extract] parsed_items_before_merge:", items)
		for it in items:
			title = (it.get("title") or "").strip()
			if not title:
				continue
			instructor = (it.get("instructor") or "").strip()
			classroom = (it.get("classroom") or "").strip()
			sched = []
			for s in (it.get("schedule") or []):
				try:
					dow = _normalize_dow(s.get("day_of_week") or s.get("day"))
					start = (s.get("start") or "").strip()
					end = (s.get("end") or "").strip()
					if dow is not None and 0 <= dow <= 6 and start and end:
						sched.append({"day_of_week": dow, "start": start, "end": end, "day": ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][dow]})
				except Exception:
					continue
			print(f"[gemma.extract] item='{title}' schedules_before_merge:", sched)
			# 合併同一天的多段時間
			sched = _merge_schedules(sched)
			print(f"[gemma.extract] item='{title}' schedules_after_merge:", sched)
			out.append({
				"title": title[:255],
				"instructor": instructor[:100],
				"classroom": classroom[:100],
				"schedule": sched,
			})
		return out
	except Exception as e:
		print(f"[gemma.extract] JSON parse failed: {e}\ntext=\n{text[:500]}...")
		return []

