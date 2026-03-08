"""
Database Layer for the Muqattaat Cryptanalytic Lab.
Provides dual SQLite/PostgreSQL support with connection pooling and proper error handling.
"""
import os
import logging
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional, Any
from dataclasses import dataclass, field

from dotenv import load_dotenv
from src.core.state import Hypothesis

load_dotenv()

logger = logging.getLogger(__name__)

# Use SQLite fallback if no DATABASE_URL
USE_SQLITE = not os.getenv("DATABASE_URL")

# Connection pool configuration
CONNECTION_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
CONNECTION_TIMEOUT = int(os.getenv("DB_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("DB_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("DB_RETRY_DELAY", "1.0"))

# Only import psycopg2 if using PostgreSQL
if not USE_SQLITE:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor, Json
else:
    pool = None
    Json = None
    RealDictCursor = None


# ============================================================================
# Connection Pool Management
# ============================================================================

class DatabaseConnectionPool:
    """Manages a pool of database connections for efficient reuse."""
    
    _instance: Optional['DatabaseConnectionPool'] = None
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self) -> None:
        """Initialize the connection pool based on database type."""
        if USE_SQLITE:
            # SQLite doesn't need pooling, use single connection
            self._connection_pool = None
            logger.info("Using SQLite fallback (no pooling needed)")
        else:
            try:
                url = os.getenv("DATABASE_URL")
                # Neon often requires sslmode=require for remote connections
                self._connection_pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=CONNECTION_POOL_SIZE,
                    dsn=url,
                    connect_timeout=CONNECTION_TIMEOUT
                )
                logger.info(f"PostgreSQL connection pool initialized with {CONNECTION_POOL_SIZE} connections")
            except Exception as e:
                logger.error(f"Failed to initialize connection pool: {e}")
                self._connection_pool = None
    
    def get_connection(self):
        """Get a connection from the pool."""
        if USE_SQLITE:
            conn = sqlite3.connect('/workspaces/QL/data/processed/meritocracy.db')
            conn.row_factory = sqlite3.Row
            return conn
        
        if self._connection_pool:
            try:
                return self._connection_pool.getconn()
            except Exception as e:
                logger.error(f"Failed to get connection from pool: {e}")
                raise
    
    def return_connection(self, conn) -> None:
        """Return a connection to the pool."""
        if USE_SQLITE or not self._connection_pool:
            try:
                conn.close()
            except Exception:
                pass
            return
        
        try:
            self._connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Failed to return connection to pool: {e}")
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        if self._connection_pool:
            try:
                self._connection_pool.closeall()
                logger.info("Connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")


# Global pool instance
_pool: Optional[DatabaseConnectionPool] = None


def get_pool() -> DatabaseConnectionPool:
    """Get or create the database connection pool."""
    global _pool
    if _pool is None:
        _pool = DatabaseConnectionPool()
    return _pool


@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager for database connections.
    Automatically handles connection acquisition and release.
    
    Usage:
        with get_db_connection() as conn:
            cur = conn.cursor()
            # do work
    """
    conn = None
    try:
        conn = get_pool().get_connection()
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            get_pool().return_connection(conn)


def get_db_connection_raw():
    """Legacy function for backward compatibility."""
    if USE_SQLITE:
        conn = sqlite3.connect('/workspaces/QL/data/processed/meritocracy.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    url = os.getenv("DATABASE_URL")
    return psycopg2.connect(url, cursor_factory=RealDictCursor)


# ============================================================================
# Retry Logic
# ============================================================================

def with_retry(func):
    """
    Decorator that adds retry logic to database operations.
    
    Args:
        func: The function to wrap with retry logic
    
    Returns:
        Wrapped function with retry handling
    """
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}. "
                        f"Retrying in {RETRY_DELAY}s..."
                    )
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Database operation failed after {MAX_RETRIES} attempts: {e}")
        raise last_exception
    
    return wrapper


# ============================================================================
# Hypothesis Recording
# ============================================================================

@with_retry
def record_hypothesis(run_id: str, hyp: Hypothesis, status: str = "RAW", reason: str = None):
    """
    Saves agent findings to the cloud finding log for persistent memory.
    
    Args:
        run_id: Unique identifier for the research run
        hyp: Hypothesis object containing the finding
        status: Status of the hypothesis (RAW, VALIDATED, REJECTED, etc.)
        reason: Optional reason for rejection
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            if Json:
                # PostgreSQL path
                cur.execute("""
                    INSERT INTO c2_finding_log (ticket_id, discovery_title, json_payload, score_boost)
                    VALUES (%s, %s, %s, %s)
                """, (
                    run_id, 
                    f"{hyp.source_scout} Discovery - Surah {hyp.surah_refs}",
                    Json({
                        "scout": hyp.source_scout,
                        "goal": hyp.goal_link,
                        "description": hyp.description,
                        "evidence": hyp.evidence_snippets,
                        "status": status,
                        "rejection_reason": reason,
                        "transformation_steps": hyp.transformation_steps,
                        "metadata": getattr(hyp, 'metadata', {})
                    }),
                    hyp.score
                ))
            else:
                # SQLite fallback - store as text
                import json as json_module
                cur.execute("""
                    INSERT INTO c2_finding_log (ticket_id, discovery_title, json_payload, score_boost)
                    VALUES (?, ?, ?, ?)
                """, (
                    run_id, 
                    f"{hyp.source_scout} Discovery - Surah {hyp.surah_refs}",
                    json_module.dumps({
                        "scout": hyp.source_scout,
                        "goal": hyp.goal_link,
                        "description": hyp.description,
                        "evidence": hyp.evidence_snippets,
                        "status": status,
                        "rejection_reason": reason,
                        "transformation_steps": hyp.transformation_steps,
                        "metadata": getattr(hyp, 'metadata', {})
                    }),
                    hyp.score
                ))
            conn.commit()
            logger.info(f"Recorded hypothesis from {hyp.source_scout} for run {run_id}")
    except Exception as e:
        logger.error(f"Failed to record hypothesis: {e}")
        # Graceful failure - don't crash the pipeline


