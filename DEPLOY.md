## Деплой бота на сервере

Протестировано на Debian 10.

[Вручную](#вручную) | [Скрипт](#с-помощью-скрипта) | [Docker](#в-docker-контейнере)

---

### Вручную:

Обновляем систему:

```bash
sudo apt update && sudo apt upgrade
```

Устанавливаем Python 3.11.1 сборкой из исходников и sqlite3:

```bash
cd
sudo apt install -y sqlite3 pkg-config
wget https://www.python.org/ftp/python/3.11.1/Python-3.11.1.tgz
tar -xzvf Python-3.11.1.tgz
cd Python-3.11.1
./configure --enable-optimizations --prefix=/home/www/.python3.11
sudo make altinstall
```

Устанавливаем Poetry:

```basj
curl -sSL https://install.python-poetry.org | python3 -
```

Клонируем репозиторий в `~/code/botanim_bot`:

```bash
mkdir -p ~/code/
cd ~/code
git clone https://github.com/alexey-goloburdin/botanim-bot.git
cd botanim-bot
```

Создаём переменные окружения:

```
cp botanim_bot/.env.example botanim_bot/.env
vim botanim_bot/.env
```

`TELEGRAM_BOT_TOKEN` — токен бота, полученный в BotFather, `TELEGRAM_BOTANIM_CHANNEL_ID` — идентификатор группы книжного клуба, участие в котором будет проверять бот в процессе голосования.

Заполняем БД начальными данными:

```bash
cat botanim_bot/db.sql | sqlite3 botanim_bot/db.sqlite3
```

Устанавливаем зависимости Poetry и запускаем бота вручную:

```bash
poetry install
poetry run python -m botanim_bot
```

Можно проверить работу бота. Для остановки, жмём `CTRL`+`C`.

Получим текущий адрес до Python-интерпретатора в poetry виртуальном окружении Poetry:

```bash
poetry shell
which python
```

Скопируем путь до интерпретатора Python в виртуальном окружении.

Настроим systemd-юнит для автоматического запуска бота, подставив скопированный путь в ExecStart, а также убедившись,
что директория до проекта (в данном случае `/home/www/code/botanim_bot`) у вас такая же:

```
sudo tee /etc/systemd/system/botanimbot.service << END
[Unit]
Description=Botanim Telegram bot
After=network.target

[Service]
User=www
Group=www-data
WorkingDirectory=/home/www/code/botanim-bot
Restart=on-failure
RestartSec=2s
ExecStart=/home/www/.cache/pypoetry/virtualenvs/botanim-bot-dRxws4wE-py3.11/bin/python -m botanim_bot

[Install]
WantedBy=multi-user.target
END

sudo systemctl daemon-reload
sudo systemctl enable botanimbot.service
sudo systemctl start botanimbot.service
```

---

### С помощью скрипта:

Клонируем репозиторий и запускаем скрипт:

```bash
git clone https://github.com/alexey-goloburdin/botanim-bot.git ~/code/botanim-bot
. ~/code/botanim-bot/deploy.sh

```

---

### В Docker контейнере:

Для начала установим docker на хост-машину по [инструкции](https://docs.docker.com/engine/install/).

Проверяем что все установилось корректно командой:

```bash
docker --version

```

Клонируем репозиторий:

```bash
git clone https://github.com/alexey-goloburdin/botanim-bot.git ~/code/botanim-bot

```

Добавляем переменные окружения:

```bash
cp -n ~/code/botanim-bot/botanim_bot/.env.example ~/code/botanim-bot/botanim_bot/.env
vim ~/code/botanim-bot/botanim_bot/.env

```

> `TELEGRAM_BOT_TOKEN` — токен бота, полученный в BotFather,
> `TELEGRAM_BOTANIM_CHANNEL_ID` — идентификатор группы книжного клуба, участие в котором будет проверять бот в процессе голосования.

Создаем базу локально, для того чтобы она сохранялась после пересоздания контейнера:

```bash
sudo apt update && sudo apt install -y sqlite3
sqlite3 ~/code/botanim-bot/botanim_bot/db.sqlite3 < ~/code/botanim-bot/botanim_bot/db.sql

```

Собираем образ и запускаем в detach моде прокидывая локальную базу:

```bash
docker build --tag botanim_bot .
docker run --detach \
	--name botanim-bot \
	--mount type=bind,source=$HOME/code/botanim-bot/botanim_bot/db.sqlite3,target=/app/botanim_bot/db.sqlite3 \
	botanim_bot

```
