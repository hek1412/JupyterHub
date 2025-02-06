##  JupyterHub + PostgreSQL с помощью Docker Compose

### 1 ) Собираем docker образ контейнера jupyterhub на основе нашей конфигураций

`docker-compose.yaml`

```
services:
  jupyterhubtest:
    build:
      context: .
      dockerfile: Dockerfile.jupyterhub
    restart: always
    image: jupyterhub
    container_name: jupyterhubtest
    networks:
      - jupyterhubtest
    volumes:
      - "./jupyterhub_config.py:/srv/jupyterhub/jupyterhub_config.py"
      - "/var/run/docker.sock:/var/run/docker.sock:rw"
      - "jupyterhub-data:/srv/jupyterhub/data"
    ports:
      - "35003:8000"
    environment:
      - JUPYTERHUB_BASE_URL=/hub
      - JUPYTERHUB_URL=http://skayfaks.keenetic.pro:35003

volumes:
  jupyterhub-data:

networks:
  jupyterhubtest:
    name: jupyterhubtest
```

`Dockerfile.jupyterhub`

```
FROM jupyterhub/jupyterhub:latest
WORKDIR /srv/jupyterhub

RUN mkdir -p /srv/jupyterhub/data && \
    chown -R 1000:100 /srv/jupyterhub 
RUN python3 -m pip install --no-cache-dir \
    psycopg2-binary \    
    dockerspawner \
    jupyterhub-nativeauthenticator

COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
```
`jupyterhub_config.py`

```
from dockerspawner import DockerSpawner
import os, nativeauthenticator
c = get_config()

# Основные настройки JupyterHub

c.JupyterHub.bind_url = 'http://:8000'
c.JupyterHub.hub_bind_url = 'http://0.0.0.0:8081'
c.JupyterHub.authenticator_class = "nativeauthenticator.NativeAuthenticator" # Назначаем класс аутентификации
c.NativeAuthenticator.check_common_password = True # Включает проверку на наличие распространенных паролей
c.NativeAuthenticator.allowed_users = {'admin'} # Устанавливает, что только указанный пользователь может использовать систему
c.NativeAuthenticator.admin_users = {'admin'} # Задает администратора JupyterHub.
c.NativeAuthenticator.allowed_failed_logins = 3 # Определяет число неудачных попыток входа, после которых пользователь будет временно заблокирован
c.NativeAuthenticator.seconds_before_next_try = 1200 # Устанавливает время блокировки в секундах после превышения попыток входа (20 минут).
c.Authenticator.open_signup = True # позволяют пользователям регистрироваться самостоятельно 
c.Authenticator.allow_all = True # всем зарегистрированным пользователям позволяет входить в систему

# Настраиваем Spawner для использования Docker
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.DockerSpawner.image = "jupyter/scipy-notebook" # Указывает образ Docker, который будет использоваться для запуска каждого пользователя
c.Spawner.http_timeout = 180 # указывает максимальное время (в секундах), в течение которого JupyterHub будет ожидать, что спаунер (Spawner) запустит сервер пользователя
c.JupyterHub.start_timeout = 360 # параметр задает максимальное время (в секундах), в течение которого JupyterHub ожидает, что будет произведён успешный запуск контролируемого процесса
c.JupyterHub.shutdown_no_activity_timeout = 600 #  Таймаут для автоматического завершения работы контейнеров при отсутствии активности (10 минут)
c.JupyterHub.shutdown_on_logout = True # автоматически останавливает сервер пользователя, как только он выходит из системы
c.DockerSpawner.use_internal_ip = True # параметр управляет использованием внутренних IP-адресов Docker
c.DockerSpawner.network_name = "jupyterhubtest" # Имя сети Docker, которое будет использоваться
c.Spawner.start_timeout = 240
c.DockerSpawner.debug = True # Включает отладку для более детальной диагностики, если что-то пойдет не так
data_dir = '/srv/jupyterhub/data'
c.JupyterHub.cookie_secret_file = os.path.join(data_dir, 'jupyterhub_cookie_secret') # определяем директорию для секретов
c.JupyterHub.db_url = "sqlite:////srv/jupyterhub/data/jupyterhub.sqlite" # Указывает использовать SQLite для хранения данных JupyterHub
c.JupyterHub.log_level = 'DEBUG' # Устанавливает уровень логирования на DEBUG
```
### 2) Создаем все файлы в одной директории и запускаем команду в терминале

