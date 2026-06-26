import requests
from typing import Optional, List, Dict, Any

class SIPApiClient:
    """
    API client for interacting with the Sentiment Intelligence Platform backend services.
    Includes headers injection, error validation wrappers, and timeout settings.
    """
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _handle_response(self, response: requests.Response):
        if 200 <= response.status_code < 300:
            return
            
        # Parse error detail
        try:
            body = response.json()
            detail = body.get("detail", "API Error")
            if isinstance(detail, list):
                messages = []
                for err in detail:
                    if isinstance(err, dict) and "msg" in err:
                        loc = ".".join(str(l) for l in err.get("loc", []))
                        messages.append(f"{loc}: {err['msg']}")
                    else:
                        messages.append(str(err))
                raise RuntimeError("; ".join(messages))
            elif isinstance(detail, dict):
                raise RuntimeError(detail.get("message", str(detail)))
            else:
                raise RuntimeError(str(detail))
        except (ValueError, KeyError):
            raise RuntimeError(f"HTTP Error {response.status_code}: {response.text}")

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        headers = self._headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
            
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=30,
                **kwargs
            )
            self._handle_response(response)
            if response.status_code == 204:
                return True
            return response.json()
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Cannot connect to API. Is the backend running?")
        except requests.exceptions.Timeout:
            raise RuntimeError("API request timed out (limit: 30 seconds).")

    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        payload = {
            "username": username,
            "email": email,
            "password": password
        }
        return self._request("POST", "/api/v1/auth/register", json=payload)

    def login(self, username: str, password: str) -> Dict[str, Any]:
        data = {
            "username": username,
            "password": password
        }
        # Form URL-encoded data for OAuth2
        return self._request("POST", "/api/v1/auth/login", data=data)

    def get_me(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v1/auth/me")

    def predict(self, text: str, model_name: str = "ensemble") -> Dict[str, Any]:
        payload = {
            "text": text,
            "model_name": model_name
        }
        return self._request("POST", "/api/v1/predict", json=payload)

    def predict_bulk(self, texts: List[str]) -> Dict[str, Any]:
        payload = {
            "texts": texts
        }
        return self._request("POST", "/api/v1/predict/bulk", json=payload)

    def get_history(self, sentiment: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        params = {"limit": limit}
        if sentiment:
            params["sentiment"] = sentiment
        return self._request("GET", "/api/v1/history/", params=params)

    def get_stats(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v1/history/stats")

    def delete_history(self, item_id: str) -> bool:
        return self._request("DELETE", f"/api/v1/history/{item_id}")
