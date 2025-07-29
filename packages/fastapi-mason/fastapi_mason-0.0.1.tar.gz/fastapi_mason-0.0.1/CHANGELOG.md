# Changelog - FastAPI+ Library

Все значимые изменения в этом проекте будут документированы в этом файле.

## [2.1.1] - 2024-12-19

### 🐛 Bug Fixes (Action Decorators)

**Fixed critical issues with @action decorators:**

1. **Route Conflict Protection**
   - Actions no longer automatically override existing routes
   - Added `override_existing=False` parameter to `@action` decorator
   - Warning messages when route conflicts are detected
   - Explicit opt-in for route overriding with `override_existing=True`

2. **FastAPI Documentation**
   - Removed `self` parameter from action endpoints in FastAPI /docs
   - Clean, professional API documentation without implementation details
   - Proper parameter display for all action methods

3. **Function Signatures**
   - Fixed function signatures in action endpoints
   - No more `*args, **kwargs` in FastAPI documentation
   - Proper parameter names and types displayed
   - Correct request/response models in API docs

**Updated Files:**
- `app/fastapi_plus/decorators.py` - Enhanced @action decorator
- `app/fastapi_plus/generics.py` - Fixed action route registration
- `app/project/views.py` - Updated examples with proper usage

**Migration Guide:**
- Existing actions will work without changes
- To override existing routes, add `override_existing=True` to @action
- Check for route conflict warnings in console output

---

## [2.1.0] - 2024-01-XX

### ✨ Новые возможности

#### 🔐 Система Permissions
- Добавлен модуль `permissions.py` с системой авторизации
- Новые permission классы:
  - `BasePermission` - базовый абстрактный класс
  - `AllowAny` - разрешить доступ всем
  - `DenyAll` - запретить доступ всем
  - `IsAuthenticated` - только для аутентифицированных пользователей
  - `IsAdminUser` - только для администраторов
  - `IsOwner` - только для владельцев объектов
  - `IsOwnerOrReadOnly` - владельцы могут редактировать, остальные только читать
  - `IsAuthenticatedOrReadOnly` - аутентифицированные могут редактировать
- Интеграция permissions в `GenericViewSet` и все миксины
- Автоматическая проверка permissions для всех действий

#### 🔍 Система Фильтрации
- Добавлен модуль `filters.py` с фильтрацией querysets
- Новые filter backends:
  - `BaseFilterBackend` - базовый класс для фильтров
  - `SearchFilter` - текстовый поиск по указанным полям
  - `OrderingFilter` - сортировка по полям
  - `DjangoFilterBackend` - фильтрация по точным значениям полей
  - `RangeFilter` - фильтрация по диапазонам (min/max, after/before)
- Интеграция с `GenericViewSet`:
  - `filter_backends` - список filter backends
  - `search_fields` - поля для поиска
  - `filterset_fields` - поля для точной фильтрации
  - `ordering_fields` - поля для сортировки
  - `ordering` - сортировка по умолчанию
  - `range_fields` - поля для диапазонной фильтрации

#### 🎯 Custom Actions (@action декоратор)
- Добавлен декоратор `@action` для создания custom endpoints
- Поддержка detail и non-detail actions
- Настраиваемые HTTP методы, URL paths, и имена routes
- Автоматическая интеграция с permissions
- Автоматическое обнаружение и регистрация action методов

#### 🔧 Middleware System
- Добавлен модуль `middleware.py` с middleware системой
- Базовый класс `BaseViewSetMiddleware` с хуками для всех действий
- Встроенные middleware:
  - `LoggingMiddleware` - логирование запросов/ответов
  - `TimingMiddleware` - измерение времени выполнения
  - `CachingMiddleware` - простое кэширование ответов
- `MiddlewareManager` для управления выполнением middleware

### 🛠 Улучшения

#### ViewSets
- Добавлены новые классы ViewSets:
  - `CreateOnlyViewSet` - только создание
  - `ListCreateViewSet` - список и создание
  - `UpdateOnlyViewSet` - только обновление
  - `ListUpdateViewSet` - список и обновление
- Все ViewSets теперь поддерживают permissions и фильтрацию
- Улучшена интеграция с Request объектами

#### Response Wrappers
- Добавлен `StatusResponseWrapper` для ответов с полем status

### 📚 Документация и примеры
- Обновлена документация в `__init__.py`
- Добавлен `DEMO_V2_1_0.py` с полными примерами использования
- Улучшены docstrings во всех модулях

---

## [2.0.1] - 2024-01-XX

### 🔧 Критические исправления

