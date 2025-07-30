import requests

class CatAPI:
    def __init__(self):
        self.base_url = "https://catfact.ninja"
    
    def RandomFact(self):
        response = requests.get(f"{self.base_url}/fact")
        return response.json().get("fact", "Факт не найден 😿")
    
    def GetBreeds(self, limit=5):
        response = requests.get(f"{self.base_url}/breeds?limit={limit}")
        return response.json().get("data", [])