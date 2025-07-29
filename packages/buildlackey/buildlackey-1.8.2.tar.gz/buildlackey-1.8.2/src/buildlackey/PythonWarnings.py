
from enum import Enum


class PythonWarnings(Enum):
    DEFAULT = 'default'    # Warn once per call location
    ERROR   = 'error'      # Convert to exceptions
    ALWAYS  = 'always'     # Warn every time
    MODULE  = 'module'     # Warn once per calling module
    ONCE    = 'once'       # Warn once per Python process
    IGNORE  = 'ignore'     # Never warn
