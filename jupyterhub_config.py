from dockerspawner import DockerSpawner
import os, nativeauthenticator
c = get_config()

# Основные настройки JupyterHub
c.JupyterHub.ip = '0.0.0.0'  # Позволяет принимать подключения от всех интерфейсов (jupyterhub)
# c.JupyterHub.port = 8000

c.JupyterHub.authenticator_class = "nativeauthenticator.NativeAuthenticator" # Назначаем класс аутентификации
# c.JupyterHub.template_paths = [f"{os.path.dirname(nativeauthenticator.__file__)}/templates/"] # лужит для указания дополнительных путей к каталогам, содержащим HTML-шаблоны, которые JupyterHub будет использовать для формирования пользовательских интерфейсов
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
c.JupyterHub.start_timeout = 120 # параметр задает максимальное время (в секундах), в течение которого JupyterHub ожидает, что будет произведён успешный запуск контролируемого процесса
c.JupyterHub.shutdown_no_activity_timeout = 600 #  Таймаут для автоматического завершения работы контейнеров при отсутствии активности (10 минут)
c.JupyterHub.shutdown_on_logout = True # автоматически останавливает сервер пользователя, как только он выходит из системы
c.DockerSpawner.use_internal_ip = True # параметр управляет использованием внутренних IP-адресов Docker
c.DockerSpawner.network_name = "jupyterhub-network" # Имя сети Docker, которое будет использоваться
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR", "/home/jovyan/work")
c.DockerSpawner.notebook_dir = notebook_dir # Каталог, который будет монтироваться в контейнере для хранения файлов Jupyter
c.DockerSpawner.volumes = {"jupyterhub-user-{username}": notebook_dir} # Настройка монтирования томов для сохранения данных пользователей
c.DockerSpawner.remove = True # Автоматически удаляет контейнеры после их остановки
c.DockerSpawner.debug = True # Включает отладку для более детальной диагностики, если что-то пойдет не так

c.JupyterHub.db_url = "sqlite:////srv/jupyterhub/data/jupyterhub.sqlite" # Указывает использовать SQLite для хранения данных JupyterHub
c.JupyterHub.log_level = 'DEBUG' # Устанавливает уровень логирования на DEBUG



