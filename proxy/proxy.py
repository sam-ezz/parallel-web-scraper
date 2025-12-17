import os 
import random

class Proxies():
    def __init__(self):
        path =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'proxies.txt')
        self.proxies = []
        if os.path.exists(path):
            with open(path) as f:
                content = f.read().strip()
                if content:
                    clean_content = content.replace("'", "").replace(" ", "").replace("\n", ",")
                    self.proxies = [p for p in clean_content.split(',') if p]

    def get_proxy(self):
        if not self.proxies or len(self.proxies) < 1:
            return None
         
        return random.choice(self.proxies)
