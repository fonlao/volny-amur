# Вольный Амур

Одностраничный сайт туристической компании по Хабаровскому краю. Frontend — Vue 3 + Vite, backend — Django + SQLite. Контент и заявки управляются через Django Admin.

## Структура

- `src/`, `public/`, `index.html`, `vite.config.js` — Vue frontend.
- `amur_site/`, `content/`, `manage.py` — Django backend и API.
- `deploy/` — конфигурации Nginx и systemd.
- `.env.example` — пример переменных окружения без секретов.

## Запуск

```powershell
.\.venv\Scripts\Activate.ps1
npm run build
python manage.py runserver 127.0.0.1:8000
```

Сайт: http://127.0.0.1:8000  
Админка: http://127.0.0.1:8000/admin/

Production-конфигурации Nginx и systemd находятся в каталоге `deploy/`.

Уведомления о заявках отправляются через SMTP, если в production-окружении заданы `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` и `LEAD_NOTIFICATION_EMAIL`.
