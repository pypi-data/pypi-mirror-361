import requests
import os
import json
import time
import getpass
import datetime
from typing import Optional, Dict, Any
import jwt  # pyjwt
import sys  # Added for streaming output
from yaspin import yaspin  # Spinner integration


class Client:
    """
    Client for interacting with the Tilantra Model Swap Router API.
    Usage:
        guidera_client = Client()
        response = guidera_client.generate(prompt, prefs, cp_tradeoff_parameter)
        suggestions = guidera_client.get_suggestions(prompt)
    """

    def __init__(
        self,
        auth_token: Optional[str] = None,
        api_base_url: str = "http://139.59.5.84",
    ):
        self.auth_token = auth_token or self._load_jwt()
        self.api_base_url = api_base_url.rstrip("/")

    def _jwt_file_path(self):
        return os.path.expanduser("~/.guidera_jwt.json")

    def _load_jwt(self):
        try:
            with open(self._jwt_file_path(), "r") as f:
                data = json.load(f)
                token = data.get("token")
                if not token:
                    return None
                # Decode the JWT without verifying signature (for expiry check only)
                try:
                    payload = jwt.decode(token, options={"verify_signature": False})
                    exp = payload.get("exp")
                    if exp and exp > time.time():
                        return token
                except Exception:
                    pass
        except Exception:
            pass
        return None

    def _save_jwt(self, token, exp):
        with open(self._jwt_file_path(), "w") as f:
            json.dump({"token": token, "exp": exp}, f)

    def _login_prompt(self):
        email = input("Enter your email: ")
        password = getpass.getpass("Enter your password: ")
        return email, password

    def login(self):
        email, password = self._login_prompt()
        url = f"{self.api_base_url}/users/login"
        payload = {"email": email, "password": password}
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            token = data["token"]
            exp = data.get("exp", int(time.time()) + 2 * 3600)
            self._save_jwt(token, exp)
            self.auth_token = token
        except requests.RequestException as e:
            print("Login failed:", e)
            raise

    @staticmethod
    def register_user(
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        company: Optional[str] = None,
        api_base_url: str = "http://139.59.5.84",
    ) -> Dict[str, Any]:
        url = f"{api_base_url.rstrip('/')}/register"
        payload = {
            "username": username,
            "email": email,
            "password": password,
        }
        if full_name:
            payload["full_name"] = full_name
        if company:
            payload["company"] = company
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, "response", None)}

    def _ensure_auth(self):
        if not self.auth_token:
            self.auth_token = self._load_jwt()
            if not self.auth_token:
                self.login()

    def generate(
        self,
        prompt: str,
        prefs: Optional[Dict[str, Any]] = None,
        cp_tradeoff_parameter: float = 0.7,
        compliance_enabled: bool = False,
        stream: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a response from the backend. If stream=True, stream the response and handle spinner/progress lines.
        """
        self._ensure_auth()
        url = f"{self.api_base_url}/generate"
        headers = {"Authorization": f"Bearer {self.auth_token}", "accept": "text/plain", "Content-Type": "application/json"}
        payload = {
            "prompt": prompt,
            "prefs": prefs or {},
            "cp_tradeoff_parameter": cp_tradeoff_parameter,
            "compliance_enabled": compliance_enabled,
        }
        try:
            if stream:
                # Spinner while connecting to backend
                with yaspin(text="Preparing...", color="white") as connect_spinner:
                    resp = requests.post(url, json=payload, headers=headers, stream=True)
                    resp.raise_for_status()
                    connect_spinner.ok("✔")
                # Spinner for picking best model
                with yaspin(text="Picking best model for you", color="magenta") as model_spinner:
                    time.sleep(1)  # Simulate model selection duration
                    model_spinner.ok("✔")
                # Spinner for fetching response
                with yaspin(text="Fetching response", color="cyan") as spinner:
                    last_non_spinner = None
                    for line in resp.iter_lines():
                        if line:
                            text = line.decode()
                            # print(repr(text))  # Uncomment for debugging line endings
                            if text.endswith('\r') and not text.endswith('\n'):
                                spinner.text = text.rstrip('\r')
                            elif text.endswith('\r\n'):
                                spinner.text = text.rstrip('\r\n')
                            elif text.endswith('\n'):
                                # Final or progress message, print after spinner
                                last_non_spinner = text.rstrip('\n')
                            else:
                                last_non_spinner = text
                    spinner.ok("✔")
                with yaspin(text="Checking compliance", color="yellow") as compliance_spinner:
                    time.sleep(1)  # Simulate compliance check duration
                    compliance_spinner.ok("✔")
                if last_non_spinner:
                    # Try to parse as JSON and remove 'ner' if present
                    try:
                        resp_json = json.loads(last_non_spinner)
                        if "compliance_report" in resp_json and "ner" in resp_json["compliance_report"]:
                            del resp_json["compliance_report"]["ner"]
                        print(json.dumps(resp_json, indent=2))
                    except Exception:
                        print(last_non_spinner)
                return {"status": "streamed"}
            else:
                resp = requests.post(url, json=payload, headers=headers)
                if resp.status_code == 401:
                    # Token invalid/expired, prompt for login and retry once
                    self.login()
                    headers = {"Authorization": f"Bearer {self.auth_token}", "accept": "text/plain", "Content-Type": "application/json"}
                    resp = requests.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                resp_json = resp.json()
                if "compliance_report" in resp_json and "ner" in resp_json["compliance_report"]:
                    del resp_json["compliance_report"]["ner"]
                print(json.dumps(resp_json, indent=2))
                return resp_json
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, "response", None)}

    def get_suggestions(self, prompt: str) -> Dict[str, Any]:
        self._ensure_auth()
        url = f"{self.api_base_url}/suggestion"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {"prompt": prompt}
        try:
            resp = requests.post(url, json=payload, headers=headers)
            if resp.status_code == 401:
                # Token invalid/expired, prompt for login and retry once
                self.login()
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, "response", None)}