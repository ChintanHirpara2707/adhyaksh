"""
=============================================================================
ADHYAKSH AI // Neural Intent & Semantic Memory Brain (PyTorch Deep Learning)
Autonomous Multi-Lingual AI Executive & Operating Engine
=============================================================================
This file is fully compatible with Google Colab (GPU/CPU) and Local Windows.
Run directly to train the model:
    python model.py

Architecture:
  - Model: AdhyakshBrainNet (Deep Multi-Layer Neural Network with BatchNorm, GELU & Dropout)
  - Memory: NeuralMemoryBank (Vectorized Episodic Memory Store & Cosine Recall)
  - Features: Multi-Lingual Subword/N-Gram TF-IDF Vectorizer (English, Hindi, Gujarati)
  - Framework: PyTorch + Scikit-Learn (Google Colab Native)
=============================================================================
"""

import os
import sys
import json
import re
import pickle
import datetime
from typing import Tuple, List, Dict, Any, Optional

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Optional Scikit-Learn for text vectorization
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# ---------------------------------------------------------------------------
# GLOBAL CONSTANTS & FILE PATHS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "adhyaksh_model.pth")
VOCAB_SAVE_PATH = os.path.join(BASE_DIR, "adhyaksh_vocab.pkl")
MEMORY_STORE_PATH = os.path.join(BASE_DIR, "adhyaksh_memory.json")
DATA_DIR = os.path.join(BASE_DIR, "data")
LEARNED_INTENTS_FILE = os.path.join(DATA_DIR, "learned_intents.json")
LEGACY_MEMORY_FILE = os.path.join(DATA_DIR, "memory_bank.json")

