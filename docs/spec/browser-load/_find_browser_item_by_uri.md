## _find_browser_item_by_uri

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:2929-2981`
**LOC delta**: ~53
**Live compat**: Live 11 + 12 (используются общие browser categories; нет hard version split)

### Rationale (Russian)
Это основной URI-резолвер для загрузки browser items по стабильному идентификатору, включая расширенный список root categories (`samples`, `user_library`, `user_folders` и т.д.). Он повышает шанс найти item в разных конфигурациях библиотеки Live. Ограничение глубины рекурсии удерживает предсказуемое время обхода.

### API Contract
```python
def _find_browser_item_by_uri(self, browser_or_item, uri, max_depth=10, current_depth=0):
```

### Examples
1. Для `uri="query:Samples#FileId_123"` функция находит item через ветку `samples` и возвращает BrowserItem.
2. Для несуществующего URI возвращает `None` без падения, даже если часть корней недоступна.

### Tests
- `tests/unit/test_browser.py::test_find_browser_item_by_uri_expanded_roots` (planned)
- `tests/integration/test_browser_live.py::test_find_browser_item_by_uri_live` (planned)

### English Description
Recursively resolves a BrowserItem by URI across a broad, load-relevant set of browser roots. The implementation is exception-tolerant and depth-bounded, which improves reliability in heterogeneous Live browser trees.
