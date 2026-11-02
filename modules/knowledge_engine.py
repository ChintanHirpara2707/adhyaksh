"""
=============================================================================
ADHYAKSH AI // Universal World Knowledge & Intelligence Brain
Live Internet Knowledge (Google / Wikipedia / Gemini / Groq LLM Integration)
=============================================================================
"""

import os
import re
import urllib.parse
import warnings
warnings.filterwarnings("ignore")
import wikipedia

# Set custom User-Agent to comply with MediaWiki API guidelines
wikipedia.set_user_agent("AdhyakshAI_Assistant/3.5 (Executive OS; AML_Project)")

# Check optional LLM SDKs
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False


def clean_query_term(raw_query: str) -> str:
    """Extracts the core entity or subject from a natural language question."""
    q = raw_query.strip().rstrip("?").strip()
    patterns = [
        r"^(who is|who was|who are|who were)\s+",
        r"^(what is|what was|what are|what were)\s+",
        r"^(tell me about|tell about|explain|describe|define)\s+",
        r"^(how does|how do|how to|why is|why are)\s+",
        r"^(information about|details on|history of)\s+",
        r"^(kya hai|kaun hai|batao|kaho|shu che|kon che)\s+",
    ]
    for p in patterns:
        q = re.sub(p, "", q, flags=re.IGNORECASE).strip()
    return q or raw_query


def query_llm_generation(prompt: str, api_key: str = None, provider: str = "auto") -> tuple[bool, str]:
    """
    Queries Google Gemini or Groq LLM if an API key is available in environment or session.
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY", "")
    groq_key = api_key or os.getenv("GROQ_API_KEY", "")

    # 1. Google Gemini Generative Brain
    if HAS_GEMINI and (gemini_key and (provider in ["auto", "gemini"])):
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                f"You are ADHYAKSH AI, an executive multi-lingual autonomous assistant. Answer clearly, accurately, and professionally in markdown format:\n\n{prompt}"
            )
            if response and response.text:
                return True, f"**[ADHYAKSH AI Neural Brain (Gemini)]**\n\n{response.text}"
        except Exception as e:
            print("Gemini API generation error:", e)

    # 2. Groq Llama 3.3 Fast Inference
    if HAS_GROQ and (groq_key and (provider in ["auto", "groq"])):
        try:
            client = Groq(api_key=groq_key)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are ADHYAKSH AI, an executive multi-lingual AI assistant. Provide concise, professional, accurate answers."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=600,
            )
            answer = chat_completion.choices[0].message.content
            return True, f"**[ADHYAKSH AI Neural Brain (Groq Llama 3.3)]**\n\n{answer}"
        except Exception as e:
            print("Groq API generation error:", e)

    return False, ""


def fetch_world_knowledge(query_text: str, custom_api_key: str = None) -> tuple[bool, str, dict]:
    """
    Multi-Tier Universal World Knowledge Engine:
    Tier 1: Cloud LLM (Gemini / Groq) if API key configured.
    Tier 2: Live Wikipedia Encyclopedia Deep Knowledge Graph (Free, instant, no key required).
    Tier 3: Google Search Web Link Generation.
    
    Returns:
        tuple (success: bool, answer_markdown: str, metadata: dict)
    """
    clean_q = clean_query_term(query_text)
    metadata = {"query": clean_q}

    # Tier 1: Generative LLM Brain (If API Key Available)
    if custom_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY"):
        succ, llm_resp = query_llm_generation(query_text, api_key=custom_api_key)
        if succ and llm_resp:
            metadata["source"] = "Generative LLM"
            return True, llm_resp, metadata

    # Tier 2: Real-Time World Encyclopedia Knowledge Base
    try:
        # Search for closest matching articles
        search_results = wikipedia.search(clean_q, results=4)
        if search_results:
            target_title = search_results[0]
            try:
                page = wikipedia.page(target_title, auto_suggest=False)
                summary_text = page.summary
                # Truncate to reasonable length if too long
                sentences = summary_text.split(". ")
                formatted_summary = ". ".join(sentences[:5]) + "."

                google_search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(clean_q)}"

                answer = f"""**ADHYAKSH AI // Knowledge Engine:**

### 📖 **{page.title}**

{formatted_summary}

---
- 🔗 **Full Article:** [{page.title} on Wikipedia]({page.url})
- 🌐 **Live Web Search:** [Search Google for "{clean_q}"]({google_search_url})
"""
                metadata["title"] = page.title
                metadata["url"] = page.url
                metadata["source"] = "Wikipedia Knowledge Graph"
                return True, answer, metadata

            except wikipedia.DisambiguationError as dis_err:
                options = dis_err.options[:5]
                bullet_opts = "\n".join([f"- *\"{opt}\"*" for opt in options])
                return True, f"**ADHYAKSH AI Knowledge Engine:**\n\nYour query *\"{clean_q}\"* has multiple distinct entries. Please specify:\n\n{bullet_opts}", {"source": "Disambiguation"}

            except wikipedia.PageError:
                pass
    except Exception as e:
        print("Knowledge Search error:", e)

    # Tier 3: Unknown Query Fallback
    fallback_resp = f"""**ADHYAKSH AI // Knowledge Engine:**

I am sorry, I do not know about this message.

I do not have verified information about *\"{query_text}\"* in my neural knowledge base or memory bank yet.
- 💡 *You can teach me by saying:* `Remember that [fact]`
- ⚡ *Or train a new response:* `Train: [trigger] -> [response]`"""

    return False, fallback_resp, {"source": "Unknown Knowledge Base", "query": query_text}
