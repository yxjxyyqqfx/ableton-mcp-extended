## load_browser_sample_by_name

**Status**: rework
**Source**: `/legacy/MCP_Server/server.py:722-753`; `/legacy/AbletonMCP_Remote_Script/__init__.py:1921-1940`; `/legacy/AbletonMCP_Remote_Script/__init__.py:1853-1919`
**LOC delta**: ~119
**Live compat**: Live 11 + 12 (операция загрузки совместима, но текущий contract ограничен fork-специфичными root path)

### Rationale (Russian)
Функция решает практичную задачу загрузки sample по имени на Drum Rack pad, но сейчас контракт искусственно зажат двумя фиксированными корнями. Это делает API удобным для текущего форка, но слабопереносимым для других setups и user folders. Поэтому фича полезна, но требует переработки публичного интерфейса.

### API Contract
```python
def load_browser_sample_by_name(
    ctx: Context,
    track_index: int,
    filename: str,
    search_root: str,
    pad_note: int = 36,
    rack_device_index: int = 1,
    replace: bool = False,
) -> str:

def _load_browser_sample_by_name(self, track_index, rack_device_index, pad_note,
                                 filename, search_root="User_folders/Splice",
                                 replace=False):

def _find_browser_item_by_name_under_path(self, search_root, filename, max_depth=12):
```

### Examples
1. `load_browser_sample_by_name(track_index=1, filename="snare.wav", search_root="User_folders/Splice", pad_note=38)` загружает сэмпл на pad 38.
2. `load_browser_sample_by_name(..., search_root="User_folders/_lib_", replace=True)` сначала очищает chain на pad, затем загружает найденный file match.

### Tests
- `tests/unit/test_browser.py::test_load_browser_sample_by_name_validates_root` (planned)
- `tests/integration/test_browser_live.py::test_load_browser_sample_by_name_live` (planned)

### English Description
Loads a sample onto a Drum Rack pad by filename under a given browser path. While operational, the public contract is currently constrained to two hardcoded user-folder roots, which limits portability across installations.

### Rework plan
- Вынести `valid_roots` из wrapper/handler в настраиваемый модульный конфиг (или dependency-injected validator), чтобы корни не были захардкожены в коде.
- Suggested API after rework: `load_browser_sample_by_name(..., search_root: str | None = None, allowed_roots: list[str] | None = None)` с безопасным default policy.
- Migration note: текущие вызовы с `User_folders/_lib_` и `User_folders/Splice` должны продолжить работать как backward-compatible defaults.
