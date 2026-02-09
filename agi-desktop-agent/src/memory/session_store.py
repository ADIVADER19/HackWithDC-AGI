"""
Session Store — Persistent storage for all agent interactions.

Each session = one chat thread.  Every query + full response is logged
so the conversation can be resumed, replayed, or exported.

Storage: data/sessions/<session_id>.json
"""

import json
import os
import uuid
from datetime import datetime


class SessionStore:
    """
    Manages persistent chat sessions.

    Usage:
        store = SessionStore()
        sid = store.create_session("Meeting prep for TechCorp")
        store.append(sid, user_query, route_info, results_dict)
        history = store.get_session(sid)
    """

    def __init__(self, sessions_dir: str | None = None):
        if sessions_dir is None:
            _project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            sessions_dir = os.path.join(_project_root, "data", "sessions")
        self.sessions_dir = sessions_dir
        os.makedirs(self.sessions_dir, exist_ok=True)

    # ── Session lifecycle ──────────────────────────────────────

    def create_session(self, title: str = "") -> str:
        """Create a new session and return its ID."""
        session_id = uuid.uuid4().hex[:12]
        session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "title": title or f"Session {session_id[:6]}",
            "interactions": []
        }
        self._save(session_id, session)
        return session_id

    def append(self, session_id: str, user_query: str,
               route: dict, results: dict, execution_time: float = 0) -> int:
        """
        Append a full interaction (query + response) to a session.

        Args:
            session_id: The session to append to
            user_query: The raw user prompt
            route: Router classification dict
            results: Dict of scenario→result (the full envelope.results)
            execution_time: Total round-trip time

        Returns:
            The 1-based interaction number
        """
        session = self._load(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        interaction_num = len(session["interactions"]) + 1
        interaction = {
            "id": interaction_num,
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "route": _sanitize(route),
            "results": _sanitize(results),
            "execution_time": execution_time,
        }

        session["interactions"].append(interaction)
        session["updated_at"] = datetime.now().isoformat()

        # Auto-title from first query if still default
        if interaction_num == 1 and session["title"].startswith("Session "):
            session["title"] = user_query[:80]

        self._save(session_id, session)
        return interaction_num

    # ── Retrieval ──────────────────────────────────────────────

    def get_session(self, session_id: str) -> dict | None:
        """Return full session dict or None."""
        return self._load(session_id)

    def get_interaction(self, session_id: str, interaction_id: int) -> dict | None:
        """Return a single interaction by its 1-based ID."""
        session = self._load(session_id)
        if session is None:
            return None
        for ix in session["interactions"]:
            if ix["id"] == interaction_id:
                return ix
        return None

    def list_sessions(self, limit: int = 50) -> list[dict]:
        """
        Return a list of session summaries (id, title, created_at,
        interaction count), newest first.
        """
        summaries = []
        for fname in os.listdir(self.sessions_dir):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(self.sessions_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                summaries.append({
                    "session_id": data.get("session_id", fname.replace(".json", "")),
                    "title": data.get("title", "Untitled"),
                    "created_at": data.get("created_at", ""),
                    "updated_at": data.get("updated_at", ""),
                    "interaction_count": len(data.get("interactions", [])),
                })
            except Exception:
                continue

        summaries.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        return summaries[:limit]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session file. Returns True if deleted."""
        path = self._path(session_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    # ── Internal ───────────────────────────────────────────────

    def _path(self, session_id: str) -> str:
        return os.path.join(self.sessions_dir, f"{session_id}.json")

    def _load(self, session_id: str) -> dict | None:
        path = self._path(session_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, session_id: str, data: dict):
        path = self._path(session_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def _sanitize(obj):
    """
    Ensure an object is JSON-serializable.
    Converts any non-serializable values to strings.
    """
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_sanitize(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj)
