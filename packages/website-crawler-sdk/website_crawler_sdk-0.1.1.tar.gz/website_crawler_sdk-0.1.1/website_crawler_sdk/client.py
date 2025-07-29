import requests
import json
import threading
import time

"""
Author: Pramod Choudhary (websitecrawler.org)
Version: 1.1
Date: July 10, 2025
"""

class WebsiteCrawlerClient:
    BASE_URL = "https://www.websitecrawler.org/api"

    def __init__(self, config):
        self.config = config
        self.api_key = self.config.get_api_key()
        self.current_url = None
        self.crawl_status = None
        self.crawl_data = None
        self.wait_time = 0
        self.task_started = False
        self.stop_main_task = threading.Event()
        self.ftr = [None, None]

    def _build_url(self, endpoint, params=None):
        url = f"{self.BASE_URL}{endpoint}"
        if params:
            query = "&".join([f"{k}={v}" for k, v in params.items()])
            url += query
        return url

    def _get_response(self, url):
        try:
            headers = {"Accept": "application/json"}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
        except requests.RequestException as e:
            print(f"[Request Error] {e}")
        return None

    def submit_url_to_website_crawler(self, url, limit):
        if self.task_started:
            print("Task is already running")
            return

        self.task_started = True

        def wait_time_task():
            while not self.stop_main_task.is_set():
                #print("Gettint the waittime")
                wt_url = self._build_url("/crawl/waitTime?", {"key": self.api_key})
                response = self._get_response(wt_url)
                #print(f"Requesting: {wt_url}")
                #print(f"Raw waitTime API response: {response}")

                if response:
                    try:
                        obj = json.loads(response)
                        wait_time = int(obj.get("waitTime", 0))
                        if wait_time > 0:
                            self.wait_time = wait_time
                            #print(f"Received waitTime: {self.wait_time}s")
                            self.stop_main_task.set()

                            self.ftr[1] = threading.Thread(
                                target=self._main_task_loop, args=(url, limit)
                            )
                            self.ftr[1].start()
                    except Exception as e:
                        print(f"Failed to parse waitTime: {e}")
                        self.task_started=False

                time.sleep(2)

        self.ftr[0] = threading.Thread(target=wait_time_task)
        self.ftr[0].start()

    def _main_task_loop(self, url, limit):
        print("in main task loop...")
        crawl_url = self._build_url("/crawl/start?", {
            "url": url,
            "limit": limit,
            "key": self.api_key
        })

        init_response = self._get_response(crawl_url)
        if init_response:
                try:
                    #print(f"CrawlURL: {crawl_url}")
                    #print(f"Raw status API response: {init_response}")
                    obj = json.loads(init_response)
                    self.crawl_status = obj.get("status")
                    #print(f"Checking crawl status in first...")
                except Exception as e:
                    print(f"Failed to parse status response: {e}")
                    self.task_started=False
                    

        while True:
            #print(f"Checking crawl status in loop...")

            status_url = self._build_url("/crawl/start?", {
                "url": url,
                "limit": limit,
                "key": self.api_key
            })
            response = self._get_response(status_url)
            #print(f"status_url: {status_url}")
            #print(f"Raw waitTime API response: {response}")
            if response:
                try:
                    obj = json.loads(response)
                    self.crawl_status = obj.get("status")
                except Exception as e:
                    print(f"Failed to parse status response: {e}")
                    self.task_started=False
                    break

            if self.crawl_status == "Crawling":
                current_url_req = self._build_url("/crawl/currentURL?", {
                    "url": url,
                    "key": self.api_key
                })
                current_resp = self._get_response(current_url_req)
                if current_resp:
                    try:
                        obj = json.loads(current_resp)
                        self.current_url = obj.get("currentURL")
                    except Exception as e:
                        print(f"Failed to parse currentURL response: {e}")
                        self.task_started=False
                        break

            if self.crawl_status == "Completed!":
                crawl_data_req = self._build_url("/crawl/cwdata?", {
                    "url": url,
                    "key": self.api_key
                })
                self.crawl_data = self._get_response(crawl_data_req)
                self.task_started = False
                print("Task completed. Exiting loop.")
                break

            time.sleep(self.wait_time)

    def get_current_url(self):
        return self.current_url

    def get_crawl_status(self):
        return self.crawl_status

    def get_crawl_data(self):
        return self.crawl_data

    def get_task_status(self):
        return self.task_started
