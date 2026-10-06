import time
import uuid
import threading
from typing import Dict, List, Any, Optional
from backend.copilot.models import CopilotTurn, ResearchContextSummary

class CopilotSession:
    def __init__(self, session_id: str, source_mode: str = "hybrid"):
        self.session_id: str = session_id
        self.created_at: float = time.time()
        self.last_active: float = time.time()
        self.source_mode: str = source_mode
        self.current_query: Optional[str] = None
        self.technical_concepts: List[str] = []
        self.retrieved_patents: List[Dict[str, Any]] = []
        self.selected_patent: Optional[Dict[str, Any]] = None
        self.turns: List[CopilotTurn] = []
        self.cached_novelty: Optional[Dict[str, Any]] = None
        self.cached_whitespace: Optional[Dict[str, Any]] = None
        self.provenance: Optional[Dict[str, Any]] = None
        self.last_intent: str = "IDLE"

    def touch(self):
        self.last_active = time.time()

    def add_turn(self, role: str, content: str, intent: Optional[str] = None):
        self.touch()
        self.turns.append(
            CopilotTurn(
                role=role,
                content=content,
                intent=intent,
                timestamp=time.time()
            )
        )
        if intent:
            self.last_intent = intent

    def set_retrieved_patents(
        self,
        patents: List[Dict[str, Any]],
        query: str,
        concepts: List[str],
        provenance: Optional[Dict[str, Any]] = None
    ):
        self.touch()
        self.retrieved_patents = patents
        self.current_query = query
        self.technical_concepts = concepts
        self.provenance = provenance
        if patents:
            # By default, select the top ranked patent as the primary focus
            self.selected_patent = patents[0]
        else:
            self.selected_patent = None
        # Invalidate cached novelty/whitespace since new patents were retrieved
        self.cached_novelty = None
        self.cached_whitespace = None

    def get_summary(self) -> ResearchContextSummary:
        selected_id = None
        if self.selected_patent:
            selected_id = (
                self.selected_patent.get("publication_number") or
                self.selected_patent.get("application_number") or
                self.selected_patent.get("title")
            )
        return ResearchContextSummary(
            current_query=self.current_query,
            intent=self.last_intent,
            patents_count=len(self.retrieved_patents),
            source_mode=self.source_mode,
            selected_patent_id=selected_id,
            technical_concepts=self.technical_concepts
        )

class SessionManager:
    """
    Thread-safe in-memory session manager with automatic TTL eviction.
    """
    def __init__(self, ttl_seconds: int = 86400):  # 24 hours
        self._sessions: Dict[str, CopilotSession] = {}
        self._lock = threading.Lock()
        self._ttl = ttl_seconds

    def get_or_create(self, session_id: Optional[str] = None, source_mode: str = "hybrid") -> CopilotSession:
        with self._lock:
            self._cleanup_expired()
            if session_id and session_id in self._sessions:
                sess = self._sessions[session_id]
                sess.touch()
                if source_mode:
                    sess.source_mode = source_mode
                return sess
            
            # Generate new session ID if missing or unrecognized
            new_id = session_id.strip() if (session_id and session_id.strip()) else str(uuid.uuid4())
            sess = CopilotSession(session_id=new_id, source_mode=source_mode)
            self._sessions[new_id] = sess
            return sess

    def get(self, session_id: str) -> Optional[CopilotSession]:
        with self._lock:
            sess = self._sessions.get(session_id)
            if sess:
                sess.touch()
            return sess

    def delete(self, session_id: str) -> bool:
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def _cleanup_expired(self):
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if now - s.last_active > self._ttl]
        for sid in expired:
            del self._sessions[sid]

# Singleton session manager
session_manager = SessionManager()
