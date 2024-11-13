from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import code
import sys
import importlib
import os

def start_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Set a Polish user agent
    polish_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; pl-PL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"
    chrome_options.add_argument(f"user-agent={polish_user_agent}")
    
    # Set preferred language and locale to Polish
    chrome_options.add_argument("--lang=pl-PL")
    
    # Emulate Polish timezone and set locale
    chrome_options.add_experimental_option("prefs", {
        "intl.accept_languages": "pl-PL,pl",
        "profile.default_content_setting_values.geolocation": 1  # Allow location access
    })

    # Set timezone with JavaScript execution (workaround for some websites)
    chrome_options.add_argument("--time-zone=Europe/Warsaw")
    chrome_options.add_argument("--tz=Europe/Warsaw")
    
    # Specify the path to your downloaded ChromeDriver
    chromedriver_path = "/home/retried/work/python/regvk/chromedriver"  # Update this path
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute JavaScript to override timezone in runtime (useful for websites that detect timezone with JS)
    driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Europe/Warsaw"})
    
    return driver

def open_website(driver, url):
    driver.get(url)
    print(f"Открыт сайт: {url}")

def start_interactive_shell(driver, functions_module_name):
    # Подготовка локальных переменных для интерактивного сеанса
    local_vars = {'driver': driver, 'importlib': importlib, 'functions': None}

    # Импорт начального модуля функций, если он существует
    if os.path.exists(f"{functions_module_name}.py"):
        try:
            functions = importlib.import_module(functions_module_name)
            importlib.reload(functions)
            # Установить driver в модуле functions
            functions.driver = driver
            local_vars['functions'] = functions
            print(f"Модуль '{functions_module_name}' загружен и driver установлен.")
        except Exception as e:
            print(f"Ошибка при загрузке модуля '{functions_module_name}': {e}", file=sys.stderr)

    banner = (
        "Интерактивный режим Selenium. Доступны переменные:\n"
        "- driver: объект WebDriver\n"
        "- importlib: модуль для импорта\n"
        "- functions: модуль с пользовательскими функциями\n\n"
        "Команды:\n"
        "- importlib.reload(functions)  # Перезагрузить модуль функций после изменений\n"
        "- functions.имя_функции()      # Вызвать функцию из модуля функций\n"
        "Например:\n"
        ">>> importlib.reload(functions)\n"
        ">>> functions.нажать_кнопку()\n"
        ">>> exit() # Для выхода и закрытия браузера\n"
    )
    code.interact(banner=banner, local=local_vars)

def main():
    driver = start_driver()
    try:
        # Откройте нужный сайт
        open_website(driver, "https://vk.com")  # Замените на ваш URL

        # Укажите имя модуля с функциями (без .py)
        functions_module_name = "functions"

        # Запустите интерактивный сеанс
        start_interactive_shell(driver, functions_module_name)
    except Exception as e:
        print(f"Произошла ошибка: {e}", file=sys.stderr)
    finally:
        driver.quit()
        print("Браузер закрыт.")

if __name__ == "__main__":
    main()