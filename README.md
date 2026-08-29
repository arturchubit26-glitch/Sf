# Music Remix Telegram Bot

Это минимальный Telegram-бот для ремиксов с FFmpeg. Пользователь отправляет аудио, выбирает стиль и получает обработанный MP3. Доступны пресеты: House, Techno, Jungle, Hip-Hop, Lo-Fi и Pop-Rock.

## Публикация на Render

1. Создайте аккаунт на [render.com](https://render.com) и войдите через GitHub.
2. Создайте новый публичный GitHub-репозиторий, например `music-remix-bot`, и загрузите в него все файлы этого проекта.
3. В Render выберите **New → Web Service**, подключите репозиторий и выберите Docker runtime.
4. Выберите бесплатный план для тестирования.
5. В разделе Environment добавьте `BOT_TOKEN` со значением токена от @BotFather.
6. После первого деплоя скопируйте URL сервиса вида `https://music-remix-bot-xxxx.onrender.com` и добавьте переменную `PUBLIC_URL` с этим URL без завершающего `/`.
7. Нажмите **Manual Deploy → Deploy latest commit**. В логах должна появиться успешная установка webhook.
8. Откройте бота в Telegram и отправьте `/start`.

Токен не нужно добавлять в GitHub, README или Dockerfile. Render хранит его в переменных окружения.

## Ограничения бесплатного Render

Free Web Service может засыпать после простоя, а локальные файлы не сохраняются между перезапусками. Поэтому это вариант для теста и небольших задач. Render указывает, что Free-сервисы не предназначены для production. Для постоянной обработки длинных треков потребуется платный постоянно работающий сервис или VPS.

## Локальный запуск

```bash
export BOT_TOKEN='ваш_токен'
export PUBLIC_URL='https://ваш-домен'
docker build -t music-remix-bot .
docker run --rm -p 10000:10000 -e BOT_TOKEN -e PUBLIC_URL music-remix-bot
```
