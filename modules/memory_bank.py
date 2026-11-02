"""
=============================================================================
ADHYAKSH AI // Long-Term Memory Persistence & Recall Engine
Unifies and synchronizes persistent memory across data/memory_bank.json,
adhyaksh_memory.json, and the PyTorch Neural Brain.
=============================================================================
"""

import os
import re
import json
import datetime
from typing import Tuple, Dict, Any, List, Optional
from config import MEMORY_FILE, LEGACY_MEMORY_FILE, BASE_DIR, DATA_DIR

CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")
ADHYAKSH_ROOT_MEMORY = os.path.join(BASE_DIR, "adhyaksh_memory.json")
ROOT_MEMORY_BANK = os.path.join(BASE_DIR, "memory_bank.json")


def get_system_detected_username() -> str:
    """Auto-detects the operating system login username on the current laptop."""
    import getpass
    for cand in [
        os.getenv("USERNAME"),
        os.getenv("USER"),
        (getpass.getuser() if hasattr(getpass, "getuser") else None)
    ]:
        if cand and cand.strip() and cand.strip().lower() not in ["administrator", "system", "root", "default", "user"]:
            return cand.strip().capitalize()
    return "Neelkanth"


def get_active_user_name() -> str:
    """Returns the current user profile name for this laptop."""
    profile_path = os.path.join(DATA_DIR, "user_profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data.get("username"):
                    return data["username"].strip()
        except Exception:
            pass

    username_txt = os.path.join(BASE_DIR, "username.txt")
    if os.path.exists(username_txt):
        try:
            with open(username_txt, "r", encoding="utf-8") as f:
                for line in f:
                    if "username:" in line.lower():
                        u = line.split(":", 1)[1].strip()
                        if u:
                            return u
        except Exception:
            pass

    return get_system_detected_username()


def set_active_user_name(new_name: str) -> str:
    """Updates the active user profile across all files and memory banks."""
    clean_name = new_name.strip(" :,'\"<>")
    if not clean_name:
        clean_name = get_system_detected_username()

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # 1. Save to user_profile.json
    profile_path = os.path.join(DATA_DIR, "user_profile.json")
    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump({
                "username": clean_name,
                "updated_at": now_str,
                "workstation": os.environ.get("COMPUTERNAME", "Local Workstation")
            }, f, indent=2)
    except Exception:
        pass

    # 2. Save to username.txt
    username_txt = os.path.join(BASE_DIR, "username.txt")
    try:
        with open(username_txt, "w", encoding="utf-8") as f:
            f.write(f"# File: username.txt\n# Updated on {now_str}\nusername: {clean_name}\n")
    except Exception:
        pass

    # 3. Synchronize Memory Banks
    mems = load_memory()
    for k in list(mems.keys()):
        f_txt = mems[k].get("fact", "").lower() if isinstance(mems[k], dict) else str(mems[k]).lower()
        if any(phrase in f_txt for phrase in ["my name is", "my user's name is", "current workstation user is", "active user and operator"]):
            del mems[k]

    new_idx = len(mems) + 1
    mems[f"fact_{new_idx}"] = {
        "fact": f"My user's name is {clean_name}",
        "timestamp": now_str,
        "category": "User Profile"
    }
    mems[f"fact_{new_idx + 1}"] = {
        "fact": f"The active user and operator on this workstation is {clean_name}",
        "timestamp": now_str,
        "category": "User Profile"
    }
    save_memory(mems)

    return clean_name


# =============================================================================
# UNIFIED MEMORY SYNCHRONIZATION (Loads & Merges all memory files)
# =============================================================================

def load_memory() -> Dict[str, Dict[str, Any]]:
    """
    Loads and unifies all stored memories from all persistent JSON banks
    (MEMORY_FILE, ADHYAKSH_ROOT_MEMORY, ROOT_MEMORY_BANK), preventing any data loss.
    """
    merged_facts = {}
    known_fact_texts = set()

    # Priority files to read from
    candidate_paths = [
        MEMORY_FILE,
        ADHYAKSH_ROOT_MEMORY,
        ROOT_MEMORY_BANK,
        LEGACY_MEMORY_FILE
    ]

    for fpath in candidate_paths:
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, dict):
                            f_text = v.get("fact", "").strip()
                            t_stamp = v.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                            cat = v.get("category", "Learned Fact")
                        else:
                            f_text = str(v).strip()
                            t_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            cat = "Learned Fact"

                        if f_text and f_text.lower() not in known_fact_texts:
                            known_fact_texts.add(f_text.lower())
                            next_id = f"fact_{len(merged_facts) + 1}"
                            merged_facts[next_id] = {
                                "fact": f_text,
                                "timestamp": t_stamp,
                                "category": cat
                            }
            except Exception:
                pass

    # If completely empty, seed default memory
    if not merged_facts:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        merged_facts = {
            "fact_1": {"fact": "My assistant is named Adhyaksh AI", "timestamp": now_str, "category": "System Identity"},
            "fact_2": {"fact": "My lead engineer and user is Neelkanth", "timestamp": now_str, "category": "User Profile"},
            "fact_3": {"fact": "This project is built by Neelkanth (Lead Engineer)", "timestamp": now_str, "category": "Project Origin"},
            "fact_4": {"fact": "my favorite language is Python", "timestamp": now_str, "category": "Preferences"},
            "fact_5": {"fact": "my university is GTU", "timestamp": now_str, "category": "Education"}
        }
        save_memory(merged_facts)

    return merged_facts