# ============================================================================
# Neon Lab API
# ============================================================================

class NeonLabAPI:
    """
    Central API endpoints for all agents. 
    Allows 24/7 data access and event recording without local file overhead.
    """
    
    def __init__(self):
        self._conn = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to the database."""
        try:
            self._conn = get_pool().get_connection()
            self._conn.autocommit = True
            logger.info("NeonLabAPI connected to database")
        except Exception as e:
            logger.warning(f"Could not connect to database: {e}")
            self._conn = None
    
    @property
    def is_connected(self) -> bool:
        """Check if the API is connected to the database."""
        return self._conn is not None
    
    def open_ticket(self, run_id: str, role: str, pattern: str):
        """
        Domain 2: Event API - Agents 'clock in' to start research.
        
        Args:
            run_id: Unique identifier for the research ticket
            role: The agent role (e.g., 'linguistic_scout', 'math_scout')
            pattern: The target pattern being investigated
        """
        if not self._conn:
            logger.warning("No database connection, skipping ticket creation")
            return
        
        try:
            with self._conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO c2_research_ticket (ticket_id, agent_role, target_pattern, status)
                    VALUES (%s, %s, %s, 'Executing')
                    ON CONFLICT (ticket_id) DO UPDATE SET status = 'Executing'
                """, (run_id, role, pattern))
            logger.debug(f"Opened ticket {run_id} for {role}")
        except Exception as e:
            logger.error(f"Failed to open ticket: {e}")
    
    def get_surah_context(self, surah_id: int) -> Optional[dict]:
        """
        Domain 1: Corpus Data - Fetches metadata and clean text for an agent.
        
        Args:
            surah_id: The Surah number to fetch
            
        Returns:
            Dictionary containing surah metadata and verses, or None on failure
        """
        if not self._conn:
            logger.warning("No database connection, skipping surah fetch")
            return None
        
        try:
            with self._conn.cursor() as cur:
                cur.execute("""
                    SELECT m.*, STRING_AGG(v.text_clean, ' ' ORDER BY v.verse_number) as content
                    FROM surah_master m
                    JOIN verse_data v ON m.surah_id = v.surah_id
                    WHERE m.surah_id = %s
                    GROUP BY m.surah_id
                """, (surah_id,))
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch surah context: {e}")
            return None
    
    def update_flow_matrix(self, from_l: str, to_l: str, weight: float):
        """
        Updates the Rigid Flow Matrix based on frequency discoveries.
        
        Args:
            from_l: Source letter
            to_l: Target letter
            weight: Probability weight for the transition
        """
        if not self._conn:
            logger.warning("No database connection, skipping flow matrix update")
            return
        
        try:
            with self._conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO rigid_flow_matrix (from_letter, to_letter, probability_weight)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO UPDATE SET probability_weight = EXCLUDED.probability_weight
                """, (from_l, to_l, weight))
            logger.debug(f"Updated flow matrix: {from_l} -> {to_l} = {weight}")
        except Exception as e:
            logger.error(f"Failed to update flow matrix: {e}")
    
    def create_ticket(self, ticket_id: str, role: str, pattern: str):
        """
        Creates a new ticket in the database.
        
        Args:
            ticket_id: Unique ticket identifier
            role: Agent role
            pattern: Target pattern
        """
        if not self._conn:
            logger.warning("No database connection, skipping ticket creation")
            return
        
        try:
            with self._conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO c2_research_ticket (ticket_id, agent_role, target_pattern, status)
                    VALUES (%s, %s, %s, 'Executing')
                """, (ticket_id, role, pattern))
            self._conn.commit()
            logger.info(f"Created ticket {ticket_id} for {role}")
        except Exception as e:
            logger.error(f"Failed to create ticket: {e}")
    
    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            get_pool().return_connection(self._conn)
            self._conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================================
