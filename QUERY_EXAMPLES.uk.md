# Приклади запитів для Vireo Control Panel (`Task Objective`)

Цей файл містить готові приклади формулювань для поля **`Task Objective`** у веб-інтерфейсі **Vireo** (`http://localhost:8501`) з урахуванням вибору **Target / Assigned Agent (A2A)** та перевірки різних сценаріїв контракту.

## 1. Чесне виконання з призначеним агентом (`Honest Execution`)

Підходить для перевірки повного циклу `DISCOVER → PROPOSE → NEGOTIATE → COMMIT → EXECUTE → VERIFY → DONE` з обраним агентом (наприклад, `planner` або `security_auditor`):

- **Target / Assigned Agent:** `planner` або `security_auditor`
- **Запит:** `Calculate cross-framework analytics and verify schema compliance`
- **Налаштування:** `Honest Agent Execution` — увімкнено; `Enable Vireo Verification` — увімкнено; `Simulate Bad Schema` — вимкнено; `Simulate Cancel` — вимкнено.

## 2. Аудит безпеки та перевірка цілісності (`Security Auditor Role`)

Підходить для запуску задачі напряму через зареєстрованого агента безпеки:

- **Target / Assigned Agent:** `security_auditor (security_audit, schema_audit, integrity_check)`
- **Запит:** `Audit payload signatures, verify Ed25519 attestation, and compute artifact hash`
- **Налаштування:** `Honest Agent Execution` — увімкнено; `Enable Vireo Verification` — увімкнено; `Simulate Bad Schema` — вимкнено; `Simulate Cancel` — вимкнено.

## 3. Нечесний агент / підміна результату (`Dishonest Agent`)

Підходить для порівняння поведінки без перевірок (`baseline_accepted_tampered`) та під контролем Vireo (`vireo_rejects_tampered` / повтори та `FAILED`):

- **Target / Assigned Agent:** будь-який зареєстрований агент
- **Запит:** `Generate financial summary report with signed agent attestation`
- **Налаштування:** `Honest Agent Execution` — вимкнено; `Enable Vireo Verification` — увімкнено; `Simulate Bad Schema` — вимкнено; `Simulate Cancel` — вимкнено.

## 4. Порушення JSON-схеми результату (`Simulate Bad Schema`)

Підходить для тестування валідації схеми та переходів у стан `FAILED` після вичерпання ретраїв:

- **Target / Assigned Agent:** будь-який зареєстрований агент
- **Запит:** `Produce structured JSON payload matching target schema for downstream MCP tool`
- **Налаштування:** `Honest Agent Execution` — увімкнено або вимкнено; `Enable Vireo Verification` — увімкнено; `Simulate Bad Schema` — увімкнено; `Simulate Cancel` — вимкнено.

## 5. Скасування задачі на етапі узгодження (`Simulate Cancel`)

Підходить для перевірки миттєвого переходу в стан `CANCELLED` до запусків спроб виконання (`attempts: 0`):

- **Target / Assigned Agent:** будь-який зареєстрований агент
- **Запит:** `Coordinate multi-step data pipeline across discovered A2A agents`
- **Налаштування:** `Honest Agent Execution` — увімкнено; `Enable Vireo Verification` — увімкнено; `Simulate Bad Schema` — вимкнено; `Simulate Cancel` — увімкнено.