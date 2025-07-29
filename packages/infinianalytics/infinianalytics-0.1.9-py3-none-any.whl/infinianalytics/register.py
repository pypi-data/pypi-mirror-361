# register.py

import requests
from datetime import datetime

class InfiniAnalytics:
    BASE_URL = "https://api.analytics.infini.es"  
    PING_ENDPOINT = f"{BASE_URL}/v1/ping/"
    REGISTER_ENDPOINT = f"{BASE_URL}/v1/register/"

    def __init__(self, token: str, automation_id: str, execution_id: str = None):
        """
        Parámetros:
            token (str): Token para la autenticación.
            automation_id (str): ID de la automatización.
            execution_id (str, opcional): ID de la ejecución en curso. 
                                          Si no se especifica, se genera uno con la fecha/hora actual.
        """
        self.token = token
        self.automation_id = automation_id
        # Si no se especifica execution_id, se crea uno con la fecha/hora actual (ISO8601).
        self.execution_id = execution_id or datetime.now().isoformat()

        self.session = requests.Session()
        self.session.headers.update({
            "token": self.token,
            "Content-Type": "application/json",
        })

        # Verificamos conexión (opcional): no lanzamos excepción; si falla, solo avisamos.
        if not self._check_connection():
            print("Error: No se ha podido verificar la conexión. "
                  "Por favor comprueba tu conexión y los parámetros de inicialización.")

    def _check_connection(self) -> bool:
        """Verifica la conexión con la API usando el endpoint /ping/."""
        try:
            payload = {
                "automation_id": self.automation_id,
            }
            response = self.session.post(self.PING_ENDPOINT, json=payload)
            if response.status_code == 200:
                return True
            else:
                print(f"[check_connection] La API devolvió un código no esperado: {response.status_code}")
                return False
        except Exception as e:
            print(f"[check_connection] Excepción capturada: {e}")
            return False

    def start(self, description: str):
        """Inicia un proceso en la API."""
        payload = {
            "event": "START",
            "automation_id": self.automation_id,
            "execution_id": self.execution_id,
            "description": description,
        }
        try:
            response = self.session.post(self.REGISTER_ENDPOINT, json=payload)
            
            if response.status_code != 201:
                print(f"[start] La API devolvió un código no esperado: {response.status_code}")
                return None
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[start] Error al iniciar proceso: {e}")
            return None

    def event(self, description: str):
        """Registra un evento en la API."""
        payload = {
            "event": "EVENT",
            "automation_id": self.automation_id,
            "execution_id": self.execution_id,
            "description": description,
        }
        try:
            response = self.session.post(self.REGISTER_ENDPOINT, json=payload)

            if response.status_code != 201:
                print(f"[event] La API devolvió un código no esperado: {response.status_code}")
                return None
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[event] Error al registrar evento: {e}")
            return None

    def warning(self, description: str):
        """Registra un warning en la API."""
        payload = {
            "event": "WARNING",
            "automation_id": self.automation_id,
            "execution_id": self.execution_id,
            "description": description,
        }
        try:
            response = self.session.post(self.REGISTER_ENDPOINT, json=payload)

            if response.status_code != 201:
                print(f"[event] La API devolvió un código no esperado: {response.status_code}")
                return None
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[event] Error al registrar evento: {e}")
            return None

    def end(self, description: str):
        """Finaliza un proceso en la API."""
        payload = {
            "event": "END",
            "automation_id": self.automation_id,
            "execution_id": self.execution_id,
            "description": description,
        }
        try:
            response = self.session.post(self.REGISTER_ENDPOINT, json=payload)
            
            if response.status_code != 201:
                print(f"[end] La API devolvió un código no esperado: {response.status_code}")
                return None
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[end] Error al finalizar proceso: {e}")
            return None

    def error(self, description: str, error_id: str = None, error_description: str = None):
        """Registra un error en la API."""
        payload = {
            "event": "ERROR",
            "automation_id": self.automation_id,
            "execution_id": self.execution_id,
            "description": description,
            "error_id": error_id,
            "error_description": error_description,
        }
        try:
            response = self.session.post(self.REGISTER_ENDPOINT, json=payload)

            if response.status_code != 201:
                print(f"[error] La API devolvió un código no esperado: {response.status_code}")
                return None
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[error] Error al registrar error: {e}")
            return None
