## _find_browser_item_by_name_under_path

**Status**: rework
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1853-1919`
**LOC delta**: ~67
**Live compat**: Live 11 + 12 (алгоритм совместим, ограничение в hardcoded `search_root`)

### Rationale (Russian)
Хелпер реализует полезный DFS-поиск loadable sample по имени под заданным browser path и корректно обходит `user_folders` vector. Проблема не в механике поиска, а в том, что контракт валидирует только два фиксированных root path. Это делает функцию внутренне надежной, но архитектурно недостаточно универсальной.

### API Contract
```python
def _find_browser_item_by_name_under_path(self, search_root, filename, max_depth=12):
```

### Examples
1. Поиск `"hat_closed.wav"` под `User_folders/Splice` возвращает первый `is_loadable` match в пределах `max_depth`.
2. Если одна из частей `search_root` не найдена в browser tree, вызывается `ValueError` с указанием проблемного сегмента пути.

### Tests
- `tests/unit/test_browser.py::test_find_browser_item_by_name_under_path_dfs` (planned)
- `tests/integration/test_browser_live.py::test_find_browser_item_by_name_under_path_live` (planned)

### English Description
Internal DFS resolver that finds an exact filename match under a browser path, including explicit traversal of `user_folders`. It is robust in traversal behavior but currently constrained by hardcoded accepted roots.

### Rework plan
- Отделить обход дерева от политики валидации root: принимать внешний validator или набор допустимых корней как параметр.
- Suggested API after rework: `_find_browser_item_by_name_under_path(search_root, filename, max_depth=12, root_validator=None)`.
- Migration note: сохранить текущий strict-режим как default validator, чтобы старые сценарии не изменили поведение внезапно.