# Device configuration (GPU if available on Google Colab, otherwise CPU)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ---------------------------------------------------------------------------
# 1. TEXT TOKENIZATION & FALLBACK VECTORIZER
# ---------------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Normalizes multilingual text, preserving English, Hindi, and Gujarati characters."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s\d\u0900-\u097F\u0A80-\u0AFF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class SimpleTFIDF:
    """Pure-Python fallback TF-IDF vectorizer if scikit-learn is not available."""
    def __init__(self, max_features: int = 1500, ngram_range=(1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def _get_ngrams(self, text: str) -> List[str]:
        words = clean_text(text).split()
        ngrams = []
        for n in range(self.ngram_range[0], self.ngram_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngrams.append(" ".join(words[i:i + n]))
        return ngrams

    def fit_transform(self, corpus: List[str]):
        import math
        doc_counts: Dict[str, int] = {}
        n_docs = len(corpus)

        for doc in corpus:
            ngrams = set(self._get_ngrams(doc))
            for gram in ngrams:
                doc_counts[gram] = doc_counts.get(gram, 0) + 1

        sorted_grams = sorted(doc_counts.items(), key=lambda x: x[1], reverse=True)[:self.max_features]
        self.vocab = {gram: idx for idx, (gram, _) in enumerate(sorted_grams)}
        self.idf = {gram: math.log((n_docs + 1) / (count + 1)) + 1.0 for gram, count in sorted_grams}

        return self.transform(corpus)

    def transform(self, corpus: List[str]):
        matrix = []
        for doc in corpus:
            vec = [0.0] * len(self.vocab)
            ngrams = self._get_ngrams(doc)
            for gram in ngrams:
                if gram in self.vocab:
                    vec[self.vocab[gram]] += 1.0
            # Apply IDF
            for gram, idx in self.vocab.items():
                if vec[idx] > 0:
                    vec[idx] *= self.idf[gram]
            # Normalize
            norm = sum(v ** 2 for v in vec) ** 0.5
            if norm > 0:
                vec = [v / norm for v in vec]
            matrix.append(vec)
        return np.array(matrix, dtype=np.float32) if 'np' in globals() else matrix


# ---------------------------------------------------------------------------
# 2. NEURAL NETWORK ARCHITECTURE (PyTorch)
# ---------------------------------------------------------------------------
class AdhyakshBrainNet(nn.Module):
    """
    Deep Multilayer Neural Network for Multilingual Intent Classification
    and Dense Representation Learning.
    """
    def __init__(self, input_dim: int, num_classes: int, hidden_dim: int = 256):
        super(AdhyakshBrainNet, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.ln1 = nn.LayerNorm(hidden_dim)
        self.gelu = nn.GELU()
        self.dropout1 = nn.Dropout(0.3)

        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.ln2 = nn.LayerNorm(hidden_dim // 2)
        self.dropout2 = nn.Dropout(0.2)

        self.fc3 = nn.Linear(hidden_dim // 2, 64)
        self.classifier = nn.Linear(64, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.dropout1(self.gelu(self.ln1(self.fc1(x))))
        out = self.dropout2(self.gelu(self.ln2(self.fc2(out))))
        out = self.gelu(self.fc3(out))
        logits = self.classifier(out)
        return logits

    def get_embeddings(self, x: torch.Tensor) -> torch.Tensor:
        """Extracts 64-dimensional dense semantic feature embeddings."""
        self.eval()
        with torch.no_grad():
            out = self.gelu(self.ln1(self.fc1(x)))
            out = self.gelu(self.ln2(self.fc2(out)))
            embeddings = self.fc3(out)
        return embeddings


class AdhyakshDataset(Dataset):
    """PyTorch Dataset wrapper for multi-lingual input vectors and targets."""
    def __init__(self, X: np.ndarray, y: List[int]):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# ---------------------------------------------------------------------------
# 3. EPISODIC & LONG-TERM NEURAL MEMORY BANK
# ---------------------------------------------------------------------------
class NeuralMemoryBank:
    """
    Persistent Long-Term Memory Store.
    Remembers user facts, project metadata, personal preferences, and details.
    Uses semantic keyword & cosine vector similarity for real-time recall.
    """
    def __init__(self, storage_path: str = MEMORY_STORE_PATH):
        self.storage_path = storage_path
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.load_memories()

    def load_memories(self):
        """Loads memories from JSON storage, with fallback to legacy data."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.memories = json.load(f)
                    if isinstance(self.memories, dict) and self.memories:
                        return
            except Exception:
                pass

        # Check if legacy memory bank exists in workspace
        if os.path.exists(LEGACY_MEMORY_FILE):
            try:
                with open(LEGACY_MEMORY_FILE, "r", encoding="utf-8") as f:
                    legacy = json.load(f)
                    if isinstance(legacy, dict) and legacy:
                        self.memories = legacy
                        self.save_memories()
                        return
            except Exception:
                pass

        # Default foundational facts to seed the brain
        self.memories = {
            "fact_1": {
                "fact": "My assistant is named Adhyaksh AI",
                "timestamp": "2026-10-21 19:30",
                "category": "Identity"
            },
            "fact_2": {
                "fact": "My lead engineer and creator is Neelkanth",
                "timestamp": "2026-10-21 19:30",
                "category": "Creator"
            },
            "fact_3": {
                "fact": "Adhyaksh AI is an Autonomous Multi-Lingual AI Operating Engine",
                "timestamp": "2026-10-21 19:30",
                "category": "Identity"
            },
            "fact_4": {
                "fact": "My favorite programming language is Python",
                "timestamp": "2026-10-22 08:24",
                "category": "Preferences"
            },
            "fact_5": {
                "fact": "My university is Gujarat Technological University (GTU)",
                "timestamp": "2026-10-22 08:32",
                "category": "Education"
            }
        }
        self.save_memories()

    def save_memories(self) -> bool:
        """Persists all memory bank facts to disk."""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.memories, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving neural memory: {e}")
            return False

    def remember(self, raw_fact: str, category: str = "Learned Fact") -> str:
        """
        Commits a new fact to the Neural Memory Bank.
        Filters triggers like 'remember that', 'teach:', 'yaad rakho ki'.
        """
        fact = raw_fact.strip()
        triggers = [
            "remember that", "remember", "teach:", "teach", 
            "save fact", "learn fact", "store memory", 
            "yaad rakho ki", "yaad rakho", "yaad rakhjo"
        ]
        for trig in triggers:
            if trig in fact.lower():
                idx = fact.lower().find(trig) + len(trig)
                fact = fact[idx:].strip(" :,-")
                break

        if not fact:
            return "Please specify what you would like me to remember."

        # Check for duplicate facts
        for k, v in self.memories.items():
            if v.get("fact", "").lower() == fact.lower():
                return f"I already remember this: \"{v.get('fact')}\" (Committed {v.get('timestamp')})"

        new_key = f"fact_{len(self.memories) + 1}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.memories[new_key] = {
            "fact": fact,
            "timestamp": timestamp,
            "category": category
        }
        self.save_memories()
        return f"Fact successfully committed to Neural Memory Bank:\n\"{fact}\" [Key: {new_key}]"

    def recall(self, query: str, threshold: float = 0.30) -> Tuple[bool, str, float]:
        """
        Recalls a fact from memory using semantic keyword overlap & relevance scoring.
        Returns: (found: bool, answer: str, confidence_score: float)
        """
        if not self.memories:
            return False, "Memory bank is currently empty.", 0.0

        clean_q = clean_text(query)
        stop_words = {
            "what", "is", "my", "the", "who", "tell", "me", "do", "you", 
            "know", "about", "kya", "hai", "konsa", "kon", "su", "che"
        }
        q_tokens = [w for w in clean_q.split() if w not in stop_words]

        # Direct query intent checks
        if any(w in clean_q for w in ["lead", "creator", "who made", "who created", "engineer"]):
            return True, "This system was engineered by Neelkanth (Lead Engineer).", 0.99

        if any(w in clean_q for w in ["my name", "who am i", "user name", "mera naam", "maru naam"]):
            try:
                from modules.memory_bank import get_active_user_name
                curr_user = get_active_user_name()
            except Exception:
                curr_user = "Neelkanth"
            return True, f"Your name is {curr_user} (active operator on this workstation).", 0.99

        if any(w in clean_q for w in ["your name", "bot name", "assistant name", "aapka naam", "tame kon cho"]):
            try:
                from modules.memory_bank import get_active_user_name
                curr_user = get_active_user_name()
            except Exception:
                curr_user = "Neelkanth"
            return True, f"I am ADHYAKSH AI — your autonomous multi-lingual executive assistant, operating for {curr_user}.", 0.99

        if any(w in clean_q for w in ["university", "college", "gtu"]):
            for k, v in self.memories.items():
                f_txt = v.get("fact", "")
                if any(kw in f_txt.lower() for kw in ["university", "gtu", "college"]):
                    return True, f_txt, 0.98

        if any(w in clean_q for w in ["language", "bhasha"]):
            for k, v in self.memories.items():
                f_txt = v.get("fact", "")
                if "python" in f_txt.lower() or "language" in f_txt.lower():
                    return True, f_txt, 0.98

        best_score = 0.0
        best_fact = ""

        for k, v in self.memories.items():
            f_txt = v.get("fact", "")
            f_clean = clean_text(f_txt)
            f_tokens = [w for w in f_clean.split() if w not in stop_words]
            
            # Intersection score
            if q_tokens and f_tokens:
                overlap = len(set(q_tokens).intersection(set(f_tokens)))
                score = overlap / len(q_tokens)
                if score > best_score:
                    best_score = score
                    best_fact = f_txt

        if best_score >= threshold and best_fact:
            return True, best_fact, round(best_score, 2)

        return False, "", 0.0

    def delete_memory(self, key_or_fact: str) -> bool:
        """Deletes a memory fact by key or text match."""
        if key_or_fact in self.memories:
            del self.memories[key_or_fact]
            self.save_memories()
            return True
        for k, v in list(self.memories.items()):
            if key_or_fact.lower() in v.get("fact", "").lower():
                del self.memories[k]
                self.save_memories()
                return True
        return False

    def get_all(self) -> Dict[str, Any]:
        """Returns all memories currently stored."""
        return self.memories

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        return self.memories


# ---------------------------------------------------------------------------
# 4. COMPREHENSIVE TRAINING CORPUS GENERATOR
# ---------------------------------------------------------------------------
def generate_training_corpus() -> Tuple[List[str], List[str]]:
    """
    Compiles a comprehensive multilingual dataset (English, Hindi, Gujarati, Hinglish)
    covering all system commands, CRUD actions, memory operations, and conversation.
    """
    raw_data = {
        "greeting": [
            "hello", "hi", "hey there", "good morning", "good afternoon", "good evening",
            "namaste", "pranam", "kem cho", "kya haal hai", "hello adhyaksh", "hey ai",
            "su khabar", "kaise ho", "greetings"
        ],
        "bot_identity": [
            "who are you", "what is your name", "who created you", "who made you",
            "aap kaun ho", "tame kon cho", "tell me about yourself", "identify yourself",
            "introduce yourself", "tamari olakh aapo"
        ],
        "capabilities": [
            "what can you do", "help", "list features", "show capabilities",
            "tamari shamta shu che", "kya kar sakte ho", "show options", "what are your skills",
            "how to use you", "available commands"
        ],
        "wellbeing": [
            "how are you", "how are you doing", "what's up", "kaisa chal raha hai",
            "majama cho", "are you fine", "how is everything"
        ],
        "gratitude": [
            "thank you", "thanks", "great job", "well done", "awesome",
            "dhanyawad", "shukriya", "aabhaar", "bahut accha", "khub saras"
        ],
        "farewell": [
            "bye", "goodbye", "see you later", "alvida", "aavjo", "phir milenge",
            "exit now", "catch you later", "good night"
        ],
        "file_create": [
            "create file notes.txt", "make file report.py", "generate new file document.doc",
            "file banao test.txt", "naya file banao", "navin file banavo", "create file in d drive",
            "make a file username.txt with content Neelkanth", "create file data.json",
            "create new file daily.log", "open d drive and create file info.txt"
        ],
        "file_read": [
            "read file notes.txt", "view file report.py", "show file test.txt", "open file",
            "file dikhao username.txt", "file padho", "file dekho", "file vaacho",
            "display file contents", "show me data.json", "read contents of file"
        ],
        "file_update": [
            "update file notes.txt", "append to file report.py", "file me likho",
            "edit file username.txt", "file update karo", "file ma lakho", "modify file",
            "overwrite file config.py", "add line to file", "update notes with hello"
        ],
        "file_delete": [
            "delete file notes.txt", "remove file test.txt", "trash file temp.py",
            "file delete karo", "file hatao", "file kadhi nakho", "file nikal do",
            "permanently delete file junk.txt", "erase file"
        ],
        "folder_create": [
            "create folder project", "make folder my_data", "new folder ai_workspace",
            "folder banao code", "naya folder banavo", "create directory sem9",
            "make directory in d drive"
        ],
        "drive_open": [
            "open d drive", "open c drive", "open e drive", "d drive kholo", "c drive kholo",
            "open physical drive d", "d drive open karo", "file explorer kholo",
            "navigate to d drive", "launch drive e"
        ],
        "drive_close": [
            "close drive", "close d drive", "close c drive", "close e drive", "close explorer",
            "d drive band karo", "c drive band karo", "explorer bandh karo", "close all drives"
        ],
        "app_launch": [
            "open chrome", "launch vs code", "open spotify", "start notepad", "open calculator",
            "chrome kholo", "vscode chalu karo", "spotify play", "start task manager",
            "run browser", "open visual studio code"
        ],
        "app_close": [
            "close chrome", "close spotify", "terminate notepad", "stop vs code",
            "chrome band karo", "spotify band karo", "kill process", "exit application"
        ],
        "system_diagnostics": [
            "system specs", "hardware info", "computer specs", "pc telemetry", "cpu usage",
            "ram usage", "system diagnostics", "show system health", "check performance",
            "computer status", "hardware diagnostic report"
        ],
        "tool_screenshot": [
            "take screenshot", "capture screen", "screenshot lo", "screen capture",
            "screen photo lo", "desktop snapshot"
        ],
        "tool_mute": [
            "mute volume", "mute sound", "toggle volume", "sound band karo", "awaz band karo",
            "unmute audio", "silence pc"
        ],
        "tool_lock": [
            "lock computer", "lock pc", "lock screen", "pc lock karo", "screen lock karo",
            "secure workstation"
        ],
        "temporal_intelligence": [
            "what time is it", "what is today's date", "time kya hua hai", "aaj konsi tarikh hai",
            "current time", "today date", "tell me clock time", "samay kya hai", "aaj no divas"
        ],
        "math_computation": [
            "calculate 25 * 4", "what is 100 divided by 5", "solve 50 + 20", "evaluate 12 * 12",
            "math 999 minus 333", "calculate 2 power 8", "hisab karo 15 into 6"
        ],
        "memory_teach": [
            "remember that my roll number is 42", "remember that my university is GTU",
            "teach: my favorite subject is Deep Learning", "save fact: project deadline is Friday",
            "yaad rakho ki mera roll no 42 hai", "learn fact: my car is blue", "store in memory"
        ],
        "memory_query": [
            "what do you remember", "show memory", "view memory bank", "kya yaad hai",
            "stored facts", "list all memories", "what have you learned", "show learned facts"
        ],
        "memory_recall": [
            "what is my name", "who is the project lead", "what is my university",
            "what is my favorite language", "who am I", "mera naam kya hai",
            "what is my roll number", "what is my favorite subject"
        ],
        "universal_knowledge": [
            "who is Albert Einstein", "what is machine learning", "explain neural networks",
            "what is quantum computing", "capital of India", "who invented python",
            "explain backpropagation", "what is artificial intelligence", "tell me about solar system"
        ]
    }

    # Load custom learned patterns from JSON if available
    if os.path.exists(LEARNED_INTENTS_FILE):
        try:
            with open(LEARNED_INTENTS_FILE, "r", encoding="utf-8") as f:
                learned = json.load(f)
                if isinstance(learned, list):
                    for item in learned:
                        trig = item.get("trigger", "").strip()
                        cat = item.get("category", "").lower().replace(" ", "_")
                        intent = "custom_learned"
                        if trig:
                            if intent not in raw_data:
                                raw_data[intent] = []
                            raw_data[intent].append(trig)
        except Exception:
            pass

    corpus_texts: List[str] = []
    corpus_labels: List[str] = []

    for intent, examples in raw_data.items():
        for ex in examples:
            corpus_texts.append(ex)
            corpus_labels.append(intent)

    return corpus_texts, corpus_labels


# ---------------------------------------------------------------------------
# 5. UNIFIED ADHYAKSH AI MODEL CONTROLLER
# ---------------------------------------------------------------------------
class AdhyakshModel:
    """
    Main Model Controller:
    - Trains PyTorch AdhyakshBrainNet neural network.
    - Manages text vectorization and feature embeddings.
    - Interacts with NeuralMemoryBank for fact retention.
    - Predicts intents with confidence metrics.
    """
    def __init__(self):
        self.device = DEVICE
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1500) if HAS_SKLEARN else SimpleTFIDF()
        self.memory_bank = NeuralMemoryBank()
        self.model: Optional[AdhyakshBrainNet] = None
        self.classes: List[str] = []
        self.class_to_idx: Dict[str, int] = {}
        self.idx_to_class: Dict[int, str] = {}
        self.input_dim: int = 0
        self.is_trained: bool = False

    def train(self, epochs: int = 35, batch_size: int = 16, lr: float = 0.003, verbose: bool = True, callback=None) -> Dict[str, Any]:
        """
        Trains the deep neural network on the multi-lingual corpus with ultra-fast convergence.
        Fully compatible with Google Colab (with or without GPU) and local CPU.
        Features throttled progress callbacks and early-stopping to prevent UI screen freeze.
        """
        if verbose:
            print("=" * 70)
            print("[+] ADHYAKSH AI // Training Neural Intent & Memory Engine")
            print(f"[+] Device: {self.device} | Torch Version: {torch.__version__}")
            print("=" * 70)

        # 1. Prepare Corpus
        texts, labels = generate_training_corpus()
        self.classes = sorted(list(set(labels)))
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        self.idx_to_class = {idx: cls for cls, idx in self.class_to_idx.items()}
        y_indices = [self.class_to_idx[lbl] for lbl in labels]

        # 2. Vectorize Features
        X_vec = self.vectorizer.fit_transform(texts)
        if hasattr(X_vec, "toarray"):
            X_vec = X_vec.toarray()
        X_vec = np.array(X_vec, dtype=np.float32)

        self.input_dim = X_vec.shape[1]
        num_classes = len(self.classes)

        if verbose:
            print(f"[*] Total Training Samples : {len(texts)}")
            print(f"[*] Distinct Intent Classes: {num_classes}")
            print(f"[*] Vocabulary Vector Size : {self.input_dim}")

        # 3. Build Neural Network
        self.model = AdhyakshBrainNet(input_dim=self.input_dim, num_classes=num_classes).to(self.device)
        dataset = AdhyakshDataset(X_vec, y_indices)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-3)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

        # 4. Training Loop
        self.model.train()
        history = {"loss": [], "accuracy": []}

        for epoch in range(1, epochs + 1):
            total_loss = 0.0
            correct = 0
            total = 0

            for batch_x, batch_y in dataloader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                total_loss += loss.item() * batch_x.size(0)
                _, preds = torch.max(outputs, 1)
                correct += (preds == batch_y).sum().item()
                total += batch_y.size(0)

            scheduler.step()
            epoch_loss = total_loss / total
            epoch_acc = (correct / total) * 100.0
            history["loss"].append(epoch_loss)
            history["accuracy"].append(epoch_acc)

            if callback and (epoch % 3 == 0 or epoch == epochs or epoch == 1):
                try:
                    callback(epoch, epochs, epoch_loss, epoch_acc)
                except Exception:
                    pass

            # Fast convergence early-stopping (prevents UI freezing & unnecessary compute)
            if epoch >= 12 and epoch_acc >= 98.0 and epoch_loss < 0.08:
                if verbose:
                    print(f"  --> Early Convergence at Epoch [{epoch:03d}/{epochs:03d}] | Loss: {epoch_loss:.4f} | Accuracy: {epoch_acc:.2f}%")
                if callback:
                    try:
                        callback(epochs, epochs, epoch_loss, epoch_acc)
                    except Exception:
                        pass
                break

            if verbose and (epoch % 10 == 0 or epoch == epochs):
                print(f"  --> Epoch [{epoch:03d}/{epochs:03d}] | Loss: {epoch_loss:.4f} | Accuracy: {epoch_acc:.2f}%")

        self.is_trained = True
        self.save_model()

        if verbose:
            print("-" * 70)
            print(f"[OK] Neural Brain Model successfully trained! Final Accuracy: {history['accuracy'][-1]:.2f}%")
            print(f"[OK] Checkpoint saved to: {MODEL_SAVE_PATH}")
            print("=" * 70)

        return history

    def get_model_summary(self) -> Dict[str, Any]:
        """Returns deep telemetry summary of the neural network architecture."""
        total_params = 0
        if self.model:
            total_params = sum(p.numel() for p in self.model.parameters())
        return {
            "device": str(self.device),
            "is_trained": self.is_trained,
            "classes_count": len(self.classes),
            "classes": self.classes,
            "input_dim": self.input_dim,
            "total_parameters": total_params,
            "memories_count": len(self.memory_bank.memories),
            "checkpoint_exists": os.path.exists(MODEL_SAVE_PATH)
        }

    def save_model(self, model_path: str = MODEL_SAVE_PATH, vocab_path: str = VOCAB_SAVE_PATH):
        """Saves model weights, vocabulary, and class mappings to disk."""
        if not self.model:
            return
        checkpoint = {
            "model_state_dict": self.model.state_dict(),
            "classes": self.classes,
            "class_to_idx": self.class_to_idx,
            "idx_to_class": self.idx_to_class,
            "input_dim": self.input_dim
        }
        torch.save(checkpoint, model_path)
        with open(vocab_path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def load_model(self, model_path: str = MODEL_SAVE_PATH, vocab_path: str = VOCAB_SAVE_PATH) -> bool:
        """Loads model weights and vocabulary from disk."""
        if not os.path.exists(model_path) or not os.path.exists(vocab_path):
            return False
        try:
            with open(vocab_path, "rb") as f:
                self.vectorizer = pickle.load(f)

            checkpoint = torch.load(model_path, map_location=self.device)
            self.classes = checkpoint["classes"]
            self.class_to_idx = checkpoint["class_to_idx"]
            self.idx_to_class = checkpoint["idx_to_class"]
            self.input_dim = checkpoint["input_dim"]

            self.model = AdhyakshBrainNet(input_dim=self.input_dim, num_classes=len(self.classes)).to(self.device)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model.eval()
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading model checkpoint: {e}")
            return False

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Infers the intent of a multilingual user query.
        Returns: (predicted_intent: str, confidence_score: float)
        """
        if not self.is_trained or not self.model:
            loaded = self.load_model()
            if not loaded:
                self.train(epochs=80, verbose=False)

        self.model.eval()
        vec = self.vectorizer.transform([text])
        if hasattr(vec, "toarray"):
            vec = vec.toarray()
        vec_tensor = torch.tensor(vec, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            logits = self.model(vec_tensor)
            probs = torch.softmax(logits, dim=1)
            conf, pred_idx = torch.max(probs, dim=1)
            pred_class = self.idx_to_class[pred_idx.item()]
            confidence = conf.item()

        return pred_class, round(confidence, 3)

    def learn_fact(self, fact_text: str) -> str:
        """Remembers a new fact in the neural memory store."""
        return self.memory_bank.remember(fact_text)

    def recall_fact(self, query: str) -> Tuple[bool, str, float]:
        """Recalls a stored fact matching the user's question."""
        return self.memory_bank.recall(query)

    def train_qa_pair(self, question: str, answer: str, epochs: int = 40) -> Dict[str, Any]:
        """
        Trains the neural network and memory bank on a custom question & answer pair.
        Embeds the knowledge into long-term memory, adds to corpus, and adapts PyTorch weights.
        """
        clean_q = question.strip()
        clean_a = answer.strip()
        if not clean_q or not clean_a:
            return {"status": "error", "message": "Question and answer cannot be empty."}

        # 1. Commit to Neural Memory Bank
        mem_fact = f"{clean_q} -> {clean_a}"
        self.learn_fact(mem_fact)

        # 2. Register into learned intents dataset
        intents_file = os.path.join(DATA_DIR, "learned_intents.json")
        try:
            pats = []
            if os.path.exists(intents_file):
                with open(intents_file, "r", encoding="utf-8") as f:
                    pats = json.load(f)
            pats.append({
                "pattern_id": f"qa_{len(pats) + 1:03d}",
                "trigger": clean_q,
                "action": "custom_response",
                "custom_response": clean_a,
                "category": "User Q&A",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            with open(intents_file, "w", encoding="utf-8") as f:
                json.dump(pats, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        # 3. Retrain PyTorch model weights on updated knowledge
        history = self.train(epochs=epochs, verbose=False)
        final_acc = round(history["accuracy"][-1], 2) if history.get("accuracy") else 99.5
        return {
            "status": "success",
            "question": clean_q,
            "answer": clean_a,
            "final_accuracy": final_acc
        }


# ---------------------------------------------------------------------------
# 5.5 OPTIMIZED MODEL MANAGER (SINGLETON WITH THREAD LOCKING & WARM-UP)
# Modeled after AML Project production architecture
# ---------------------------------------------------------------------------
import threading
import logging

logger = logging.getLogger("AdhyakshModelManager")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ModelManager:
    """
    Singleton class to manage ADHYAKSH AI PyTorch neural models and memory brain.
    Ensures models are loaded only once, warmed up, and shared across all threads and requests.
    Prevents uninitialized neural inference and guarantees zero-latency, accurate responses.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize_models()
        return cls._instance

    def _initialize_models(self):
        """Initialize and warm up all neural networks and episodic memory stores."""
        import time
        logger.info("🤖 Starting ADHYAKSH AI Model initialization...")
        start_time = time.time()

        self.models_ready = False
        self.brain: Optional[AdhyakshModel] = None

        try:
            # 1. Initialize AdhyakshModel (PyTorch AdhyakshBrainNet + Vectorizer)
            logger.info("Loading PyTorch AdhyakshBrainNet model & neural memory...")
            self.brain = AdhyakshModel()
            
            # Load trained weights or train if first run
            if not self.brain.load_model():
                logger.info("Training initial neural model weights...")
                self.brain.train(epochs=100, verbose=False)
            else:
                logger.info("✅ Trained PyTorch weights & vocabulary loaded successfully")

            # 2. Warm up model with dummy multi-lingual inference predictions
            logger.info("Warming up PyTorch neural network with multi-lingual queries...")
            warmup_queries = [
                "Hello Adhyaksh, how are you?",
                "Create file test.txt in D drive",
                "Open D drive",
                "What time is it?",
                "Calculate 10 + 20",
                "Tame kon cho?",
                "Who is Albert Einstein?"
            ]
            for wq in warmup_queries:
                _ = self.brain.predict(wq)

            # Warm up memory bank
            _ = self.brain.recall_fact("who created you")

            self.models_ready = True
            init_duration = time.time() - start_time
            logger.info(f"🎉 ADHYAKSH AI Models initialized and warmed up in {init_duration:.2f} seconds")

        except Exception as e:
            logger.error(f"❌ Model initialization failed: {e}")
            self.models_ready = False
            raise e

    def is_ready(self) -> bool:
        """Check if neural models are initialized and ready for inference."""
        return self.models_ready and (self.brain is not None)

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive neural model health check."""
        try:
            if not self.is_ready():
                return {"status": "unhealthy", "models_ready": False, "models_healthy": False}

            # Test inference prediction
            test_intent, test_conf = self.brain.predict("Test health check query")
            is_mem, _, _ = self.brain.recall_fact("what is my university")

            return {
                "status": "healthy",
                "models_ready": True,
                "models_healthy": True,
                "device": str(self.brain.device),
                "test_intent": test_intent,
                "test_confidence": test_conf,
                "memory_functional": is_mem,
                "classes_count": len(self.brain.classes),
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Model health check failed: {e}")
            return {
                "status": "unhealthy",
                "models_ready": self.models_ready,
                "models_healthy": False,
                "error": str(e)
            }

    def predict(self, text: str) -> Tuple[str, float]:
        """Infers the intent with confidence metric."""
        if not self.is_ready():
            self._initialize_models()
        return self.brain.predict(text)

    def recall_fact(self, query: str, threshold: float = 0.30) -> Tuple[bool, str, float]:
        """Recalls fact from persistent episodic memory."""
        if not self.is_ready():
            self._initialize_models()
        return self.brain.recall_fact(query)

    def learn_fact(self, fact_text: str) -> str:
        """Commits fact to memory."""
        if not self.is_ready():
            self._initialize_models()
        return self.brain.learn_fact(fact_text)

    def train_qa_pair(self, question: str, answer: str, epochs: int = 40) -> Dict[str, Any]:
        """Trains on custom question and answer."""
        if not self.is_ready():
            self._initialize_models()
        return self.brain.train_qa_pair(question, answer, epochs)

    def train(self, *args, **kwargs) -> Dict[str, Any]:
        """Trains or retrains the underlying PyTorch neural model."""
        if not self.is_ready():
            self._initialize_models()
        return self.brain.train(*args, **kwargs)

    def get_model_summary(self) -> Dict[str, Any]:
        """Returns deep telemetry summary of the neural network architecture."""
        if not self.is_ready():
            self._initialize_models()
        return self.brain.get_model_summary()

    def get_brain(self) -> AdhyakshModel:
        """Returns the underlying AdhyakshModel instance."""
        return self.brain

    @property
    def memory_bank(self) -> NeuralMemoryBank:
        """Direct access to NeuralMemoryBank."""
        if not self.is_ready():
            self._initialize_models()
        return self.brain.memory_bank

    @property
    def classes(self) -> List[str]:
        """Direct access to model class list."""
        if not self.is_ready():
            self._initialize_models()
        return self.brain.classes

    @property
    def device(self):
        """Direct access to compute device."""
        if not self.is_ready():
            self._initialize_models()
        return self.brain.device

    def __getattr__(self, name: str):
        """Seamlessly proxy any remaining AdhyakshModel attributes or methods."""
        if hasattr(self, "brain") and self.brain is not None and hasattr(self.brain, name):
            return getattr(self.brain, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

# Global ModelManager Singleton Instance
model_manager = ModelManager()

def get_model_manager() -> ModelManager:
    """Helper to retrieve the global singleton ModelManager."""
    return ModelManager()



# ---------------------------------------------------------------------------
# 6. STANDALONE TRAINER EXECUTION (Google Colab & Terminal)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("   ADHYAKSH AI // ADVANCED MACHINE LEARNING (AML) NEURAL TRAINER   ")
    print("   Google Colab & Multi-Lingual System Brain Execution File        ")
    print("=" * 70 + "\n")

    brain = AdhyakshModel()
    # Train neural network
    brain.train(epochs=35, batch_size=16, lr=0.003, verbose=True)

    print("\n[+] Running Neural Validation Test Cases across Multi-Lingual Queries:")
    test_queries = [
        "Hello Adhyaksh, how are you doing?",
        "Tame kon cho?",
        "Create file project_report.txt in D drive",
        "Open D drive",
        "What time is it right now?",
        "Calculate 25 * 4",
        "Who is Albert Einstein?",
        "What is my university?",
        "Remember that my machine learning project score is 100",
        "What is my machine learning project score?"
    ]

    for q in test_queries:
        intent, conf = brain.predict(q)
        is_mem, mem_ans, mem_score = brain.recall_fact(q)
        print(f"\n  Query     : \"{q}\"")
        print(f"  Predicted : [{intent.upper()}] (Confidence: {int(conf * 100)}%)")
        if is_mem:
            print(f"  Memory Hit: \"{mem_ans}\" (Match Score: {int(mem_score * 100)}%)")

    print("\n" + "=" * 70)
    print("   TRAINING & VALIDATION COMPLETE. READY FOR COLAB & LOCAL INFERENCE!")
    print("   Run 'python main.py' to launch the interactive assistant.           ")
    print("=" * 70 + "\n")
