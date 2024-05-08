import dotenv, os, paramiko, re
from pt_logger import logger

dotenv.load_dotenv()
HOST = os.getenv("SSH_HOST")
PORT = os.getenv("SSH_PORT")
USER = os.getenv("SSH_USER")
PASS = os.getenv("SSH_PASS")

def exec_command_on_remote(command: str) -> str: 
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logger.debug(f"Connecting to remote {USER}@{HOST}:{PORT}")
        client.connect(
            hostname=HOST,
            port=PORT,
            username=USER,
            password=PASS,
        )
    except:
        logger.error("Couldn't connect to remote")
        return "Couldn't connect to remote"

    _, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    if (len(data) > 4096):
        logger.warn("SSH output is too big")
        return data[:4093] + "..."
    else:
        return data

### Сбор информации о системе ###
#  О релизе
def get_release() -> str:
    logger.debug("Getting release from remote")
    return exec_command_on_remote("cat /etc/os-release")

# Об архитектуры процессора, имени хоста системы и версии ядра.
def get_uname() -> str:
    logger.debug("Calling uname on remote")
    resultString  = f"Архитектура: {exec_command_on_remote('uname --processor')}\n"
    resultString += f"Имя хоста  : {exec_command_on_remote('uname --nodename')}\n"
    resultString += f"Версия ядра: {exec_command_on_remote('uname --kernel-version')}\n"
    return resultString
    
# О времени работы
def get_uptime() -> str:
    logger.debug("Calling uptime on remote")
    return exec_command_on_remote("uptime --pretty")

### Сбор информации о состоянии файловой системы ###
def get_df() -> str:
    logger.debug("Calling df on remote")
    return exec_command_on_remote("df -h")

### Сбор информации о состоянии оперативной памяти ###
def get_free() -> str:
    logger.debug("Calling free on remote")
    return exec_command_on_remote("free -h")

### Сбор информации о производительности системы ###
def get_mpstat() -> str:
    logger.debug("Calling mpstat on remote")
    return exec_command_on_remote("mpstat")

### Сбор информации о работающих в данной системе пользователях ###
def get_w() -> str:
    logger.debug("Calling w on remote")
    return exec_command_on_remote("w")

### Сбор логов ###
# Последние 10 входов в систему
def get_auths() -> str:
    logger.debug("Calling last on remote")
    return exec_command_on_remote("last | head -n 10")

# Последние 5 критических событий #
def get_critical() -> str:
    logger.debug("Calling dmesg on remote")
    result = exec_command_on_remote("dmesg --level crit | head -n 5")
    if (result == ""):
        return "Нет критических событий"
    else:
        return result

### Сбор информации о запущенных процессах ###  
def get_ps() -> str:
    logger.debug("Calling ps on remote")
    return exec_command_on_remote("ps")

### Сбор информации об используемых портах ###  
def get_ss() -> str:
    logger.debug("Calling ss on remote")
    return exec_command_on_remote("ss")

### Сбор информации об установленных пакетах ###  
def get_apt_list(package: str = "") -> str:
    # should prevent command injections
    specialChars = re.compile(r"[&|;\n`]|\$\(")
    if (specialChars.search(package) != None):
        logger.critical(f"Malicius payload detected {package}")
        return "Forbiden package name"
    else:
        return exec_command_on_remote(f"apt list {package}")

### Сбор информации информации о запущенных сервисах ###  
def get_services() -> str:
    return exec_command_on_remote("systemctl list-units --type=service --state=running | grep 'running'")

def get_repl_logs() -> str:
    return exec_command_on_remote("cat /var/log/postgresql/postgresql-15-main.log | grep -i 'replication'")