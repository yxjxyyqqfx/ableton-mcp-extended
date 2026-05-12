## _search_browser_by_name

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1942-1988`
**LOC delta**: ~47
**Live compat**: Live 11 + 12 (поиск идет через общие browser roots без ветвления по major version)

### Rationale (Russian)
Функция обеспечивает универсальный поиск по имени файла в нескольких корневых категориях браузера, не завязываясь на конкретный путь пользователя. Это полезный fallback-механизм для name-based lookup и диагностики. Логика компактная и переносимая без fork-специфичных констант.

### API Contract
```python
def _search_browser_by_name(self, browser, filename, max_depth=12):
```

### Examples
1. Поиск `"kick.wav"` проходит через `user_folders`, `samples`, `user_library` и возвращает первый loadable match.
2. При глубоко вложенной структуре `max_depth=6` ограничивает рекурсию и ускоряет обход.

### Tests
- `tests/unit/test_browser.py::test_search_browser_by_name_finds_first_loadable` (planned)
- `tests/integration/test_browser_live.py::test_search_browser_by_name_live_roots` (planned)

### English Description
Performs a case-insensitive recursive name search across a curated set of browser roots. It returns the first loadable BrowserItem match and gracefully skips problematic roots via exception-tolerant traversal.