# Database Schema Initialization
# ============================================================================

def init_db_schema():
    """Initializes the multi-domain schema in Neon or SQLite."""
    conn = get_db_connection_raw()
    cur = conn.cursor()
    
    if USE_SQLITE:
        # SQLite: execute statements one at a time
        cur.execute("""
            CREATE TABLE IF NOT EXISTS surah_master (
                surah_id INTEGER PRIMARY KEY, surah_name VARCHAR(100), total_verses INTEGER,
                has_muqattaat INTEGER, vector_magnitude REAL, checksum_cluster_id INTEGER
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS muqattaat_prefix (
                prefix_id INTEGER PRIMARY KEY AUTOINCREMENT, surah_id INTEGER,
                letters_sequence VARCHAR(20), abjad_weight INTEGER, anchor_verse_index INTEGER, saturation_percentage REAL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS verse_data (
                verse_id INTEGER PRIMARY KEY AUTOINCREMENT, surah_id INTEGER,
                verse_number INTEGER, text_uthmani TEXT, text_clean TEXT, is_anchor_flare INTEGER, prefix_density_ratio REAL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rigid_flow_matrix (
                transition_id INTEGER PRIMARY KEY AUTOINCREMENT, from_letter CHAR(1), to_letter CHAR(1),
                probability_weight REAL, is_forbidden INTEGER
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS c2_research_ticket (
                ticket_id VARCHAR(50) PRIMARY KEY, agent_role VARCHAR(50),
                target_pattern TEXT, status VARCHAR(20), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS c2_finding_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id VARCHAR(50), discovery_title VARCHAR(200),
                json_payload TEXT, score_boost REAL
            )
        """)
    else:
        # PostgreSQL: multi-statement execution
        cur.execute("""
            CREATE TABLE IF NOT EXISTS surah_master (
                surah_id INT PRIMARY KEY, surah_name VARCHAR(100), total_verses INT,
                has_muqattaat BOOLEAN, vector_magnitude FLOAT, checksum_cluster_id INT
            );
            CREATE TABLE IF NOT EXISTS muqattaat_prefix (
                prefix_id SERIAL PRIMARY KEY, surah_id INT REFERENCES surah_master(surah_id),
                letters_sequence VARCHAR(20), abjad_weight INT, anchor_verse_index INT, saturation_percentage FLOAT
            );
            CREATE TABLE IF NOT EXISTS verse_data (
                verse_id SERIAL PRIMARY KEY, surah_id INT REFERENCES surah_master(surah_id),
                verse_number INT, text_uthmani TEXT, text_clean TEXT, is_anchor_flare BOOLEAN, prefix_density_ratio FLOAT
            );
            CREATE TABLE IF NOT EXISTS rigid_flow_matrix (
                transition_id SERIAL PRIMARY KEY, from_letter CHAR(1), to_letter CHAR(1),
                probability_weight FLOAT, is_forbidden BOOLEAN
            );
            CREATE TABLE IF NOT EXISTS c2_research_ticket (
                ticket_id VARCHAR(50) PRIMARY KEY, agent_role VARCHAR(50),
                target_pattern TEXT, status VARCHAR(20), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS c2_finding_log (
                log_id SERIAL PRIMARY KEY, ticket_id VARCHAR(50), discovery_title VARCHAR(200),
                json_payload JSONB, score_boost FLOAT
            );
        """)
    
    conn.commit()
    cur.close()
    conn.close()
    logger.info("✅ Lab Schema Initialized.")


# ============================================================================
# Cleanup
# ============================================================================

def cleanup_connections() -> None:
    """Clean up all database connections on shutdown."""
    global _pool
    if _pool:
        _pool.close_all()
        _pool = None
        logger.info("Database connections cleaned up")

