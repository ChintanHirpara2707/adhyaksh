"""
=============================================================================
ADHYAKSH AI // Adaptive Learning & User Feedback Training Engine
Enables user-driven active learning, intent adaptation, and correction loops
=============================================================================
"""

import os
import json
import datetime
import re
from config import LEARNED_INTENTS_FILE

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Default seed training patterns to ensure rich initial capability
DEFAULT_TRAINING_PATTERNS = [
    {
        "pattern_id": "lp_001",
        "trigger": "start my coding workspace",
        "action": "open_app_and_drive",
        "parameters": {"app": "code", "drive": "D:\\"},
        "custom_response": "Coding workspace activated! Opened Visual Studio Code and navigated to D: drive.",
        "category": "Workspace Automation",
        "timestamp": "2026-10-21 12:00",
        "usage_count": 3
    },
    {
        "pattern_id": "lp_002",
        "trigger": "who is the project lead",
        "action": "custom_response",
        "parameters": {},
        "custom_response": "The project lead is Neelkanth, presiding over the Advanced Machine Learning system architecture.",
        "category": "Knowledge",
        "timestamp": "2026-10-21 12:05",
        "usage_count": 5
    },
    {
        "pattern_id": "lp_003",
        "trigger": "prepare daily progress report",
        "action": "create_file",
        "parameters": {"filename": "daily_progress_report.txt", "drive": "D:\\", "content": "# Daily Progress Report\nStatus: On Track\n"},
        "custom_response": "Created daily progress report on D: drive.",
        "category": "File Automation",
        "timestamp": "2026-10-21 12:10",
        "usage_count": 2
    },
    {
        "pattern_id": "lp_004",
        "trigger": "enter focus mode",
        "action": "mute_and_launch",
        "parameters": {"app": "spotify", "mute_toggle": False},
        "custom_response": "Focus mode initiated. Spotify launched for focus beats and audio muted.",
        "category": "Productivity",
        "timestamp": "2026-10-21 12:15",
        "usage_count": 1
    }
]

