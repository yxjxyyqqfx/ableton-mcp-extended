## _browser_children

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1442-1494`
**LOC delta**: ~53
**Live compat**: Live 11 + 12 (версионных развилок нет; поведение опирается на безопасную интроспекцию объектов Browser API)

### Rationale (Russian)
Вспомогательная функция стабилизирует доступ к дочерним элементам браузера и снижает риск падений при нестандартных iterable-объектах Live API. Она ограничивает перебор (`max_items=512`) и защищает обход `children`/indexing через try/except. Это ключевой блок для безопасной навигации по дереву браузера.

### API Contract
```python
def _browser_children(self, browser_or_item):
```

### Examples
1. Вызов на `app.browser.samples` возвращает bounded-список child items даже если объект не list.
2. Вызов на строке/`None` возвращает `[]`, предотвращая ошибочную рекурсию в поисковых хелперах.

### Tests
- `tests/unit/test_browser.py::test_browser_children_safe_accessor` (planned)
- `tests/integration/test_browser_live.py::test_browser_children_live_vectors` (planned)

### English Description
Safe internal accessor for BrowserItem children that normalizes multiple Live object shapes (`children`, indexable vectors, iterables). It prevents traversal crashes and enforces bounded iteration, making downstream browser search functions more reliable.
