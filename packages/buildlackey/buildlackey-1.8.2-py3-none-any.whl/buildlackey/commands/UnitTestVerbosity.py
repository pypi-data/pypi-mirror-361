
from enum import Enum

from click import BadParameter

VERBOSITY_QUIET:   int = 0  # Print the total numbers of tests executed and the global result
VERBOSITY_DEFAULT: int = 1  # QUIET plus a dot for every successful test or an 'F' for every failure
VERBOSITY_VERBOSE: int = 2  # Print help string of every test and the result
VERBOSITY_LOUD:    int = 3  # ??


class UnitTestVerbosity(Enum):

    QUIET     = 'quiet'    # 0 Print the total numbers of tests executed and the global result
    DEFAULT   = 'default'  # 1 QUIET plus a dot for every successful test or an 'F' for every failure
    VERBOSE   = 'verbose'  # 2 Print help string of every test and the result
    LOUD      = 'loud'     # 3 ??

    @classmethod
    def toEnum(cls, strValue: str) -> 'UnitTestVerbosity':
        """
        Converts the input string to the correct verbosity level
        Args:
            strValue:   A string value

        Returns:  The unit test verbosity enumeration
        """
        canonicalStr: str = strValue.strip(' ').lower()

        match canonicalStr:
            case UnitTestVerbosity.QUIET.value:
                enumValue: UnitTestVerbosity = UnitTestVerbosity.QUIET
            case UnitTestVerbosity.DEFAULT.value:
                enumValue = UnitTestVerbosity.DEFAULT
            case UnitTestVerbosity.VERBOSE.value:
                enumValue = UnitTestVerbosity.VERBOSE
            case UnitTestVerbosity.LOUD.value:
                enumValue = UnitTestVerbosity.LOUD
            case _:
                raise BadParameter(f"I do not understand that verbosity level '{strValue}'")

        return enumValue

    @classmethod
    def toUnitTestValue(cls, verbosity: 'UnitTestVerbosity') -> int:

        match verbosity:
            case UnitTestVerbosity.QUIET:
                retValue: int = VERBOSITY_QUIET
            case UnitTestVerbosity.DEFAULT:
                retValue = VERBOSITY_DEFAULT
            case UnitTestVerbosity.VERBOSE:
                retValue = VERBOSITY_VERBOSE
            case UnitTestVerbosity.LOUD:
                retValue = VERBOSITY_LOUD
            case _:
                raise ValueError('WTF this cannot be allowed to happen, I will not be denied')

        return retValue
