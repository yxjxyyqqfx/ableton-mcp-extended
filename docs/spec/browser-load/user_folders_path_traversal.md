## user_folders_path_traversal

**Status**: rework
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:3850-4066` (special-case block: `3893-3981`)
**LOC delta**: ~217
**Live compat**: Live 11 + 12 (special-case введен для стабильности Live Browser vector доступа, без explicit version gating)

### Rationale (Russian)
Специальная ветка для `user_folders` защищает от нестабильного generic traversal, который может рвать TCP-соединение с Live. Это важное практическое поведение, но оно смешано с общим path-walk в одном методе и требует структурной декомпозиции. Отдельный traversal policy для `user_folders` упростит сопровождение и тестирование.

### API Contract
```python
def get_browser_items_at_path(self, path):
```

### Examples
1. Запрос пути `"user_folders"` возвращает список root entries из `app.browser.user_folders` с безопасным bounded-индексированием.
2. Запрос `"user_folders/Splice/Samples"` проходит по сегментам пути case-insensitive и возвращает дочерние items текущего узла.

### Tests
- `tests/unit/test_browser.py::test_user_folders_path_traversal_special_case` (planned)
- `tests/integration/test_browser_live.py::test_get_browser_items_at_path_user_folders_live` (planned)

### English Description
Implements browser path traversal with an explicit `user_folders` special-case to avoid unstable generic traversal behavior. This improves runtime safety, but the current monolithic method should be split into dedicated traversal strategies.

### Rework plan
- Выделить `user_folders` traversal в отдельный helper/service и унифицировать его контракт с generic category traversal.
- Suggested API after rework: `get_browser_items_at_path(path, traversal_policy="auto")` + internal strategies (`user_folders`, `generic`).
- Migration note: сохранить текущую семантику ответа (`path`, `name`, `uri`, `items`) и case-insensitive matching сегментов пути.
