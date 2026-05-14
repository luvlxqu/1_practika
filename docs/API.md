# 📡 API Documentation — Safe Contact

## Основная информация

| Параметр | Значение |
|----------|----------|
| **Базовый URL** | `http://localhost:5000` |
| **Формат данных** | JSON |
| **Аутентификация** | JWT Bearer Token |
| **Swagger UI** | `http://localhost:5000/static/swagger-ui.html` |

---

## 🔐 Аутентификация

### POST /auth/login

Перенаправляет на страницу входа Logto.

**Ответ:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "client"
  }
}
```

### POST /auth/change-role

Смена роли. При первом вызове создаёт профиль (specialist или client).

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "role": "specialist"
}
```

**Допустимые роли:**

| Роль | Доступ |
|------|--------|
| `client` | Поиск и бронирование слотов |
| `specialist` | Создание и управление слотами |
| `admin` | Полный доступ к системе |
| `moderator` | Одобрение анкет специалистов |

**Ответ (200):**
```json
{
  "message": "Role changed successfully",
  "role": "specialist"
}
```

**Ошибки:**
```json
{
  "error": "Invalid role specified",
  "code": 400
}
```

### POST /auth/test-token/

Создаёт тестового пользователя (только для разработки).

**Ответ:**
```json
{
  "token": "eyJhbGciOiJI...",
  "user": {
    "email": "test@example.com",
    "role": "client"
  }
}
```

---

## 📅 Слоты

### POST /slots/create

Создание слотов (роль: specialist).

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "datetime": "2024-01-15T10:00:00",
  "duration": 60,
  "price": 3000
}
```

**Параметры:**

| Поле | Тип | Обязательное | Ограничения |
|------|-----|--------------|-------------|
| `datetime` | ISO 8601 | Да | Будущее время |
| `duration` | integer | Да | 30–180 минут |
| `price` | float | Нет | 0–100000 руб. |

**Ответ (201):**
```json
{
  "message": "Slot created",
  "slot": {
    "id": 1,
    "datetime": "2024-01-15T10:00:00",
    "duration": 60,
    "price": 3000,
    "status": "free"
  }
}
```

### GET /slots/get

Получить слоты текущего специалиста.

**Заголовки:** `Authorization: Bearer <token>`

**Ответ:**
```json
{
  "slots": [
    {
      "id": 1,
      "datetime": "2024-01-15T10:00:00",
      "duration": 60,
      "price": 3000,
      "status": "free"
    }
  ]
}
```

### GET /clients/get-slots

Получить свободные слоты специалиста (роль: client).

**Параметры запроса:**

| Параметр | Тип | Обязательное |
|----------|-----|--------------|
| `specialist_id` | integer | Да |

**Ответ:**
```json
{
  "slots": [
    {
      "id": 1,
      "specialist_name": "Иванов Иван",
      "datetime": "2024-01-15T10:00:00",
      "duration": 60,
      "price": 3000
    }
  ]
}
```

---

## 📝 Записи

### POST /clients/make-appointment/

Забронировать слот (роль: client).

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "slot_id": 1
}
```

**Ответ (201):**
```json
{
  "message": "Appointment created",
  "appointment": {
    "id": 1,
    "datetime": "2024-01-15T10:00:00",
    "specialist": "Иванов Иван",
    "duration": 60,
    "status": "confirmed"
  }
}
```

**Ошибки:**

| Код | Описание |
|-----|----------|
| 404 | Слот не найден |
| 409 | Слот уже забронирован |
| 403 | Недостаточно прав |

---

## 👤 Профиль специалиста

### PUT /specialists/update

Обновить профиль (роль: specialist).

**Заголовки:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Тело запроса (все поля опциональны):**
```json
{
  "name": "Иванов Иван",
  "specialization": "Клинический психолог",
  "experience": 5,
  "description": "Специализируюсь на КПТ...",
  "education": "МГУ, факультет психологии",
  "phone": "+7 (999) 123-45-67"
}
```

**Ответ:**
```json
{
  "message": "Profile updated",
  "specialist": {
    "id": 1,
    "name": "Иванов Иван",
    "specialization": "Клинический психолог",
    "experience": 5
  }
}
```

---

## ⚠️ Коды ошибок

| Код | Значение | Пример |
|-----|----------|--------|
| **400** | Неверный запрос | Обязательные поля не заполнены |
| **401** | Не авторизован | Токен отсутствует или истёк |
| **403** | Недостаточно прав | Клиент пытается создать слот |
| **404** | Не найдено | Ресурс не существует |
| **409** | Конфликт | Слот уже занят |
| **422** | Ошибка валидации | Некорректный формат данных |
| **500** | Внутренняя ошибка | Проблема на сервере |

---

## 🧪 Тестирование через cURL

```bash
# 1. Получить тестовый токен
TOKEN=$(curl -s -X POST http://localhost:5000/auth/test-token/ | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# 2. Сменить роль на specialist
curl -X POST http://localhost:5000/auth/change-role \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"specialist"}'

# 3. Создать слот
curl -X POST http://localhost:5000/slots/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"datetime":"2024-01-15T10:00:00","duration":60,"price":3000}'

# 4. Получить свои слоты
curl http://localhost:5000/slots/get \
  -H "Authorization: Bearer $TOKEN"
```