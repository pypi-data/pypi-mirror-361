import time

from selenium.webdriver.common.by import By

class TagEvent:
    def __call__(self, driver):
        self.perform_event(driver)

    def perform_event(self, driver):
        raise NotImplementedError


class SecondDelayEvent(TagEvent):
    def __init__(self, element: str = None, time_delay: int = 10):
        self.element = element
        self.time_delay = time_delay

    def perform_event(self, driver):
        if self.element.startswith("."):
            identifier = self.element[1:].split("::")
            elems = driver.find_elements(By.CLASS_NAME, identifier[0])
            elem = elems[int(identifier[1])] if len(identifier) == 2 else elems[0]
        elif self.element.startswith("#"):
            identifier = self.element[1:]
            elem = driver.find_elements(By.ID, identifier)
        elif self.element.startswith("/"):
            identifier = self.element
            elem = driver.find_element(By.XPATH, identifier)
        driver.execute_script("arguments[0].scrollIntoView(behavior='smooth', block='start');", elem)
        time.sleep(self.time_delay)


class ClickEvent(TagEvent):
    def __init__(self, element: str = ""):
        self.element = element

    def perform_event(self, driver):
        if self.element.startswith("."):
            identifier = self.element[1:].split("::")
            elems = driver.find_elements(By.CLASS_NAME, identifier[0])
            elem = elems[int(identifier[1])] if len(identifier) == 2 else elems[0]
        elif self.element.startswith("#"):
            identifier = self.element[1:]
            elem = driver.find_elements(By.ID, identifier)
        elif self.element.startswith("/"):
            identifier = self.element
            elem = driver.find_element(By.XPATH, identifier)
        elem.click()