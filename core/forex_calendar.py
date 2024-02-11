import random, json, datetime, calendar, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


class NewsCalendar:
    def __init__(self, url: str, chrome_dir: str, filename="./calendar.json") -> None:
        self.url = url
        self.chrome_dir = chrome_dir
        self.filename = filename
        self.driver = self.create_driver()

    def run(self, save=True):
        value_list, impacts = self.parse_data()
        serialzed = self.serialize_to_dict(value_list, impacts)
        self.driver.quit()
        if save:
            self.save_data_as_json(serialzed, self.filename)
        return serialzed

    def create_driver(self):
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        ]

        user_agent = random.choice(user_agent_list)

        browser_options = webdriver.ChromeOptions()
        browser_args = [
            "--disable-extensions",
            "--no-sandbox",
            "--headless",
            "start-maximized",
            "window-size=1900,1080",
            "disable-gpu",
            "--disable-software-rasterizer",
            "--disable-dev-shm-usage",
            f"user-agent={user_agent}",
        ]
        for arg in browser_args:
            browser_options.add_argument(arg)


        browser_options.binary_location = os.path.join(self.chrome_dir, "chrome.exe")
        chromedriver_path = os.path.join(self.chrome_dir, "chromedriver.exe")
        service = Service(chromedriver_path)
        browser_options.add_argument(f"webdriver.chrome.driver={chromedriver_path}")
        # driver = webdriver.Chrome(options=browser_options)
        driver = webdriver.Chrome(service=service, options=browser_options)

        
        return driver

    def parse_impact(self, data_table):
        xpath = ".//span[contains(@class, 'icon--ff-impact')]"
        impact_elements = data_table.find_elements(By.XPATH, xpath)
        icon_map = {
            "icon--ff-impact-red": "high",
            "icon--ff-impact-ora": "medium",
            "icon--ff-impact-yel": "low",
        }
        impacts = [
            next(
                (
                    icon_map[cls]
                    for cls in icon_map
                    if cls in el.get_attribute("class").split()
                ),
                None,
            )
            for el in impact_elements
        ]
        return impacts

    def parse_data(self) -> tuple[list[list[str]], list[str]]:
        self.driver.get(self.url)
        data_table = self.driver.find_element(By.CLASS_NAME, "calendar__table")
        value_list = []

        impacts = self.parse_impact(data_table)

        for row in data_table.find_elements(By.TAG_NAME, "tr"):
            row_data = list(
                filter(None, [td.text for td in row.find_elements(By.TAG_NAME, "td")])
            )
            if row_data:
                value_list.append(row_data)
        return value_list, impacts

    def serialize_to_dict(
        self, value_list: list[list[str]], impacts: list[str]
    ) -> list[dict[str, str | None]]:
        # Define desired currencies and impacts
        desired_currencies = ["GBP", "USD", "EUR"]
        desired_impacts = ["high"]

        def format_date(date_str: str, now=datetime.datetime.now()):
            parsed_date = datetime.datetime.strptime(date_str, "%I:%M%p")
            new_date = now.replace(
                hour=parsed_date.hour,
                minute=parsed_date.minute,
                second=0,
                microsecond=0,
            )
            return new_date.strftime("%Y-%m-%d %H:%M:%S")

        event_data_list = []

        for value, impact in zip(value_list, impacts):
            # Skip events with undesired impact or currency
            if impact not in desired_impacts or value[0] not in desired_currencies:
                continue  

            event_data = {}
            if value[0].startswith(tuple(calendar.day_abbr)):
                value.pop(0)
                # continue  # skip

            # Check if a date is present and extract it
            if any(time_indicator in value[0] for time_indicator in ["am", "pm"]):
                event_data["date"] = format_date(value.pop(0))
            # else:
            #     event_data["date"] = None

            # Assign impact, currency, and event name
            event_data["impact"] = impact
            event_data["currency"] = value.pop(0)
            event_data["event"] = value.pop(0)

            # Assign actual, forecast, previous if they exist
            event_data["actual"] = value.pop(0) if len(value) > 0 else None
            event_data["forecast"] = value.pop(0) if len(value) > 0 else None
            event_data["previous"] = value.pop(0) if len(value) > 0 else None

            # Any remaining values can be added as additional information
            if value:
                event_data["additional_info"] = value

            event_data_list.append(event_data)

        return event_data_list

    def save_data_as_json(self, events_data: list[dict], filename: str):
        with open(filename, "w") as json_file:
            json.dump(events_data, json_file, indent=4)


if __name__ == "__main__":
    url = "https://www.forexfactory.com/calendar?day=today"
    filename = "./json_data/forex_calendar.json"
    calendar_news = NewsCalendar(
        url, os.path.expanduser("./chrome"), filename
    )
    calendar_news.run()
