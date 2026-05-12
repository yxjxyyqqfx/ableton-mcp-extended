## resolve_filepath_to_browser_path

**Status**: rework
**Source**: `/legacy/MCP_Server/server.py:835-845`; `/legacy/AbletonMCP_Remote_Script/__init__.py:2906-2927`; `/legacy/AbletonMCP_Remote_Script/__init__.py:81-86`
**LOC delta**: ~39
**Live compat**: Live 11 + 12 (функция pure-mapping, не зависит от version-specific API)

### Rationale (Russian)
Функция важна для bridge между файловыми путями и путями браузера Live, но текущая версия завязана на фиксированные `/ocp/mnt/...` и host-пути. Это затрудняет использование в других окружениях и CI-топологиях. Нужна конфигурируемая стратегия резолва вместо встроенного списка префиксов.

### API Contract
```python
def resolve_filepath_to_browser_path(ctx: Context, filepath: str) -> str:

def _resolve_filepath_to_browser_path(self, filepath):

_FILEPATH_BROWSER_MAPPING = [
    ("/ocp/mnt/_lib_", "User_folders/_lib_"),
    ("/Users/user/Documents/_lib_", "User_folders/_lib_"),
    ("/ocp/mnt/Splice", "User_folders/Splice"),
    ("/Users/user/Splice", "User_folders/Splice"),
]
```

### Examples
1. `resolve_filepath_to_browser_path("/ocp/mnt/Splice/Samples/Kick.wav")` → `User_folders/Splice/Samples/Kick.wav`.
2. Неподдерживаемый префикс (например `/tmp/audio.wav`) возвращает `unsupported_prefix` ошибку.

### Tests
- `tests/unit/test_browser.py::test_resolve_filepath_to_browser_path_known_prefixes` (planned)
- `tests/integration/test_browser_live.py::test_resolve_filepath_to_browser_path_live_contract` (planned)

### English Description
Converts host/container filepaths into Ableton browser paths for downstream sample loading flows. The current implementation works but is environment-specific due to hardcoded mount prefixes.

### Rework plan
- Перенести mapping-префиксы в конфиг/ENV/инициализацию script (а не class literal), добавить возможность дополнять правила без изменения кода.
- Suggested API after rework: `resolve_filepath_to_browser_path(filepath: str, mapping: Sequence[tuple[str, str]] | None = None)` с валидацией и нормализацией separator/case.
- Migration note: существующие `/ocp/mnt/_lib_` и `/ocp/mnt/Splice` должны остаться в default mapping для бесшовного перехода.
