#!/usr/bin/env bash

# Деплой бота на сервере
# Протестировано на Debian 10 && Ubuntu 18.04.

# Обновляем систему:

sudo apt update && sudo apt upgrade -y

os=$(cat /etc/os-release | grep "^ID=" | awk -F "=" '{printf $2}')

if [[ $os == "ubuntu" ]]; then
	sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev \
		libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev tk-dev libc6-dev checkinstall
fi

# Устанавливаем Python 3.11.1 сборкой из исходников и sqlite3:

cd ~
sudo apt install -y sqlite3 pkg-config
wget https://www.python.org/ftp/python/3.11.1/Python-3.11.1.tgz
tar -xzvf Python-3.11.1.tgz
cd Python-3.11.1
./configure --enable-optimizations --prefix=$HOME/.python3.11
sudo make -j $(nproc)
sudo make altinstall

echo "export PATH=$HOME/.python3.11/bin:\$PATH" >> ~/.bashrc
source ~/.bashrc

# Устанавливаем Poetry:

curl -sSL https://install.python-poetry.org | python3.11 -

echo "export PATH=$HOME/.local/bin:\$PATH" >> ~/.bashrc
source ~/.bashrc

# Создаём переменные окружения:

cd ~/code/botanim-bot/botanim_bot

# TELEGRAM_BOT_TOKEN — токен бота, полученный в BotFather
printf "Введите токен telegram бота\a "
read TELEGRAM_BOT_TOKEN

# TELEGRAM_BOTANIM_CHANNEL_ID — идентификатор группы книжного клуба, участие в котором будет проверять бот в процессе голосования
printf "Введите id telegram канала\a "
read TELEGRAM_BOTANIM_CHANNEL_ID

echo "TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN" > .env
echo "TELEGRAM_BOTANIM_CHANNEL_ID=$TELEGRAM_BOTANIM_CHANNEL_ID" >> .env

# Заполняем БД начальными данными:

sqlite3 db.sqlite3 < db.sql

# Устанавливаем зависимости Poetry:

cd ~/code/botanim-bot
poetry install

# Настроим systemd-юнит для автоматического запуска бота:

sudo tee /etc/systemd/system/botanimbot.service << END
[Unit]
Description=Botanim Telegram bot
After=network.target

[Service]
User=$(id --user --name)
Group=$(id --group --name)
WorkingDirectory=$HOME/code/botanim-bot
Restart=on-failure
RestartSec=2s
ExecStart=$(poetry env info --path)/bin/python -m botanim_bot

[Install]
WantedBy=multi-user.target
END

# Перезагружаем демона и запускаем наш systemd-юнит:

sudo systemctl daemon-reload
sudo systemctl enable botanimbot.service
sudo systemctl start botanimbot.service

printf "\a"
