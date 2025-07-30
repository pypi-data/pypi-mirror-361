__version__ = '0.0.2'
__letter__ = 'i'

def get_version() -> str:
    return f"{__letter__}'{__version__}'"

__all__ = [
    'get_version',
]