"""
Configuration file for Resume-JD Match Scorer application.
Contains all constants and configurable parameters.
"""

# File Processing Configuration
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB in bytes
TEXT_PREVIEW_CHAR_LIMIT: int = 1000
MIN_WORD_COUNT: int = 50  # Minimum words for meaningful analysis
MIN_CHAR_COUNT: int = 100  # Minimum characters for scanned PDF detection

# NLP Model Configuration
MODEL_NAME: str = 'all-MiniLM-L6-v2'
EMBEDDING_DIMENSION: int = 384

# Score Thresholds
STRONG_MATCH_THRESHOLD: float = 70.0  # >= 70% is considered strong match
MODERATE_MATCH_THRESHOLD: float = 50.0  # >= 50% is considered moderate match

# Text Encoding Fallbacks (in order of preference)
TEXT_ENCODINGS: list[str] = ['utf-8', 'latin-1', 'cp1252']

# Logging Configuration
LOG_LEVEL: str = 'INFO'

# UI Configuration
PAGE_TITLE: str = "Resume ↔ JD Match Scorer"
PAGE_ICON: str = "🤖"
APP_TITLE: str = "🤖 Resume ↔ JD Match Scorer"
APP_INSTRUCTION: str = (
    "Instruction: Upload a **resume** (PDF) and a "
    "**job description** (TXT) to get a semantic match score."
)

# File Type Configuration
ALLOWED_RESUME_TYPES: list[str] = ["pdf"]
ALLOWED_JD_TYPES: list[str] = ["txt"]

# Regex Patterns
TEXT_CLEAN_PATTERN: str = r'[^a-z0-9\s]'
WHITESPACE_PATTERN: str = r'\s+'