def save_memory(memory_dict: Dict[str, Dict[str, Any]]) -> bool:
    """
    Saves memory dictionary to all persistent JSON banks in sync:
    - data/memory_bank.json
    - adhyaksh_memory.json (root)
    - memory_bank.json (root)
    """
    success = True
    targets = [MEMORY_FILE, ADHYAKSH_ROOT_MEMORY, ROOT_MEMORY_BANK]

    for fpath in targets:
        try:
            parent = os.path.dirname(fpath)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(memory_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing memory to {fpath}: {e}")
            success = False

    return success


def teach_memory(user_text: str, category: str = "Learned Fact") -> str:
    """Extracts a fact from user text and commits it to persistent memory across all banks."""
    mem_dict = load_memory()
    fact_text = user_text.strip()

    triggers = [
        "remember that", "remember this", "remember", "teach:", "teach", 
        "save fact", "learn fact", "store memory", "yaad rakho ki", 
        "yaad rakho", "yaad rakhjo"
    ]
    for trigger in triggers:
        if trigger in fact_text.lower():
            idx = fact_text.lower().find(trigger) + len(trigger)
            fact_text = fact_text[idx:].strip(" :,-")
            break

    if not fact_text:
        return "Please specify what you would like Adhyaksh AI to remember (e.g. *'Remember that my favorite book is Atomic Habits'*)."

    # Deduplicate exact facts
    for k, v in mem_dict.items():
        if v.get("fact", "").lower() == fact_text.lower():
            return f"I already have this in my memory bank:\n*\"{v.get('fact')}\"* `[Stored on {v.get('timestamp')}]`"

    new_id = f"fact_{len(mem_dict) + 1}"
    now_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    mem_dict[new_id] = {
        "fact": fact_text,
        "timestamp": now_stamp,
        "category": category
    }
    save_memory(mem_dict)

    # Sync with PyTorch model if active
    try:
        from model import get_model_manager
        mm = get_model_manager()
        if mm and hasattr(mm, "learn_fact"):
            mm.learn_fact(fact_text)
    except Exception:
        pass

    return f"🧠 **Adhyaksh AI Long-Term Memory Committed:**\n\n- **Fact:** *\"{fact_text}\"*\n- **Category:** `{category}`\n- **Committed:** `{now_stamp}`\n- **Persistence:** Synchronized across all neural stores."


def query_memory(search_term: Optional[str] = None) -> str:
    """Retrieves all or matching stored memories from the persistent JSON bank."""
    mem_dict = load_memory()
    if not mem_dict:
        return "Adhyaksh AI memory bank is currently empty. You can teach me facts by saying: *'Remember that my favorite project is Machine Learning'*."

    items = []
    for k, v in mem_dict.items():
        fact_str = v.get("fact", "")
        t_stamp = v.get("timestamp", "Earlier")
        cat = v.get("category", "General")
        if search_term:
            if search_term.lower() in fact_str.lower() or search_term.lower() in cat.lower():
                items.append(f"- **[{cat}]** *\"{fact_str}\"* `[{t_stamp}]`")
        else:
            items.append(f"- **[{cat}]** *\"{fact_str}\"* `[{t_stamp}]`")

    if not items and search_term:
        return f"No memories found matching query *'{search_term}'*."

    joined = "\n".join(items)
    return f"🧠 **Adhyaksh AI Long-Term Memory Bank ({len(items)} Stored Facts):**\n\n{joined}"


def delete_memory(fact_id: str) -> Tuple[bool, str]:
    """Deletes a specific memory by key across all stores."""
    mem_dict = load_memory()
    if fact_id in mem_dict:
        removed_fact = mem_dict.pop(fact_id)["fact"]
        save_memory(mem_dict)
        return True, f"Successfully removed *\"{removed_fact}\"* from long-term memory."
    return False, f"Memory key `{fact_id}` not found in memory bank."


def get_all_memories_list() -> List[Dict[str, Any]]:
    """Returns a clean list of all memories with their ID, fact, timestamp, and category."""
    mem_dict = load_memory()
    res = []
    for k, v in mem_dict.items():
        res.append({
            "id": k,
            "fact": v.get("fact", ""),
            "timestamp": v.get("timestamp", ""),
            "category": v.get("category", "Learned Fact")
        })
    return res


# =============================================================================
# INTELLIGENT FACT RETRIEVAL & AUTOMATIC FACT LEARNING
# =============================================================================

def search_memory_for_answer(query_text: str) -> Tuple[bool, str]:
    """
    Intelligently checks if the user's query asks about a fact stored in long-term memory.
    Supports English, Hindi, and Gujarati phrasing.
    Returns: (found: bool, answer: str)
    """
    mem_dict = load_memory()
    if not mem_dict:
        return False, ""

    clean = query_text.lower().strip().rstrip("?!.")

    # 1. Direct identity and creator queries
    if any(k in clean for k in ["my name", "who am i", "user name", "mera naam", "maru naam"]):
        curr_u = get_active_user_name()
        return True, f"👤 **From Long-Term Memory:**\n\nYour name is **{curr_u}** (active user on this workstation)."

    if any(k in clean for k in ["lead", "creator", "who made", "who created", "engineer"]):
        return True, "⚡ **From Long-Term Memory:**\n\nThis system was engineered by **Neelkanth** (Lead Engineer)."

    # 2. Extract salient topic words from question
    # Strip common interrogative phrases
    prefix_patterns = [
        r"^(what is my|what's my|what is the|who is my|who is|tell me my|tell me about my|do you know my|kya hai|kya yaad hai)\s+",
        r"^(where is my|where do i|which is my|which one is my|do you remember my|what do you know about my)\s+",
        r"^(maru|maro|mari|mera|meri|mere)\s+"
    ]
    for pat in prefix_patterns:
        clean = re.sub(pat, "", clean).strip()

    noise_words = {
        "my", "is", "the", "a", "an", "me", "about", "to", "for", "in", "on", "of",
        "do", "you", "know", "what", "where", "who", "which", "tell", "remember",
        "please", "kya", "su", "che", "hai", "tha", "chhe"
    }
    q_words = set(re.findall(r"\w+", clean)) - noise_words

    if not q_words:
        return False, ""

    best_fact = None
    best_score = 0.0

    for k, v in mem_dict.items():
        f_text = v.get("fact", "")
        f_text_lower = f_text.lower()
        f_words = set(re.findall(r"\w+", f_text_lower)) - noise_words

        # Handle QA pair format like "Question -> Answer"
        if "->" in f_text:
            parts = f_text.split("->", 1)
            q_part = parts[0].lower()
            a_part = parts[1].strip()
            q_part_words = set(re.findall(r"\w+", q_part)) - noise_words
            common_q = q_words.intersection(q_part_words)
            if common_q and len(common_q) >= min(len(q_words), 2):
                return True, f"🧠 **From Long-Term Memory:**\n\n**{a_part}**"

        # Check keyword overlap
        common = q_words.intersection(f_words)
        score = len(common) / len(q_words) if q_words else 0.0

        # Exact substring boost
        if clean in f_text_lower:
            score += 0.4

        if score > best_score:
            best_score = score
            best_fact = f_text

    if best_score >= 0.45 and best_fact:
        # Format the response cleanly
        return True, f"🧠 **From Long-Term Memory:**\n\n*\"{best_fact}\"*"

    return False, ""


def detect_and_remember_user_fact(text: str) -> Tuple[bool, str]:
    """
    Detects natural fact declarations like:
    - "my favorite fruit is mango"
    - "my car number is GJ-01-AB-1234"
    - "my email is alex@gmail.com"
    - "i live in Ahmedabad"
    - "my graduation year is 2026"
    Automatically commits them to long-term memory so they are never forgotten!
    Returns: (is_fact: bool, confirmation_message: str)
    """
    clean = text.strip()
    text_lower = clean.lower()

    # Avoid questions or commands
    if clean.endswith("?") or any(text_lower.startswith(q) for q in [
        "what", "who", "where", "when", "how", "why", "can you", "could you", "is my", "are you",
        "open ", "close ", "create ", "delete ", "launch ", "search ", "find "
    ]):
        return False, ""

    # Pattern 1: "my [attribute] is [value]"
    match_my_is = re.match(r"^my\s+([a-zA-Z0-9_\s]{2,35})\s+(?:is|was|are)\s+(.+)$", clean, re.IGNORECASE)
    if match_my_is:
        attr = match_my_is.group(1).strip()
        val = match_my_is.group(2).strip(" .!,")
        # Ensure it's not a noise sentence
        if attr.lower() not in ["name", "assistant", "screen", "mic", "query", "command"] and len(val) >= 1:
            fact_statement = f"my {attr.lower()} is {val}"
            teach_memory(fact_statement, category="Personal Attribute")
            return True, f"🧠 **Fact Remembered:**\n\nI have saved to long-term memory that **your {attr} is {val}**.\n\nWhenever you ask *'What is my {attr}?'*, I will recall this immediately!"

    # Pattern 2: "i live in [city]" / "i am located in [city]"
    match_live = re.match(r"^i\s+(?:live|reside|stay)\s+in\s+([a-zA-Z\s]{2,40})$", clean, re.IGNORECASE)
    if match_live:
        city = match_live.group(1).strip(" .!,")
        fact_statement = f"I live in {city}"
        teach_memory(fact_statement, category="Personal Location")
        return True, f"🧠 **Fact Remembered:**\n\nI have saved to long-term memory that you live in **{city}**."

    # Pattern 3: "my phone/mobile number is [num]"
    match_phone = re.match(r"^my\s+(?:phone|mobile|contact)\s+(?:number\s+)?is\s+([0-9\+\-\s]{7,16})$", clean, re.IGNORECASE)
    if match_phone:
        pnum = match_phone.group(1).strip(" .!,")
        fact_statement = f"my phone number is {pnum}"
        teach_memory(fact_statement, category="Contact Info")
        return True, f"🧠 **Fact Remembered:**\n\nI have saved your phone number (`{pnum}`) to persistent memory."

    # Pattern 4: "my email is [email]"
    match_email = re.match(r"^my\s+email\s+(?:address\s+)?is\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$", clean, re.IGNORECASE)
    if match_email:
        email_addr = match_email.group(1).strip(" .!,")
        fact_statement = f"my email is {email_addr}"
        teach_memory(fact_statement, category="Contact Info")
        return True, f"🧠 **Fact Remembered:**\n\nI have saved your email (`{email_addr}`) to persistent memory."

    return False, ""


# =============================================================================
# PERSISTENT CHAT HISTORY (Remembers conversation across reloads)
# =============================================================================

def load_chat_history() -> List[Dict[str, Any]]:
    """Loads past conversation messages from disk so chat is never lost on refresh."""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []


def save_chat_history(messages: List[Dict[str, Any]]) -> bool:
    """Saves current conversation messages to disk persistently."""
    try:
        os.makedirs(os.path.dirname(CHAT_HISTORY_FILE), exist_ok=True)
        # Keep last 100 messages to prevent excessive file bloat
        to_save = messages[-100:] if len(messages) > 100 else messages
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving chat history: {e}")
        return False


def clear_chat_history() -> bool:
    """Clears the persistent chat history file."""
    return save_chat_history([])