`docker-compose build`

![image](https://github.com/user-attachments/assets/bdaae205-3269-481f-80c2-a86bac91fd6a)

Запускаем его, смотрим что сервис запустился 
```
docker-compose up -d
docker logs jupyterhubtest
```
![image](https://github.com/user-attachments/assets/96f2bcde-9ba8-430a-8dee-07f5258d861d)

Переходим по адресу `http://skayfaks.keenetic.pro:35003/`

![image](https://github.com/user-attachments/assets/179e8ca1-baa4-446d-a3c3-b2992f4f2b0c)

Необходимо зарегистрировать админа. Вводим логин из конфигурационного файла и задаем пароль

![image](https://github.com/user-attachments/assets/96ac4627-91dd-47a4-912f-a2ef8d191116)

Отлично создали админа, логинимся

![image](https://github.com/user-attachments/assets/b43e9f00-8999-4ee0-b244-50b4831305ef)

Нажимаем вход, наблюдаем как загружается сервер админа в JupyterHub

![image](https://github.com/user-attachments/assets/f18e2136-e4b1-49f3-a2a2-bc1b99cab34c)

Ура, первая часть готова

![image](https://github.com/user-attachments/assets/dea0d053-037f-4e82-b799-3f5acc44edaf)

### 3) Далее переходим в панель управления администратора

![image](https://github.com/user-attachments/assets/36812edc-01da-4979-8d72-4241cb90e934)

Нажимаем иконку добавить пользователя

![image](https://github.com/user-attachments/assets/7959c5a6-d5dd-4790-bb40-d65fbf7e21d9)

Вводим первого user777, нажимаем на иконку добавить

![image](https://github.com/user-attachments/assets/95a6feff-598c-49d5-a6ee-78f09e5b42b0)

Новый пользователь создан

![image](https://github.com/user-attachments/assets/7f5e650a-dce8-4b81-bca0-76ffc32c2667)

Теперь выходим из под админа и регистрируемся под `user777`, нажимаем создать пользователя

![image](https://github.com/user-attachments/assets/3b9c5a3b-980a-4c4e-a802-802a44f9da89)

Если выдало окно, что регистрация прошла успешно, входим под новым пользователем

![image](https://github.com/user-attachments/assets/fef8343f-ba2a-49e0-8fc2-db811c970231)

Наблюдаем за созданием образа для ноутбука

![image](https://github.com/user-attachments/assets/76d07b3c-334c-420f-ae00-5f051de011fb)

Открываем блокнот, проверяем, что все работает

![image](https://github.com/user-attachments/assets/06690e7e-f47e-4a3c-83dc-cc6c21d8b1f2)

Теперь входим в панель управления и выходим из учетной записи `user777`(Вкладка админа отсутствует). Снова входим с правами admin в панель управления

![image](https://github.com/user-attachments/assets/bb5480d4-5179-4b41-9896-72dffd66d769)

### 4) Аналогичным образом создаем еще двух пользователей user666 и user555. Запускаем их образы с ноутбуками из панели управления, нажимая на иконку Start Server

Существует более простой способ создания пользователей, которые заранее известны, например 'user111', 'user222', 'user333'.

Нам необходимо просто добавить эту строчку в `jupyterhub_config.py`
```
c.Authenticator.allowed_users = {'user111', 'user222', 'user333'}
```
и пересобрать образ..

Если мы запустили `jupyterhub` и у нас нет постоянного доступа к серверу на котором он развернут...
В данном случае продолжаем работать в панели управления администратора, так мы сможем добавлять пользователя в любое время.

![image](https://github.com/user-attachments/assets/9678b245-6e08-4ca1-82ec-1de9b9625d2f)

Возвращаемся в терминал и смотрим запущенные контейнеры

![image](https://github.com/user-attachments/assets/3c2f77c7-ebd5-4861-9037-ddb3ab9c9b74)

Теперь проверим существующие контейнеры для сети `jupyterhubtest`

`docker network inspect jupyterhubtest`

![image](https://github.com/user-attachments/assets/36a7d982-7859-42ae-9f7f-74ec8904dfa6)

Видим сам jupyterhub, контейнер админа и 2 пользовательских контейнера, а также видим дополнительную информацию

### 5) Теперь нам нужно создать базу данных PostgreSQL в отдельном контейнере, также в одной сети с юпитер хабом 
Останавливаем наш сервис

`docker compose down`

добавим в docker-compose.yaml еще один сервис

`docker-compose.yaml`
```
services:
  postgrestest:
    image: postgres:17.2-bookworm
    container_name: postgrestest
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres_db
      PGDATA: /var/lib/postgresql/data/
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data/
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U postgres -d postgres_db" ]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped
    networks:
      - jupyterhubtest

volumes:
  postgres-data:
  jupyterhub-data:
```
### 6) Пересобираем образ

`docker-compose build`

![image](https://github.com/user-attachments/assets/a610a0f6-c711-4e30-a4b6-18adb5ab9a5f)

`docker compose up -d`

![image](https://github.com/user-attachments/assets/107cda60-f99e-4319-9c81-02fce19fcbb0)

### 7) Теперь заходим по адресу `http://skayfaks.keenetic.pro:35003` в юпитер хаб, под любым пользователем которго мы ранее создавали, я войду под админом
Далее нам нужно создать новый блокнот, создать скрипт для доступа к вновь созданной базе данных и создать в ней таблицу
Открываем блокнот
и устанавливаем библиотеку `psycopg2`

`!pip install psycopg2-binary`

![image](https://github.com/user-attachments/assets/c449c32c-bd67-434e-a0a7-78603dadd28e)

Создаем скрипт для подключения к базе данных, создаем таблицу, наполняем её и потом удаляем

```
import psycopg2
connect_postgres = {
    'dbname': 'postgres_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'postgrestest',
    'port': '5432'
}
try:
    # соединение с базой данных
    connection = psycopg2.connect(**connect_postgres)
    cursor = connection.cursor()
    
    test_table = '''
    CREATE TABLE IF NOT EXISTS test_table (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        value INTEGER
    );
    '''
    # Выполняем запрос
    cursor.execute(test_table)
    connection.commit()
    
    print("Таблица test_table успешно создана.")
    
    # наполняем тестовыми данными
    test_data = [
        ('Игорь', 100),
        ('Артем', 200),
        ('Петя', 300),
        ('Влад', 400),
        ('Саша', 500)
    ]
    
    # осуществляем вставку в таблицу
    insert_query = '''
    INSERT INTO test_table (name, value) VALUES (%s, %s);
    '''
    
    cursor.executemany(insert_query, test_data)
    connection.commit()
    
    print("Тестовые данные успешно вставлены.")
    
    # вывод данных
    select_query = 'SELECT * FROM test_table;'
    cursor.execute(select_query)
    
    # получение всех строк из ответа
    records = cursor.fetchall()
    
    print("Данные из таблицы test_table:")
    for row in records:
        print(f"id: {row[0]}, name: {row[1]}, value: {row[2]}")
    connection.commit()   
    # теперь удаляем таблицу
    drop_table_query = 'DROP TABLE IF EXISTS test_table;'
    cursor.execute(drop_table_query)
    connection.commit()
    
    print("Таблица test_table успешно удалена.")
    
except Exception as error:
    print("Произошла ошибка:", error)
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
```
![image](https://github.com/user-attachments/assets/2dc3ef94-d134-4b3d-9827-d3f130ae5192)

### 8) Запускаем скрипт и смотрим на результат выполнения

![image](https://github.com/user-attachments/assets/141289fe-ce8a-4ac0-bb07-a1d6b427190a)

Вторая часть выполнена, теперь у нас есть развернутая среда для написания кода JupyterHub, создаются отдельные ноутбуки для пользователей и есть возможность подключенния к базе данных PostgreSQL

