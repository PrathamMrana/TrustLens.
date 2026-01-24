from enum import Enum, auto

class Language(Enum):
    PYTHON = auto()
    JAVASCRIPT = auto()
    TYPESCRIPT = auto()
    JAVA = auto()
    UNKNOWN = auto()

def detect_language(filename: str) -> Language:
    """
    Detect programming language deterministically from file extension.
    
    Args:
        filename: Name of the file with extension
        
    Returns:
        Language enum value
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.py'):
        return Language.PYTHON
    elif filename_lower.endswith('.js'):
        return Language.JAVASCRIPT
    elif filename_lower.endswith('.ts'):
        return Language.TYPESCRIPT
    elif filename_lower.endswith('.java'):
        return Language.JAVA
    else:
        return Language.UNKNOWN