def _initialize_learning_store():
    """Initializes the training patterns file if not already present."""
    if not os.path.exists(LEARNED_INTENTS_FILE):
        try:
            with open(LEARNED_INTENTS_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_TRAINING_PATTERNS, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error initializing learned intents: {e}")

_initialize_learning_store()


def get_all_learned_patterns() -> list[dict]:
    """Retrieves all user-trained patterns from persistent storage."""
    _initialize_learning_store()
    try:
        with open(LEARNED_INTENTS_FILE, "r", encoding="utf-8") as f:
            patterns = json.load(f)
            if isinstance(patterns, list):
                return patterns
    except Exception:
        pass
    return []


def save_learned_patterns(patterns: list[dict]) -> bool:
    """Saves updated patterns list back to disk."""
    try:
        with open(LEARNED_INTENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(patterns, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving learned patterns: {e}")
        return False


def infer_action_from_text(output_text: str) -> tuple[str, dict, str]:
    """
    Intelligently inspects a user-provided training output to check if it's
    an action (like opening an app, website, or drive) or a verbal response.
    Returns: (action, parameters, custom_response)
    """
    clean = output_text.strip()
    clean_l = clean.lower()
    params = {}

    # 1. Direct URL or website navigation
    if clean_l.startswith("http://") or clean_l.startswith("https://") or re.search(r"\b[a-zA-Z0-9-]+\.(com|org|net|in|io)\b", clean_l):
        m = re.search(r"https?://[^\s]+|[a-zA-Z0-9-]+\.(com|org|net|in|io)[^\s]*", clean_l)
        url = m.group(0) if m else clean
        if not url.startswith("http"):
            url = "https://" + url
        return "open_website", {"url": url}, f"Opened website: {url}"

    # 2. Open website keyword (e.g. 'open youtube', 'open github')
    for site in ["youtube", "google", "github", "chatgpt", "linkedin", "gmail", "spotify", "netflix", "whatsapp"]:
        if f"open {site}" in clean_l or f"launch {site}" in clean_l:
            return "command", {"command": f"open {site}"}, f"Executing: open {site}"

    # 3. Open drive keyword (e.g. 'open d drive')
    for d_char in ["c", "d", "e", "f"]:
        if f"open {d_char} drive" in clean_l or f"{d_char} drive kholo" in clean_l:
            return "open_drive", {"drive": f"{d_char.upper()}:\\"}, f"Opened {d_char.upper()}: drive."

    # 4. Open app (e.g. 'open vs code', 'open chrome', 'launch notepad')
    for app_key in ["code", "vscode", "vs code", "chrome", "spotify", "notepad", "calculator", "calc", "taskmgr"]:
        if f"open {app_key}" in clean_l or f"launch {app_key}" in clean_l or f"start {app_key}" in clean_l:
            return "open_app", {"app": app_key}, f"Launched {app_key}."

    # 5. Create file (e.g. 'create file notes.txt in d drive')
    if clean_l.startswith("create file") or clean_l.startswith("make file"):
        return "command", {"command": clean}, f"Created file according to your instructions."

    # 6. Screenshot or mute
    if "screenshot" in clean_l:
        return "command", {"command": "take screenshot"}, "Captured desktop screenshot."
    if "mute" in clean_l:
        return "command", {"command": "mute volume"}, "Muted master audio."

    # Default: Custom Verbal / Text Response
    return "custom_response", {}, clean


def train_new_pattern(
    trigger: str,
    action: str = None,
    custom_response: str = "",
    parameters: dict = None,
    category: str = "User Feedback"
) -> tuple[bool, str, dict]:
    """
    Trains the AI on a new user trigger phrase and desired action/response.
    Supports continuous model updating with full persistence.
    """
    clean_trigger = trigger.strip().lower()
    clean_trigger = re.sub(r"^[,\.!\?:;\s]+|[,\.!\?:;\s]+$", "", clean_trigger)

    if not clean_trigger:
        return False, "Trigger phrase cannot be empty.", {}

    # Infer action if not explicitly given
    if not action or action == "custom_response":
        inferred_action, inferred_params, inferred_resp = infer_action_from_text(custom_response)
        action = inferred_action
        if not parameters:
            parameters = inferred_params
        if not custom_response:
            custom_response = inferred_resp

    patterns = get_all_learned_patterns()

    # Check if exact trigger already exists - update it in-place
    for pat in patterns:
        if pat.get("trigger", "").lower().strip() == clean_trigger:
            pat["action"] = action
            pat["custom_response"] = custom_response or pat.get("custom_response", "")
            pat["parameters"] = parameters or pat.get("parameters", {})
            pat["category"] = category
            pat["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            save_learned_patterns(patterns)
            return True, f"Updated existing learned pattern for trigger *'{clean_trigger}'*.", pat

    # Create new pattern
    new_id = f"lp_{len(patterns) + 1:03d}"
    new_pat = {
        "pattern_id": new_id,
        "trigger": clean_trigger,
        "action": action,
        "parameters": parameters or {},
        "custom_response": custom_response or f"Executed trained action '{action}'.",
        "category": category,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "usage_count": 0
    }
    patterns.append(new_pat)
    save_learned_patterns(patterns)
    return True, f"Successfully trained model on: *'{clean_trigger}'*!", new_pat


def clean_matching_query(text: str) -> str:
    """Removes conversational fluff words for accurate semantic matching."""
    q = text.lower().strip()
    q = re.sub(r"^[,\.!\?:;\s]+|[,\.!\?:;\s]+$", "", q)
    q = re.sub(r"^(please|can you|could you|kindly|hey|assistant|adhyaksh)\s+", "", q, flags=re.I)
    q = re.sub(r"^(tell me|give me|show me|what is|what's|who is|who's|explain)\s+", "", q, flags=re.I)
    q = re.sub(r"^(kripya|batao|kaho|shu che|kon che)\s+", "", q, flags=re.I)
    return q.strip()


def match_learned_intent(query_text: str, similarity_threshold: float = 0.55) -> tuple[bool, dict | None, float]:
    """
    Evaluates whether an incoming query matches any user-trained pattern using
    a robust 4-tier hybrid matcher:
    1. Exact Match
    2. Sub-phrase Containment
    3. Stop-Word Filtered TF-IDF Vectorization & Cosine Similarity
    4. Token Jaccard & Fuzzy Overlap
    Returns: (is_match: bool, matched_pattern: dict | None, confidence_score: float)
    """
    patterns = get_all_learned_patterns()
    if not patterns:
        return False, None, 0.0

    q_raw = query_text.strip().lower()
    q_clean = clean_matching_query(q_raw)

    # -----------------------------------------------------------------------
    # Tier 1: Exact Match (Normalized)
    # -----------------------------------------------------------------------
    for pat in patterns:
        trig = pat.get("trigger", "").lower().strip()
        trig_clean = clean_matching_query(trig)
        if q_raw == trig or (q_clean and q_clean == trig_clean):
            pat["usage_count"] = pat.get("usage_count", 0) + 1
            save_learned_patterns(patterns)
            return True, pat, 1.0

    # -----------------------------------------------------------------------
    # Tier 2: Sub-phrase Containment (Trigger inside query or query inside trigger)
    # -----------------------------------------------------------------------
    for pat in patterns:
        trig = pat.get("trigger", "").lower().strip()
        trig_clean = clean_matching_query(trig)
        
        # Check if full trigger is contained in user query
        if len(trig) >= 3 and (trig in q_raw or (trig_clean and trig_clean in q_clean)):
            pat["usage_count"] = pat.get("usage_count", 0) + 1
            save_learned_patterns(patterns)
            return True, pat, 0.95

        # Check if user query is contained in trigger
        if len(q_clean) >= 3 and (q_clean in trig or q_raw in trig):
            pat["usage_count"] = pat.get("usage_count", 0) + 1
            save_learned_patterns(patterns)
            return True, pat, 0.90

    # -----------------------------------------------------------------------
    # Tier 3: TF-IDF Cosine Similarity with Stop-Word & Coverage Weighting
    # -----------------------------------------------------------------------
    if HAS_SKLEARN and len(patterns) >= 1:
        try:
            corpus = [p.get("trigger", "").lower() for p in patterns]
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(corpus)
            target_q = q_clean if q_clean else q_raw
            q_words = re.findall(r"\w+", target_q.lower())

            if q_words:
                matched_words = [w for w in q_words if w in vectorizer.vocabulary_]
                coverage = len(matched_words) / len(q_words)
            else:
                coverage = 0.0

            query_vec = vectorizer.transform([target_q])
            sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

            best_idx = int(np.argmax(sim_scores))
            raw_score = float(sim_scores[best_idx])
            # Coverage weighting: prevents a single word out of a 10-word query causing a false positive
            effective_score = raw_score * min(1.0, coverage * 2.0)

            if effective_score >= similarity_threshold:
                matched_pat = patterns[best_idx]
                matched_pat["usage_count"] = matched_pat.get("usage_count", 0) + 1
                save_learned_patterns(patterns)
                return True, matched_pat, round(effective_score, 3)
        except Exception:
            pass

    # -----------------------------------------------------------------------
    # Tier 4: Token Jaccard Overlap
    # -----------------------------------------------------------------------
    q_tokens = set(re.findall(r"\w+", q_clean or q_raw))
    best_pat = None
    best_ratio = 0.0

    for pat in patterns:
        trig_tokens = set(re.findall(r"\w+", pat.get("trigger", "").lower()))
        if not trig_tokens:
            continue
        intersection = q_tokens.intersection(trig_tokens)
        union = q_tokens.union(trig_tokens)
        jaccard = len(intersection) / len(union) if union else 0.0

        if jaccard > best_ratio:
            best_ratio = jaccard
            best_pat = pat

    if best_ratio >= 0.50 and best_pat:
        best_pat["usage_count"] = best_pat.get("usage_count", 0) + 1
        save_learned_patterns(patterns)
        return True, best_pat, round(best_ratio, 3)

    return False, None, 0.0


def delete_learned_pattern(pattern_id: str) -> tuple[bool, str]:
    """Deletes a learned pattern by ID."""
    patterns = get_all_learned_patterns()
    filtered = [p for p in patterns if p.get("pattern_id") != pattern_id]
    if len(filtered) < len(patterns):
        save_learned_patterns(filtered)
        return True, f"Pattern `{pattern_id}` successfully removed from training storage."
    return False, f"Pattern `{pattern_id}` not found."


def get_training_statistics() -> dict:
    """Calculates operational metrics of the self-learning engine."""
    patterns = get_all_learned_patterns()
    total_samples = len(patterns)
    total_invocations = sum(p.get("usage_count", 0) for p in patterns)
    categories = {}
    for p in patterns:
        cat = p.get("category", "General")
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_patterns": total_samples,
        "total_invocations": total_invocations,
        "categories": categories,
        "vectorizer_active": HAS_SKLEARN,
        "last_trained": patterns[-1].get("timestamp") if patterns else "None"
    }


def parse_natural_training_command(text: str) -> tuple[str, str] | tuple[None, None]:
    """
    Parses conversational user training inputs like:
    - 'Train: [trigger] -> [output]'
    - 'When I say [trigger], do/reply [output]'
    - 'If I say [trigger], then [output]'
    - 'Train: [trigger] means [output]'
    - 'Train model: [trigger] = [output]'
    """
    clean = text.strip()
    clean_l = clean.lower()

    # Pattern 1: Arrow syntax: 'Train: X -> Y', 'Teach: X -> Y', 'X => Y'
    if "->" in clean or "=>" in clean:
        arrow = "->" if "->" in clean else "=>"
        parts = clean.split(arrow, 1)
        trig = re.sub(r"^(train\s*:?|teach\s*:?|learn\s*:?)\s*(model\s*:?)?\s*", "", parts[0], flags=re.I).strip(" :,-'\"")
        resp = parts[1].strip()
        if trig and resp:
            return trig, resp

    # Pattern 2: 'when I say X (reply|answer|say|do|then) Y'
    m = re.search(r"(?:train\s*:?\s*)?when\s+i\s+say\s+['\"]?(.+?)['\"]?\s*[,:]?\s*(?:then\s+reply|then\s+say|then\s+do|reply|answer|say|do|then|respond with)\s+['\"]?(.+)['\"]?$", clean, re.I)
    if m:
        return m.group(1).strip(" '\""), m.group(2).strip(" '\"")

    # Pattern 3: 'if I say X (reply|answer|say|do|then) Y'
    m = re.search(r"(?:train\s*:?\s*)?if\s+i\s+say\s+['\"]?(.+?)['\"]?\s*[,:]?\s*(?:then\s+reply|then\s+say|then\s+do|reply|answer|say|do|then|respond with)\s+['\"]?(.+)['\"]?$", clean, re.I)
    if m:
        return m.group(1).strip(" '\""), m.group(2).strip(" '\"")

    # Pattern 4: 'Train: X means Y' or 'Train: X is Y' or 'Train: X = Y'
    m = re.search(r"^(?:train\s*:?|teach\s*:?|learn\s*:?)\s*(?:model\s*:?)?\s*(.+?)\s+(?:means|is|=|should be)\s+(.+)$", clean, re.I)
    if m:
        return m.group(1).strip(" '\""), m.group(2).strip(" '\"")

    # Pattern 5: 'Train: X do Y'
    if " do " in clean_l and (clean_l.startswith("train") or clean_l.startswith("teach")):
        sub = re.sub(r"^(train\s*:?|teach\s*:?)\s*", "", clean, flags=re.I)
        parts = re.split(r"\s+do\s+", sub, flags=re.I, maxsplit=1)
        if len(parts) == 2:
            return parts[0].strip(" '\""), parts[1].strip(" '\"")

    return None, None
