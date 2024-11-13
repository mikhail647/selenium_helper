from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

driver = None

def log_message(message):
    """Логирует сообщение с временной меткой для отладки."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def generate_random_birthdate():
    """Генерирует случайную дату рождения для пользователя старше 18 лет."""
    today = datetime.today()
    min_age_date = today - timedelta(days=18*365)
    random_days = random.randint(0, 365*50)
    birthdate = min_age_date - timedelta(days=random_days)
    return birthdate.strftime("%d.%m.%Y")

def load_names_from_file(file_path):
    """Загружает имена из указанного файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        log_message(f"Файл {file_path} не найден.")
        return []
    
first_names = load_names_from_file('first_name.txt')
last_names = load_names_from_file('last_name.txt')

def generate_random_name():
    """Генерирует случайное имя и фамилию."""
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    return first_name, last_name


first_name, last_name = generate_random_name()
birthdate = generate_random_birthdate()
birth_day, birth_month, birth_year = birthdate.split('.')


def select_birthdate_via_ui(driver, birth_day, birth_month, birth_year):
    """
    Выбирает дату рождения через UI календаря на странице регистрации VK.

    :param driver: экземпляр Selenium WebDriver
    :param birth_day: день рождения (целое число)
    :param birth_month: месяц рождения (целое число от 1 до 12)
    :param birth_year: год рождения (целое число)
    """

    # Сопоставление номера месяца с русским названием
    months = {
        1: 'январь',
        2: 'февраль',
        3: 'март',
        4: 'апрель',
        5: 'май',
        6: 'июнь',
        7: 'июль',
        8: 'август',
        9: 'сентябрь',
        10: 'октябрь',
        11: 'ноябрь',
        12: 'декабрь'
    }

    month_name = months.get(int(birth_month), '')
    year = int(birth_year)

    try:
        # 1. Нажатие на кнопку календаря
        calendar_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[./span[contains(text(), 'Показать календарь')]]")
            )
        )
        calendar_button.click()
        log_message("Нажата кнопка 'Показать календарь'.")

        # 2. Ожидание появления календаря
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, 'vkuiCalendar')
            )
        )
        log_message("Календарь отображается.")

        # 3. Выбор года
        year_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@aria-label='Изменить год']")
            )
        )
        year_input.click()
        log_message("Открыт выпадающий список годов.")

        # 3.1. Навигация по списку годов
        # Отправляем клавиши для прокрутки списка до нужного года
        actions = ActionChains(driver)
        # Начинаем с текущего года и определяем направление прокрутки
        current_year = int(datetime.now().year)
        year_diff = current_year - year
        log_message(f"Текущий год: {current_year}, целевой год: {year}, разница: {year_diff}")
        steps = year_diff
        # Прокручиваем список
        for _ in range(steps):
            actions.send_keys(Keys.ARROW_UP)
            actions.perform()
            actions.reset_actions()
        actions.send_keys(Keys.ENTER)
        actions.perform()
        actions.reset_actions()
        log_message(f"Выбран год: {year}")
        
        #выбор месяца
        month_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@aria-label='Изменить месяц']")
            )
        )
        month_input.click()
        log_message("Открыт выпадающий список месяцев.")
        
        # 4.1. Навигация по списку месяцев
        # Получаем текущий выбранный месяц
        current_month_name = driver.find_element(By.XPATH, "//span[@class='vkuiCalendarHeader__month']").text.lower()
        current_month_number = [k for k, v in months.items() if v == current_month_name][0]
        month_diff =  current_month_number - int(birth_month)
        log_message(f"Текущий месяц: {current_month_name}, целевой месяц: {month_name}, разница: {month_diff}")

        key = Keys.ARROW_UP if month_diff > 0 else Keys.ARROW_DOWN
        for _ in range(month_diff):
            actions.send_keys(key)
            actions.perform()
            actions.reset_actions()
        # Нажимаем Enter для выбора месяца
        actions.send_keys(Keys.ENTER)
        actions.perform()
        actions.reset_actions()
        log_message(f"Выбран месяц: {month_name}")
        
        # 5. Ожидание обновления дней после изменения месяца/года
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='vkuiCalendarDays']")
            )
        )

        # 6. Выбор дня
        day_xpath = (
            f"//div[@class='vkuiCalendarDays']"
            f"//div[contains(@class, 'vkuiCalendarDay') and not(contains(@class, 'vkuiCalendarDay__hidden')) and not(@aria-disabled='true')]"
            f"//span[normalize-space(text())='{int(birth_day)}']"
            f"/ancestor::div[contains(@class, 'vkuiCalendarDay')]"
        )
        day_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, day_xpath)
            )
        )
        day_element.click()
        log_message(f"Выбран день: {birth_day}.")

    except Exception as e:
        log_message(f"Не удалось выбрать дату рождения через UI: {e}")
        
def end():
    pass

def tryin():
    # **Выбор даты рождения через UI**
    try:
        select_birthdate_via_ui(driver, birth_day, birth_month, birth_year)
        
    except Exception as e:
        log_message(f"Ошибка при выборе даты рождения: {e}")
        # Дополнительная обработка ошибки, если необходимо