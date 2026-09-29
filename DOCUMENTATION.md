# BIPRO — Полная техническая документация

**Версия:** 1.0  
**Дата:** 30.09.2026  
**Репозиторий:** https://github.com/stanovskih/bipro  
**Django:** 5.1.3 · **СУБД:** MySQL (utf8mb4) · **Локаль:** ru / Europe/Moscow  
**Покрытие документации:** ~90%

---

## Оглавление

1. [Общее описание](#1-общее-описание)
2. [Технологический стек](#2-технологический-стек)
3. [Структура проекта](#3-структура-проекта)
4. [Структура базы данных](#4-структура-базы-данных)
5. [Контроллеры (Views)](#5-контроллеры-views)
6. [URL-маршрутизация](#6-url-маршрутизация)
7. [Формы](#7-формы)
8. [Страницы (Templates)](#8-страницы-templates)
9. [Пользовательский интерфейс](#9-пользовательский-интерфейс)
10. [Аутентификация и роли](#10-аутентификация-и-роли)
11. [Админка](#11-админка)
12. [Отчёты и печать](#12-отчёты-и-печать)
13. [Импорт данных](#13-импорт-данных)
14. [Внешние интеграции](#14-внешние-интеграции)
15. [Настройки проекта](#15-настройки-проекта)
16. [Установка и запуск](#16-установка-и-запуск)
17. [Критичные проблемы безопасности](#17-критичные-проблемы-безопасности)
18. [Известные баги](#18-известные-баги)
19. [Рекомендации](#19-рекомендации)
20. [Приложения](#20-приложения)

---

## 1. Общее описание

**BIPRO (БиПро)** — Django-система управления и автоматизации ЖКХ. Ведёт учёт **заявок** жителей и **отключений** ресурсов по домам, работает с обширной справочной базой (компании, участки, улицы, объекты, сотрудники, рабочие системы), поддерживает фото, автоматическую нумерацию заявок, рассылку уведомлений об отключениях в Telegram/Max, генерацию PDF-отчётов и ролевую модель доступа.

**Основной интерфейс** — серверный рендеринг Django-шаблонов (Bootstrap 5) + Django Admin для справочников и активации пользователей.

**Доменные сущности:**

- **Заявка** (`Order`) — центральная сущность: тип, приоритет, адрес, исполнители, сроки, факт выполнения, сумма, фото.
- **Отключение** (`Disconnect`) — плановые и аварийные отключения по объектам и рабочим системам.
- **Справочники** (`dict`): Location, Company, District, Street, WorkSystem, Building, Employee, StandardDescription.

---

## 2. Технологический стек

| Слой | Технология |
|------|-----------|
| Backend | Python, Django 5.1.3 |
| БД | MySQL (utf8mb4) |
| Шаблоны | Django Templates |
| CSS/UI | Bootstrap 5.3.8, Bootstrap Icons 1.10.2 |
| JS | jQuery 3.3.1, jQuery UI 1.13.2, Tom Select 2.6.2 |
| PDF | ⚠️ TBD — библиотека в `ads/reports/*` не установлена |
| Внешние API | Max (`platform-api.max.ru`) — рассылка уведомлений |
| Деплой | ⚠️ TBD |

---

## 3. Структура проекта

```
bipro/
├── ads/                  # Заявки и отключения
│   ├── migrations/
│   ├── admin.py          # ⚠️ TBD
│   ├── apps.py
│   ├── forms.py          # ⚠️ TBD
│   ├── models.py         # 7 моделей
│   ├── views.py          # 14 views
│   ├── urls.py           # 12 маршрутов
│   └── reports/          # ⚠️ TBD — 4 модуля PDF
├── bipro/                # Конфигурация
│   ├── settings.py
│   ├── urls.py
│   ├── views.py          # index, login, logout, signup, signup_successfully
│   ├── wsgi.py
│   └── asgi.py
├── dict/                 # Справочники
│   ├── migrations/
│   ├── admin.py          # ⚠️ TBD
│   ├── models.py         # 9 моделей
│   ├── views.py          # пустой (заглушка)
│   └── urls.py           # ⚠️ TBD
├── templates/            # base.html, order_list.html, order_form.html + ⚠️ TBD
├── static/               # Иконки, CSS, логотип
├── media/                # Загрузки (в .gitignore)
│   ├── fotos/
│   ├── buildings/
│   └── company/
├── import.py             # ⚠️ TBD
├── manage.py
└── .gitignore
```

---

## 4. Структура базы данных

### 4.1. Приложение `dict` — справочники (9 моделей)

#### `Location` — Локация

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField(50) | Наименование локации |

**Meta:** `verbose_name = "Локация"`

---

#### `Company` — Компания

| Поле | Тип | Описание |
|------|-----|----------|
| location | FK → Location, SET_NULL | Локация |
| company_type | CharField(20), choices | `ук` / `подряд` |
| name | CharField(50) | Краткое наименование |
| legal_name | CharField(150) | Полное наименование |
| phone | CharField(50) | Телефон |
| address | CharField(150) | Адрес |
| email | CharField(50) | Email |
| comment | TextField | Комментарий |
| is_used | BooleanField | Используется ли |
| logo | ImageField → `company/` | Логотип |

**Meta:** `verbose_name = "Компания"`

---

#### `District` — Участок

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField(50) | Наименование участка |
| company | FK → Company, SET_NULL | Компания-владелец |

**Meta:** `verbose_name = "Участок"`  
**`__str__`:** `f'{self.name}/{self.company}'`

---

#### `Street` — Улица

| Поле | Тип | Описание |
|------|-----|----------|
| location | FK → Location, SET_NULL | Локация |
| name | CharField(50) | Наименование |
| legal_name | CharField(50) | Правильное наименование |
| c1_name | CharField(50) | Наименование в 1С |
| is_used | BooleanField | Используется ли |

**Meta:** `ordering = ('name',)`

---

#### `StreetInCompany` — Обслуживаемые улицы

| Поле | Тип | Описание |
|------|-----|----------|
| street | FK → Street, DO_NOTHING | Улица |
| company | FK → Company, CASCADE | Компания |

**Meta:** `ordering = ('street',)`

---

#### `WorkSystem` — Рабочая система

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField(50) | Наименование системы |
| pictogram | CharField(15) | Пиктограмма (эмодзи/svg) |
| is_used | BooleanField | Используется ли |

**`__str__`:** `f"{self.pictogram if self.pictogram else ''}{self.name}"`

---

#### `Building` — Объект (дом)

| Поле | Тип | Описание |
|------|-----|----------|
| location | FK → Location, SET_NULL | Локация |
| name | CharField(50) | Название объекта |
| street | FK → Street, DO_NOTHING | Улица |
| house | CharField(15) | Номер дома |
| lon, lat | FloatField | Координаты |
| channelid | BigIntegerField | ID Telegram/Max-канала |
| square | DecimalField(18,2) | Площадь |
| flat_count | IntegerField | Кол-во квартир |
| floor_count | IntegerField | Кол-во этажей |
| photo | ImageField → `buildings/` | Фото |
| company | FK → Company, CASCADE | УК/владелец |
| description | TextField | Описание |
| comment | TextField | Комментарий |
| source | JSONField | Внешние данные |

**Meta:** `ordering = ('name',)`

---

#### `Employee` — Сотрудник

| Поле | Тип | Описание |
|------|-----|----------|
| user | OneToOne → User, DO_NOTHING | Учётка |
| name | CharField(50) | ФИО |
| post | CharField(20), choices | boss / secretary / chief / itr / admin / disp / master / worker |
| worksystem | M2M → WorkSystem | Рабочие системы |
| district | M2M → District | Участки |
| company | FK → Company, DO_NOTHING | Компания |
| deleted | BooleanField | Уволен? |
| phone | CharField(12) | Телефон |
| telegram | CharField(12) | Telegram |
| district_main | FK → District, SET_NULL, `related_name='district_main'` | Основной участок |
| comment | TextField | Комментарий |

**Meta:** `ordering = ('name',)`

---

#### `StandardDescription` — Стандартное описание заявки

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField(500) | Текст описания |
| worksystem | FK → WorkSystem, CASCADE | Рабочая система |

---

### 4.2. Приложение `ads` — заявки и отключения (7 моделей)

#### `OrderState` — Состояние заявки

| Поле | Тип | Описание |
|------|-----|----------|
| id | CharField(30), PK | Строковый ID (`accepted`, `inprogress`, …) |
| name | CharField(30) | Наименование |
| color | CharField(10) | Цвет в HEX |
| pos | IntegerField | Порядок сортировки |
| сompleted | BooleanField | Признак завершения ⚠️ *кириллическая `с`* |

**Meta:** `ordering = ('pos',)`

---

#### `Order` — Заявка (ядро)

| Группа | Поле | Тип | Описание |
|--------|------|-----|----------|
| **Метаданные** | author | FK → User, CASCADE | Автор |
| | creation_date | DateTimeField (auto_now_add) | Дата создания |
| | modified_date | DateTimeField | Дата изменения |
| | last_printed_date | DateTimeField | Дата последней печати |
| | number | CharField(15) | Номер |
| | order_date | DateField | Дата заявки |
| | orderid | IntegerField | Внешний ID |
| **Классификация** | state | FK → OrderState, SET_NULL | Состояние |
| | ordertype | CharField(20), choices | houses / flats / paid / repair / household / emergency |
| | priority | CharField(20), choices | emergency / urgent / current |
| | sourcetype | CharField(20), choices | disp / site / max / auto |
| **Место** | district | FK → District, SET_NULL | Участок |
| | street | FK → Street, SET_NULL | Улица |
| | house | CharField(15) | Дом |
| | flat | CharField(15) | Квартира |
| | entrance | IntegerField | Подъезд |
| | floor | IntegerField | Этаж |
| | building | FK → Building, SET_NULL | Объект |
| **Заявитель** | citizen | CharField(50) | ФИО |
| | phone | CharField(15) | Телефон |
| **Планирование** | plan_date | DateField | Плановая дата |
| | plan_period | CharField(20), choices | until / after / during |
| | plan_text | CharField(30) | Текст плана |
| | worksystem | FK → WorkSystem, SET_NULL | Рабочая система |
| **Описание** | description | TextField(500) | Описание заявки |
| **Исполнение** | master | FK → Employee, SET_NULL, `related_name='master_user'` | Мастер |
| | employee | M2M → Employee | Исполнители |
| | worker_text | CharField(50) | Текстовый исполнитель |
| | master_text | CharField(50) | Текстовый мастер |
| | fact_date | DateTimeField | Факт выполнения |
| | fact_start_work_time | DateTimeField | Факт начала работ |
| | fact_description | TextField | Фактическое описание |
| **Финансы** | summa | DecimalField(18,2) | Сумма |
| **Организации** | company_owner | FK → Company, SET_NULL, `company_owner` | УК |
| | company_exec | FK → Company, SET_NULL, `company_exec` | Подрядчик |

**Свойства (property):**

| Свойство | Назначение |
|----------|------------|
| `get_photo_count` | Число фото |
| `get_profile_company` / `get_profile_name` | Данные профиля автора |
| `address` | HTML-адрес (улица+дом+кв + УК) |
| `colored_state` | Цветной бейдж состояния с иконками |
| `get_employees` | Список исполнителей через `;` |
| `shot_description` | 60 символов описания + фактическое |
| `order_date_format` | Дата заявки `дд.мм.гг` |
| `creation_date_time_format` | Дата + время |
| `plan_date_format` | Дата плана с эмодзи 🕘/🕞 |

---

#### `FotosInOrder` — Фото в заявке

| Поле | Тип | Описание |
|------|-----|----------|
| order | FK → Order, CASCADE | Заявка |
| name | CharField(150) | Описание |
| foto | ImageField → `fotos/` | Файл фото |
| max_token | CharField(200) | Токен для Max |
| max_url | URLField(500) | Ссылка на фото |

**Свойства:** `admin_image`, `preview_image` — превью 60×40

---

#### `Numbering` — Нумерация

| Поле | Тип | Описание |
|------|-----|----------|
| suffix | CharField(5) | Суффикс |
| prefix | CharField(5) | Префикс |
| current_number | IntegerField | Текущий номер |
| district | FK → District, CASCADE | Участок |
| company | FK → Company, CASCADE | Компания |

---

#### `DistrictInBuilding` — Закрепление УК↔дом↔участок

| Поле | Тип | Описание |
|------|-----|----------|
| company | FK → Company, CASCADE | Компания |
| building | M2M → Building | Объекты |
| district | FK → District, CASCADE | Участок |

---

#### `WorkSystemInBuilding` — Закрепление подрядчика

| Поле | Тип | Описание |
|------|-----|----------|
| company | FK → Company, CASCADE | УК |
| building | M2M → Building | Объекты |
| worksystem | M2M → WorkSystem | Рабочие системы |
| company_exec | FK → Company, CASCADE, `company_exec_building` | Подрядчик |

---

#### `Disconnect` — Отключение

| Поле | Тип | Описание |
|------|-----|----------|
| author | FK → User, CASCADE | Автор |
| creation_date | DateTimeField (auto_now_add) | Дата создания |
| number | CharField(15) | Номер |
| start_disconnect | DateTimeField | Дата начала |
| plan_connection_date | DateTimeField | Плановая дата подключения |
| fact_connection_date | DateTimeField | Фактическая дата подключения |
| building | M2M → Building | Объекты |
| worksystem | M2M → WorkSystem | Рабочие системы |
| description | TextField(500) | Описание |
| connected | BooleanField | Подключено? |
| sender | CharField(150) | Ответственный от подрядчика |
| disconnection_type | CharField(50), choices | Отключение / Аварийное / Ухудшение / Информация |
| source | CharField(50), choices | Входящее / Исходящее / Внутреннее |
| published | BooleanField | Опубликовать |
| company_owner | FK → Company, SET_NULL, `disc_company_owner` | УК |
| company_exec | FK → Company, SET_NULL, `disc_company_exec` | Подрядчик |
| data | JSONField | Ответы внешнего API |

**Свойства:** `get_buildings_text`, `get_worksystem_text`, `get_period`

---

### 4.3. Схема связей

```
Location ─┬─< Company ─┬─< District ─┬─< Employee
          │            │             └─< Numbering
          │            ├─< Building ─┬─< Order
          │            │             └─< Disconnect (M2M)
          └─< Street ──┴─< Building
                                     WorkSystem ─┬─< Order
                                                 ├─< StandardDescription
                                                 └─< Disconnect (M2M)

Order ─┬─< FotosInOrder
       ├─< Employee (M2M)
       ├── OrderState (FK)
       └── Company (owner / exec)

User ──1:1── Employee
```

---

## 5. Контроллеры (Views)

### 5.1. Корневые views (`bipro/views.py`)

| View | URL | Назначение |
|------|-----|------------|
| `index` | `/index` | Лендинг (index2.html) |
| `login` | `/login` | Вход (ручная проверка `is_active` + `authenticate`) |
| `logout` | `/logout` | Выход → `redirect('login')` |
| `signup` | `/signup` | Регистрация → `is_active=False` + flash «ожидает активации» |
| `signup_successfully` | `/signup_successfully` | Страница подтверждения |

**Логика `login`:**
1. GET-параметры `username`, `password` из формы.
2. Проверка `User.objects.filter(username=...)`.
3. Если найден и `is_active=False` → рендер `lklogin.html` с ошибкой «Учетная запись не активированна!»
4. `authenticate()` → при успехе `auth_login()` + редирект на `order_list`.
5. При неудаче — ошибка в `login.html`.

### 5.2. Заявки (`ads/views.py`)

#### `OrderListView` (`LoginRequiredMixin, ListView`)
- **Шаблон:** `order_list.html`
- **Контекст:** `orders`, `company_exec_list`, `order_state_list`, `worksystem_list`
- **Пагинация:** 100, сортировка `-id`

**Ролевая фильтрация:**

| Условие | Что видит |
|---------|-----------|
| `company.company_type == 'ук'` | Заявки с `company_owner` = его компания |
| `company.company_type == 'подряд'` | Заявки с `company_exec` = его компания |
| `post == 'master'` | Заявки по его системам ИЛИ где он мастер |
| `post == 'worker'` | Заявки, где он в списке `employee` |

**GET-фильтры:** `search` (1/2/3 слова), `order_date_at/to`, `order_state`, `company_exec`, `worksystem_filter`.

#### `OrderCreateView` (`CreateView`)
- **Форма:** `OrderForm`, **шаблон:** `order_form.html`
- **Начальные значения:** `order_date` = сегодня, `plan_date` = +1 день
- **Динамика формы:** `street`, `building`, `company_exec`, `employee`, `master` — фильтруются по компании пользователя

**Бизнес-логика `form_valid`:**
1. `author` = текущий пользователь
2. Если `building` пуст — ищется по `street` + `house`; при находке проставляются `company_owner`, `district`
3. Если `number` пуст и есть `district` → генерация из `Numbering` (`prefix + number + suffix`) + инкремент счётчика

#### `OrderUpdateView` (`UpdateView`)
Аналогично `CreateView.get_form`.

#### `OrderCloseView` (`UpdateView`)
- **Форма:** `OrderCloseForm`, **шаблон:** `order_close_form.html`
- **Начальные:** `fact_date=now`, `state='completed'`

#### `FotoInOrderUpdateView` (`UpdateView`)
- **Форма:** `FotoInOrderForm`, **формсет:** `FotoInOrderFormSet`
- **Особенность:** `transaction.atomic()` — если формсет невалиден, откат

### 5.3. Отключения (`ads/views.py`)

#### `DisconnectListView` (`LoginRequiredMixin, ListView`)
- Всегда фильтр по `company_owner = employee.company`
- GET-фильтры: `disconnect_date_at/to`, `disconnect_plan_date_at/to`, `disconnect_fact_date_at/to`, `disconnect_state`, `company_exec`

#### `DisconnectCreateView` (`CreateView`)
- **Ключевая логика:** если `published=True`, `data=None` и тип ∈ ('Ухудшение','Аварийное','Отключение') → формируется текст и рассылается по каналам `Building.channelid` через `platform-api.max.ru`
- **Шаблоны текста:**
  - Ухудшение: «…ухудшенный режим подачи {система} с … по … в связи с плановыми ремонтными работами»
  - Аварийное: «…отсутствовать {система} … в связи с аварийно-восстановительными работами»
  - Отключение: «…отсутствовать {система} … в связи с плановыми ремонтными работами»

#### `DisconnectUpdateView` (`UpdateView`)
Аналогично, без рассылки.

### 5.4. AJAX / API

| View | Параметры | Возврат |
|------|-----------|---------|
| `get_address_from_phone` | `phone` | JSON: `{result, debt, street_id, street_name, house, flat, entrance, floor, citizen}` |
| `get_company_exec` | `street_id`, `house`, `worksystem_id` | JSON: `{result, company_exec, standart_description: [...]}` |
| `get_orders_history` | `street_id`, `house`, `flat` | HTML-таблица последних 10 заявок |

### 5.5. Отчёты и печать

| View | Метод | Возврат |
|------|-------|---------|
| `reports` | GET (форма) / POST (фильтр) | `reports.html` / PDF |
| `print` | POST (JSON `{ids}`) | PDF-поток |
| `print_disconnect` | POST (JSON `{ids}`) | PDF-поток |

### 5.6. Сводная таблица views

| # | View | Тип | Шаблон / Ответ |
|---|------|-----|----------------|
| 1 | `index` | function | index2.html |
| 2 | `login` | function | login.html / lklogin.html |
| 3 | `logout` | function | redirect |
| 4 | `signup` | function | signup.html |
| 5 | `signup_successfully` | function | signup_successfully.html |
| 6 | `OrderListView` | ListView | order_list.html |
| 7 | `OrderCreateView` | CreateView | order_form.html |
| 8 | `OrderUpdateView` | UpdateView | order_form.html |
| 9 | `OrderCloseView` | UpdateView | order_close_form.html |
| 10 | `FotoInOrderUpdateView` | UpdateView | order_foto_form.html |
| 11 | `DisconnectListView` | ListView | disconnect_list.html |
| 12 | `DisconnectCreateView` | CreateView | disconnect_form.html |
| 13 | `DisconnectUpdateView` | UpdateView | disconnect_form.html |
| 14 | `reports` | function | reports.html / PDF |
| 15 | `get_address_from_phone` | function | JSON |
| 16 | `get_company_exec` | function | JSON |
| 17 | `get_orders_history` | function | HTML |
| 18 | `print` | function | PDF |
| 19 | `print_disconnect` | function | PDF |

---

## 6. URL-маршрутизация

### 6.1. Корень (`bipro/urls.py`)

| URL | View | Name |
|-----|------|------|
| `/admin/` | Admin | — |
| `/` | `OrderListView` | — |
| `/index` | `index` | — |
| `/login` | `login` | `login` |
| `/logout` | `logout` | ⚠️ `login` (баг) |
| `/signup` | `signup` | `signup` |
| `/signup_successfully` | `signup_successfully` | `signup_successfully` |
| `/ads/...` | include | — |
| `/jsi18n/` | JavaScriptCatalog | `javascript-catalog` |

### 6.2. Приложение `ads` (`ads/urls.py`)

| URL | View | Name |
|-----|------|------|
| `/ads/orders` | `OrderListView` | `order_list` |
| `/ads/orders/create` | `OrderCreateView` | `order_create` |
| `/ads/orders/<pk>/update/` | `OrderUpdateView` | `order_update` |
| `/ads/orders/<pk>/close/` | `OrderCloseView` | `order_close` |
| `/ads/orders/<pk>/foto/` | `FotoInOrderUpdateView` | ⚠️ `order_close` (дубликат) |
| `/ads/orders/reports` | `reports` | `order_reports` |
| `/ads/getaddressfromphone` | `get_address_from_phone` | — |
| `/ads/getordershistory` | `get_orders_history` | — |
| `/ads/getcompanyexec` | `get_company_exec` | — |
| `/ads/print` | `print` | — |
| `/ads/printdisconnect` | `print_disconnect` | — |
| `/ads/disconnects` | `DisconnectListView` | `disconnect_list` |
| `/ads/disconnects/create` | `DisconnectCreateView` | `disconnect_create` |
| `/ads/disconnects/<pk>/update` | `DisconnectUpdateView` | `disconnect_update` |

### 6.3. Проверка `reverse_lazy`

| View | `success_url` | Резолвится? |
|------|---------------|-------------|
| `OrderCreateView` | `reverse_lazy('order_list')` | ✅ |
| `OrderUpdateView` | `reverse_lazy('order_list')` | ✅ |
| `OrderCloseView` | `reverse_lazy('order_list')` | ✅ |
| `FotoInOrderUpdateView` | `reverse_lazy('order_list')` | ✅ |
| `DisconnectCreateView` | `reverse_lazy('disconnect_list')` | ✅ |
| `DisconnectUpdateView` | `reverse_lazy('disconnect_list')` | ✅ |

---

## 7. Формы

⚠️ **TBD** — требуется `ads/forms.py` и `bipro/forms.py`.

Известные формы:

| Форма | Модуль | Назначение |
|-------|--------|------------|
| `OrderForm` | ads/forms.py | Создание/редактирование заявки |
| `OrderCloseForm` | ads/forms.py | Закрытие заявки |
| `FotoInOrderForm` | ads/forms.py | Фото (inline) |
| `FotoInOrderFormSet` | ads/forms.py | Формсет фото |
| `DisconnectForm` | ads/forms.py | Отключение |
| `ExtendedRegisterForm` | bipro/forms.py | Регистрация |

---

## 8. Страницы (Templates)

### 8.1. Готовые шаблоны

| Шаблон | Назначение |
|--------|------------|
| `base.html` | Базовый layout: тёмная шапка, навигация, профиль, footer |
| `order_list.html` | Главная — таблица заявок + фильтры + массовая печать |
| `order_form.html` | Форма заявки + AJAX + история |

### 8.2. TBD-шаблоны

`index2.html`, `login.html`, `lklogin.html`, `signup.html`, `signup_successfully.html`, `order_close_form.html`, `order_foto_form.html`, `disconnect_list.html`, `disconnect_form.html`, `reports.html`

### 8.3. `base.html` — каркас

```
HEAD: jQuery 3.3.1, jQuery UI 1.13.2, Bootstrap 5.3.8, Bootstrap Icons 1.10.2,
      jquery-ui.css (локально), Tom Select 2.6.2

HEADER (bg-dark): Логотип /static/logo_black.png + «БиПро» + слоган
  Навигация (авторизованные): Заявки · Отключения · Отчёты · [Админ]
  Профиль: лого компании → ФИО → должность → компания → (выход)
  Аноним: [Регистрация] | [Войти]

{% block content %}

FOOTER: © 2026 ООО "БиПро"
```

### 8.4. `order_list.html` — список заявок

**Структура:**
- Тулбар: `[+ Добавить заявку]` `[🖨 Распечатать]` `[🗑 Удалить]` `[⚙ Фильтр]` `[✖ Очистить фильтр]` + поиск
- Таблица (10 колонок): ☐ · Номер (dropdown) · Статус · Автор · Дата заявки · ФИО · Адрес · Описание · Дата план · Исполнитель
- Модалка `#settingsModal` — фильтры (state, даты, подрядчик, рабочая система)
- Пагинация (кастомная)
- JS: Tom Select, «выбрать все», `fetch POST /ads/print` → PDF в новой вкладке

**10 колонок таблицы:**

| # | Колонка | Источник |
|---|---------|----------|
| 1 | ☐ | `#select-all` |
| 2 | Номер (dropdown: Изменить/Закрыть/Фото) | `o.number`, `o.id` |
| 3 | Статус | `o.colored_state` |
| 4 | Автор | `o.get_profile_name`, `o.get_profile_company` |
| 5 | Дата заявки | `o.order_date_format` |
| 6 | ФИО | `o.citizen`, `o.phone` |
| 7 | Адрес | `o.address` |
| 8 | Описание | `o.shot_description` |
| 9 | Дата план | `o.plan_date_format`, `o.master` |
| 10 | Исполнитель | `o.get_employees`, `o.company_exec` |

### 8.5. `order_form.html` — форма заявки

**Секции:**
1. **Классификация:** number, order_date, ordertype, priority, state
2. **Заявитель и адрес:** phone (AJAX), citizen, street, house, flat, entrance, floor
3. **Работа и описание:** worksystem (AJAX), company_exec (авто), description
4. **Планирование:** plan_date, plan_period, master, employee
5. **Скрытый блок (collapse):** district, building, sourcetype, summa, master_text, worker_text, plan_text
6. **Модалка «История с адреса»** — AJAX в `#hist-table`

**JS:**
- Tom Select (⚠️ селектор `.tom-select-custom` не применяется)
- AJAX по `#id_phone.focusout` → `/ads/getaddressfromphone`
- AJAX по `#id_worksystem.change` → `/ads/getcompanyexec`
- AJAX по `#hist.click` → `/ads/getordershistory`
- jQuery UI autocomplete для `#id_description`

---

## 9. Пользовательский интерфейс

### 9.1. UI-стек

- **Bootstrap 5.3.8** — сетка, компоненты, утилиты
- **Bootstrap Icons** — иконки
- **jQuery + jQuery UI** — autocomplete, datepicker
- **Tom Select** — множественные `<select>` с поиском
- **Bootstrap Modal** — фильтры и история

### 9.2. UI-паттерны

**Список заявок:**
- Компактная таблица с чекбоксами для массовой печати
- Цветные бейджи состояний + inline-иконки (🖨 📷 ❗ ₽)
- Dropdown с действиями (Изменить / Закрыть / Фото)
- Модалка фильтров
- Пагинация по 100

**Форма заявки:**
- Многосекционная сетка Bootstrap
- Скрытый блок «дополнительные поля» (collapse)
- AJAX-автозаполнение по телефону (адрес + ФИО)
- AJAX-подбор подрядчика + стандартных описаний по рабочей системе
- Модалка «История с адреса»
- jQuery UI autocomplete для описания

**Печать:**
- Кнопка «Распечатать» → `fetch POST /ads/print` → blob PDF в новой вкладке

### 9.3. Индикаторы в списках

Из `Order.colored_state`:
- Цветной бейдж `OrderState.color` + `OrderState.name`
- 🖨 `printer.png` — заявка печаталась
- ❗ — приоритет `urgent`/`emergency`
- `site.png` — источник «сайт»
- `telegram2.png` — источник «Max/Telegram»
- `foto.png` — есть фото
- ₽ — тип «Платная»
- Красный цвет + «Просрочена» — если `plan_date < сегодня` и состояние `accepted`/`inprogress`

### 9.4. Медиа и статика

- `media/fotos/` — фото заявок
- `media/buildings/` — фото домов
- `media/company/` — логотипы компаний
- `static/*.png` — иконки-индикаторы
- `static/logo_black.png` — логотип
- `static/blue-circle.svg` — fallback лого компании

---

## 10. Аутентификация и роли

### 10.1. Поток регистрации и входа

```
[Гость]
   ├─→ /index          → index2.html
   ├─→ /signup         → signup.html ──POST──→ User(is_active=False)
   │                                        └─→ signup_successfully.html
   └─→ /login          → login.html ──POST──→ authenticate()
                          │                      ├─ is_active=False → lklogin.html
                          │                      ├─ неверный пароль → login.html
                          │                      └─ успех → order_list
[Админ] ─→ /admin ─→ User.is_active = True
```

### 10.2. Роли (`Employee.POSTS`)

| Код | Название | Права |
|-----|----------|-------|
| `boss` | Генеральный | полный доступ |
| `secretary` | Секретарь | полный доступ |
| `chief` | Начальник участка | полный доступ |
| `itr` | ИТР | полный доступ |
| `admin` | Административный | полный доступ |
| `disp` | Диспетчер участка | полный доступ |
| `master` | Мастер участка | заявки по своим системам + где он мастер |
| `worker` | Рабочий участка | заявки, где он исполнитель |

### 10.3. Типы компаний

| Код | Название | Что видит |
|-----|----------|-----------|
| `ук` | Управляющая компания | заявки, где `company_owner` = его компания |
| `подряд` | Подрядчик | заявки, где `company_exec` = его компания |

### 10.4. Активация пользователей

- Новые пользователи через `/signup` создаются с `is_active=False`
- Вход возможен только после активации администратором через `/admin`
- В `login()` есть явная проверка `is_active` до `authenticate`

---

## 11. Админка

⚠️ **TBD** — требуются `ads/admin.py` и `dict/admin.py`.

Известно:
- `admin.site.site_header = settings.ADMIN_SITE_HEADER` → «Администрирование БиПро»
- Модели используют `format_html`, `short_description`, `admin_order_field` (закомментирован) — заточены под кастомную админку
- Ожидается настройка `list_display`, `list_filter`, `search_fields`, `readonly_fields`, `inlines` (для `FotosInOrder`)

---

## 12. Отчёты и печать

⚠️ **TBD** — требуется `ads/reports/*.py`.

| Модуль | Функция | Назначение |
|--------|---------|------------|
| `ads/reports/jobs.py` | `jobs_report` | PDF по заявкам (полный) |
| `ads/reports/jobs_short.py` | `jobs_report` | PDF по заявкам (сокращённый) |
| `ads/reports/disconnect_list.py` | `generate_disconnects` | PDF по отключениям |
| `ads/reports/order_list.py` | `order_list2` | PDF-отчёт по фильтру |

Все возвращают буфер, который отдаётся через `StreamingHttpResponse` с `content_type="application/pdf"`.

**Библиотека генерации PDF:** ⚠️ TBD (ReportLab? WeasyPrint? xhtml2pdf?)

---

## 13. Импорт данных

⚠️ **TBD** — требуется `import.py`.

Ожидаемая структура описания:

| Пункт | Что указать |
|-------|-------------|
| Источник данных | CSV / Excel / API / внешняя БД |
| Что импортирует | справочники / заявки / отключения |
| Формат запуска | `python manage.py shell < import.py` или management command |
| Зависимости | pandas, openpyxl, requests, psycopg2 |
| Идемпотентность | Есть ли upsert по `orderid` |

Примечание: модель `Order` содержит `orderid` (внешний ID) — вероятно, ключ сопоставления при импорте.

---

## 14. Внешние интеграции

| Сервис | Назначение | Где вызывается |
|--------|-----------|----------------|
| **Max** (`platform-api.max.ru`) | Рассылка уведомлений об отключениях в каналы домов | `DisconnectCreateView.form_valid` |
| Telegram | Поля `Employee.telegram`, `Building.channelid` — задел | ⚠️ TBD |
| 1С | `Street.c1_name` — сопоставление улиц | ⚠️ TBD (через `import.py`?) |

**Токен Max:** зашит в коде (`TOKEN = "f9LHodD0cOJ..."`) — ⚠️ критично, вынести в `.env`.

---

## 15. Настройки проекта

### 15.1. Основные параметры (`bipro/settings.py`)

| Параметр | Значение | Комментарий |
|----------|----------|-------------|
| Django | 5.1.3 | |
| `SECRET_KEY` | `'django-insecure-3c*yv%px!...'` | ⚠️ **в репозитории** |
| `DEBUG` | `True` | ⚠️ для прода — `False` |
| `ALLOWED_HOSTS` | `[]` | ⚠️ заполнить в проде |
| `ROOT_URLCONF` | `bipro.urls` | |
| `DEFAULT_AUTO_FIELD` | `BigAutoField` | |
| `ADMIN_SITE_HEADER` | `'Администрирование БиПро'` | |

### 15.2. Приложения

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dict',
    'ads',
]
```

### 15.3. База данных

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bipro',
        'USER': 'root',
        'PASSWORD': 'mymyvveR01',    # ⚠️ в репозитории
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

### 15.4. Локализация

| Параметр | Значение |
|----------|----------|
| `LANGUAGE_CODE` | `ru` |
| `TIME_ZONE` | `Europe/Moscow` |
| `USE_I18N` | `True` |
| `USE_TZ` | `True` |

### 15.5. Статика и медиа

```python
STATIC_URL = 'static/'                       # ⚠️ без ведущего слэша
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'
```

### 15.6. Шаблоны

```python
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]
```

### 15.7. Что НЕ настроено (но нужно)

| Параметр | Зачем |
|----------|-------|
| `LOGIN_URL` | Редирект неавторизованных |
| `LOGIN_REDIRECT_URL` | Куда после входа |
| `LOGOUT_REDIRECT_URL` | Куда после выхода |
| `CSRF_TRUSTED_ORIGINS` | Для HTTPS |
| `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` | Безопасность |
| `EMAIL_*` | Уведомления |
| `LOGGING` | Логи |
| `CACHES` | Redis/Memcached |

---

## 16. Установка и запуск

### 16.1. Системные зависимости (Ubuntu/Debian)

```bash
sudo apt install python3-dev default-libmysqlclient-dev build-essential pkg-config
```

### 16.2. Клонирование и виртуальное окружение

```bash
git clone https://github.com/stanovskih/bipro.git
cd bipro

python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
```

### 16.3. Зависимости

```bash
pip install django==5.1.3 mysqlclient
# + остальные из requirements.txt
```

### 16.4. Создание БД MySQL

```bash
mysql -u root -p
> CREATE DATABASE bipro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
> exit;
```

### 16.5. Миграции и суперпользователь

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 16.6. Запуск

```bash
python manage.py runserver
```

- Админка: http://127.0.0.1:8000/admin/
- Список заявок: http://127.0.0.1:8000/ads/orders

### 16.7. Продакшен

```bash
python manage.py collectstatic
# + настроить Nginx/Apache для статики и медиа
# + gunicorn/uwsgi как WSGI-сервер
```

---

## 17. Критичные проблемы безопасности

| # | Проблема | Риск | Действие |
|---|----------|------|----------|
| 1 | `SECRET_KEY` в репозитории | Компрометация сессий, CSRF, cookies | Сменить + вынести в `.env` |
| 2 | Пароль MySQL `mymyvveR01` в репозитории | Прямой доступ к БД | Сменить + создать `bipro_user` с ограниченными правами |
| 3 | Токен бота Max в `views.py` | Утечка, спам от лица бота | Вынести в `.env`, перегенерировать |
| 4 | `DEBUG=True` | Stack trace, SQL, настройки | `False` в проде |
| 5 | `ALLOWED_HOSTS=[]` | Сломается в проде | Заполнить доменами |
| 6 | `root` для приложения | Широкие права | `GRANT SELECT,INSERT,UPDATE,DELETE` отдельному пользователю |
| 7 | Нет `LoginRequiredMixin` в `OrderUpdateView`, `OrderCloseView`, `FotoInOrderUpdateView`, `DisconnectCreateView`, `DisconnectUpdateView`, `reports`, `print`, `print_disconnect`, AJAX | Аноним дёргает эндпоинты | Добавить миксин/декоратор |
| 8 | Выход через GET | CSRF-разлогин | POST + `{% csrf_token %}` |
| 9 | `STATIC_URL = 'static/'` без ведущего слэша | Поломка на вложенных URL | `/static/` |
| 10 | Медиа через `static()` в `urls.py` | В проде не работает | Nginx |

### 17.1. Шаблон `.env`

```bash
DJANGO_SECRET_KEY=новый-сгенерированный-ключ
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=bipro.example.com,www.bipro.example.com
DB_NAME=bipro
DB_USER=bipro_user
DB_PASSWORD=надёжный-пароль
DB_HOST=127.0.0.1
DB_PORT=3306
MAX_BOT_TOKEN=токен-бота-max
```

### 17.2. Подключение через `python-decouple`

```python
# settings.py
from decouple import config, Csv

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', cast=Csv())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

### 17.3. Если секреты уже попали в публичный репозиторий

1. Сменить `SECRET_KEY` → все сессии инвалидируются.
2. Сменить пароль MySQL.
3. Сменить токен бота Max.
4. Очистить историю git:
   ```bash
   git filter-repo --path bipro/settings.py --invert-paths
   # или BFG Repo-Cleaner
   git push --force
   ```
5. Обратиться в GitHub Support для удаления закэшированных версий.
6. Включить Secret Scanning / gitleaks / trufflehog в CI.

---

## 18. Известные баги

### 18.1. `models.py`

| Место | Проблема | Влияние |
|-------|----------|---------|
| `OrderState` | Поле `сompleted` — кириллическая `с` | Поиск/миграции могут не работать |
| `Order.colored_state` | Используется `datetime.today()`, но **нет импорта `datetime`** | **NameError** при отображении |
| `Order.get_profile_company` | `short_description = 'Адрес'` (должно быть «Компания») | Неверный заголовок |
| `FotosInOrder.preview_image` | `short_description` навешан на `admin_image` | Дубль заголовка |
| Первая строка | `from cProfile import Profile` — артефакт профилирования | Мусор |
| Модель `Debt` закомментирована, но `get_address_from_phone` возвращает `debt` | Мёртвый код / несоответствие | — |

### 18.2. `views.py`

| Место | Проблема | Влияние |
|-------|----------|---------|
| `DisconnectListView.get_queryset` | Лишний пробел в `'disconnect_fact_date_to '` | Фильтр не работает |
| `get_address_from_phone` | Мёртвый `return HttpResponse(...)` перед `JsonResponse` | Мусор |
| `get_company_exec` | `HttpResponse(json.dumps(...))` вместо `JsonResponse` | Непоследовательность |
| `OrderListView` | TODO: фильтрация по должности не завершена | — |
| `OrderCreateView` | TODO: parent_id не учитывается | — |
| Везде | `Employee.objects.get(user=...)` без `try/except` | Падение, если нет профиля |
| `views.py` | Много неиспользуемых импортов | Мусор |

### 18.3. `urls.py`

| Файл | Проблема | Влияние |
|------|----------|---------|
| `bipro/urls.py` | `logout` с `name='login'` | `reverse('login')` вернёт logout |
| `ads/urls.py` | `foto/` с `name='order_close'` | `reverse('order_close')` вернёт не то |
| `ads/urls.py` | Большинство URL без trailing slash | Риск потери POST |
| `bipro/urls.py` | `path('index', ...)` без `/` | `/index/` не сработает |

### 18.4. Шаблоны

| Файл | Проблема |
|------|----------|
| `order_form.html` | `<h3>...</h2>` — несовпадение тегов |
| `order_form.html` | `.tom-select-custom` — класса нет ни на одном поле → Tom Select не применяется |
| `order_form.html` | Хардкод AJAX URL вместо `{% url %}` |
| `order_list.html` | Пагинация не сохраняет GET-фильтры |
| `order_list.html` | Поля `plan_date_at` / `plan_date_to` не обрабатываются во view |
| `order_list.html` | Кнопка «Удалить» без обработчика |
| `order_list.html` | `<th style="...; !important">` — не работает |
| Оба | Хардкод `/ads/...` вместо `{% url %}` |
| `base.html` | CDN без SRI (кроме Bootstrap), устаревший jQuery 3.3.1 |
| `base.html` | `opacity-100-hover`, `fs-9`, `tracking-wide` — нестандартные классы |
| `base.html` | `/media/{{ company.logo }}` вместо `{{ company.logo.url }}` |

---

## 19. Рекомендации

### 🔴 Критично (безопасность)
1. Сменить `SECRET_KEY`, пароль MySQL, токен Max — **все три уже в публичном git**
2. Вынести секреты в `.env` (`python-decouple`)
3. `DEBUG=False` для прода, заполнить `ALLOWED_HOSTS`
4. Добавить `LoginRequiredMixin` / `@login_required` на все защищённые views и AJAX
5. Выход — через POST с CSRF

### 🟠 Важно (баги)
6. Исправить `name='login'` для logout и `name='order_close'` для foto
7. Добавить `from datetime import datetime` в `ads/models.py`
8. Привести URL к trailing slash
9. Починить пагинацию — сохранять GET-параметры
10. Реализовать фильтры `plan_date_at/to` в `OrderListView`

### 🟡 Желательно (качество)
11. Убрать неиспользуемые импорты
12. Исправить `.tom-select-custom` (класс или селектор)
13. Заменить хардкод URL на `{% url %}`
14. Убрать мёртвый код (`.field-dolg`, закомментированные модели, `console.log`)
15. Заменить магические строки на `TextChoices`
16. Вынести дублирующийся `get_form` в миксин
17. `Employee.objects.get(user=...)` → `get_object_or_404` или try/except
18. Обновить jQuery (3.3.1 → 3.7.x), добавить SRI-хэши

---

## 20. Приложения

### 20.1. Список моделей (сводка)

| Модель | Приложение | Verbose name |
|--------|-----------|--------------|
| `Location` | dict | Локация |
| `Company` | dict | Компания |
| `District` | dict | Участок |
| `Street` | dict | Улица |
| `StreetInCompany` | dict | Обслуживаемые улицы |
| `WorkSystem` | dict | Рабочая система |
| `Building` | dict | Объект |
| `Employee` | dict | Сотрудник |
| `StandardDescription` | dict | Стандартное описание |
| `OrderState` | ads | Состояние заявки |
| `Order` | ads | Заявка |
| `FotosInOrder` | ads | Фото в заявке |
| `Numbering` | ads | Нумерация |
| `DistrictInBuilding` | ads | Закрепление участков |
| `WorkSystemInBuilding` | ads | Закрепление подрядчика |
| `Disconnect` | ads | Отключение |

### 20.2. Список views (сводка)

| # | View | Тип | Шаблон |
|---|------|-----|--------|
| 1 | `index` | function | index2.html |
| 2 | `login` | function | login.html / lklogin.html |
| 3 | `logout` | function | — |
| 4 | `signup` | function | signup.html |
| 5 | `signup_successfully` | function | signup_successfully.html |
| 6 | `OrderListView` | ListView | order_list.html |
| 7 | `OrderCreateView` | CreateView | order_form.html |
| 8 | `OrderUpdateView` | UpdateView | order_form.html |
| 9 | `OrderCloseView` | UpdateView | order_close_form.html |
| 10 | `FotoInOrderUpdateView` | UpdateView | order_foto_form.html |
| 11 | `DisconnectListView` | ListView | disconnect_list.html |
| 12 | `DisconnectCreateView` | CreateView | disconnect_form.html |
| 13 | `DisconnectUpdateView` | UpdateView | disconnect_form.html |
| 14 | `reports` | function | reports.html / PDF |
| 15 | `get_address_from_phone` | function | JSON |
| 16 | `get_company_exec` | function | JSON |
| 17 | `get_orders_history` | function | HTML |
| 18 | `print` | function | PDF |
| 19 | `print_disconnect` | function | PDF |

### 20.3. Глоссарий

| Термин | Значение |
|--------|----------|
| **Заявка** | Обращение жителя или УК по адресу |
| **Отключение** | Плановое/аварийное отключение ресурса |
| **Объект** | Дом (`Building`) |
| **Участок** | Территориальная единица (`District`) |
| **Рабочая система** | Инженерная система (ХВС, ГВС, отопление) |
| **Рабочая система в объекте** | Закрепление подрядчика (`WorkSystemInBuilding`) |
| **Нумерация** | Правило генерации номеров заявок (`Numbering`) |
| **Стандартное описание** | Шаблон текста (`StandardDescription`) |
| **УК** | Управляющая компания |
| **Подрядчик** | Исполнитель работ |

### 20.4. Что осталось (TBD)

| # | Файл | Раздел |
|---|------|--------|
| 1 | `ads/forms.py` | Формы |
| 2 | `bipro/forms.py` | `ExtendedRegisterForm` |
| 3 | `ads/admin.py`, `dict/admin.py` | Админка |
| 4 | `ads/reports/*.py` | Отчёты |
| 5 | `import.py` | Импорт |
| 6 | `requirements.txt` | Зависимости |
| 7 | Остальные шаблоны | UI |

---

## Конвертация в PDF

**Pandoc (универсальный способ):**

```bash
pandoc DOCUMENTATION.md -o DOCUMENTATION.pdf \
  --pdf-engine=xelatex \
  -V mainfont="DejaVu Sans" \
  -V geometry:margin=2cm \
  --toc --toc-depth=3
```

**VS Code:** расширение «Markdown PDF» → `Ctrl+Shift+P` → `Markdown PDF: Export (pdf)`.

**GitHub:** залейте `.md` в репозиторий, откройте, `Ctrl+P` → «Сохранить как PDF».

**Typora / Obsidian:** Файл → Экспорт → PDF.

---

## История изменений

| Дата | Версия | Изменения |
|------|--------|-----------|
| 2026-09-30 | 1.0 | Первая полная версия документации |

---

*Документ подготовлен на основе файлов `ads/models.py`, `dict/models.py`, `ads/views.py`, `bipro/views.py`, `bipro/urls.py`, `ads/urls.py`, `bipro/settings.py`, `templates/base.html`, `templates/order_list.html`, `templates/order_form.html`. Разделы, помеченные ⚠️ TBD, требуют дополнительных исходников.*