#### Декоратор @viewset
- **ИСПРАВЛЕНО**: Упрощена логика декоратора `@viewset`
- **УДАЛЕНО**: Хрупкая модификация function signatures
- **ДОБАВЛЕНО**: Лучшая обработка ошибок и валидация
- Декоратор теперь более надежный и менее зависимый от внутренней структуры FastAPI

#### Валидация конфигурации
- **ДОБАВЛЕНО**: Модуль `validation.py` с комплексной валидацией
- **ДОБАВЛЕНО**: Класс исключения `ViewSetConfigError`
- **ДОБАВЛЕНО**: Функция `validate_viewset_config()` для проверки:
  - Наличие и корректность model
  - Валидность Pydantic схем
  - Корректность pagination классов
  - Валидность response wrappers
- **ДОБАВЛЕНО**: Валидация action методов с `validate_action_method()`
- Все ViewSets теперь автоматически валидируются при инициализации

#### CursorPagination
- **ИСПРАВЛЕНО**: Полная реализация `CursorPagination`
- **ДОБАВЛЕНО**: Методы `encode_cursor()` и `decode_cursor()`
- **ДОБАВЛЕНО**: Поддержка `cursor_field` и `ordering` конфигурации
- **ДОБАВЛЕНО**: Поля `previous_cursor`, `has_previous`, `has_next`
- **УЛУЧШЕНО**: Метод `fill_meta()` с полной логикой cursor навигации
- **ДОБАВЛЕНО**: Автоматическое определение типов полей для cursor

#### Импорты и API
- **ИСПРАВЛЕНО**: Полностью переписан `__init__.py` с корректными импортами
- **ДОБАВЛЕНО**: Полный список `__all__` экспортов
- **ИСПРАВЛЕНО**: Примеры в документации теперь используют правильные классы
- Библиотека теперь пригодна для использования "из коробки"

### 🔄 Обратная совместимость
- Все изменения обратно совместимы с кодом v2.0.0
- Старые ViewSets продолжают работать без изменений
- Добавлена только новая функциональность

---

## [2.0.0] - 2024-01-XX (Исходная версия)

### 🎉 Первый релиз

#### Базовая архитектура
- `GenericViewSet` - базовый класс с бизнес-логикой
- Система миксинов для добавления routes:
  - `ListMixin` - GET /
  - `RetrieveMixin` - GET /{id}
  - `CreateMixin` - POST /
  - `UpdateMixin` - PUT/PATCH /{id}
  - `DestroyMixin` - DELETE /{id}

#### ViewSets
- `ModelViewSet` - полный CRUD
- `ReadOnlyViewSet` - только чтение

#### Пагинация
- `DisabledPagination` - без пагинации
- `LimitOffsetPagination` - limit/offset стиль
- `PageNumberPagination` - номера страниц
- `CursorPagination` - cursor-based (базовая реализация)

#### Response Wrappers
- `ResponseWrapper` - базовый класс
- `PaginatedResponseWrapper` - для пагинированных ответов
- `ResponseDataWrapper` - обертка с полем data
- `ListDataWrapper` - для списков
- `PaginatedResponseDataWrapper` - стандартная пагинированная обертка

#### Утилиты
- `sort_routes_by_specificity()` - сортировка routes
- Система типов с `ModelType`, `SchemaType`, `PaginationType`

#### Декораторы
- `@viewset` - автоматическая регистрация ViewSet

---

## Планы развития

### v2.2.0 (планируется)
- 🔄 Bulk operations (массовые операции)
- 📊 Система метрик и мониторинга
- 🗄️ Улучшенное кэширование с Redis
- 🔒 Расширенные permission классы

### v3.0.0 (в разработке)
- 🚀 Полная поддержка async context managers
- 📡 Streaming responses для больших datasets
- 🔧 Plugin система для расширений
- 🎨 Improved serialization система

---

## Как обновиться

### С v2.0.0 до v2.0.1
```bash
# Обновление обратно совместимо
pip install fastapi-plus==2.0.1
```

### С v2.0.1 до v2.1.0
```bash
pip install fastapi-plus==2.1.0
```

Новые возможности опциональны - старый код продолжит работать без изменений.

Для использования новых возможностей:
```python
# Добавьте permissions
permission_classes = [IsAuthenticated]

# Добавьте фильтрацию
filter_backends = [SearchFilter, DjangoFilterBackend]
search_fields = ['name', 'email']

# Добавьте custom actions
@action(methods=['POST'], detail=True)
async def custom_action(self, item_id: int):
    # ваш код
    pass
```
