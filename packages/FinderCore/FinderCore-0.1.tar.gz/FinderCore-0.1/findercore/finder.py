import requests

class Finder:
    _part1_b64 = "https://core-hub-node.vercel.app/api/core"
    _part2_b64 = "?nick="

    @property
    def RAIZ(self):
        part1 = self._part1_b64
        part2 = self._part2_b64
        return part1 + part2 

    def __init__(self):
        pass

    def find(self, nick: str):
        if not nick:
            raise ValueError("El nick es requerido.")

        try:
            response = requests.get(self.RAIZ + nick, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            return {"error": "La API externa no respondió a tiempo.", "results": []}
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return {"error": "El usuario no fue encontrado en la base de datos.", "results": []}
            return {"error": f"Error HTTP: {e}", "results": []}
        except Exception as e:
            return {"error": f"Error interno: {e}", "results": []}

        data = response.json()
        if not data.get("results"):
            return {"error": "El usuario no fue encontrado en la base de datos.", "results": []}

        return data
