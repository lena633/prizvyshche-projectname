
"""Ієрархія винятків застосунку: один корінь, кілька конкретних нащадків."""

class JobRadarError(Exception):
    """Базовий виняток застосунку."""

class SourceError(JobRadarError):
    """Проблема з джерелом даних: файл, мережа, формат."""

class ParseError(SourceError):
    """Запис не вдалося розібрати."""

class ConfigError(JobRadarError):
    """Некоректна конфігурація застосунку."""

