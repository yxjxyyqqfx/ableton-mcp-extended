## _FILEPATH_BROWSER_MAPPING

**Status**: rework
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:81-86`
**LOC delta**: ~6
**Live compat**: Live 11 + 12 (константа не зависит от Live version API)

### Rationale (Russian)
Константа дает явный мост между файловой системой и browser roots, что полезно для предсказуемого routing sample-путей. Но значения жестко привязаны к конкретным mount/host путям форка и не масштабируются на другие окружения. Ее нужно вынести в конфигурацию и документировать как deployment-specific mapping.

### API Contract
```python
_FILEPATH_BROWSER_MAPPING = [
    ("/ocp/mnt/_lib_", "User_folders/_lib_"),
    ("/Users/user/Documents/_lib_", "User_folders/_lib_"),
    ("/ocp/mnt/Splice", "User_folders/Splice"),
    ("/Users/user/Splice", "User_folders/Splice"),
]
```

### Examples
1. Mapping-правило `("/ocp/mnt/Splice", "User_folders/Splice")` конвертирует абсолютный путь к Browser path с сохранением relative suffix.
2. Добавление нового правила для другой shared-папки позволяет переиспользовать `_resolve_filepath_to_browser_path` без изменения алгоритма.

### Tests
- `tests/unit/test_browser.py::test_filepath_browser_mapping_entries` (planned)
- `tests/integration/test_browser_live.py::test_filepath_mapping_end_to_end` (planned)

### English Description
Defines the path-prefix translation table used by filepath-to-browser-path resolution. The concept is useful, but the currently hardcoded prefixes are fork-specific and should be externalized.

### Rework plan
- Переместить mapping в конфиг загрузки (JSON/env/инициализация), чтобы deployment задавал свои правила без patching кода.
- Suggested API after rework: module-level `get_filepath_browser_mapping()` с lazy-load и fallback на defaults.
- Migration note: оставить текущие четыре правила как начальный default profile для совместимости.
