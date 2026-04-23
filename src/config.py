import os
from dotenv import load_dotenv
from pathlib import Path

class Settings:
    """
    A centralised configuration class to manage settings from .env files.
    """
    def __init__(self, server_name: str):
        self._load_environment(server_name)

        self.ibm_host: str = os.getenv("IBM_HOST", "")
        self.ibm_user: str = os.getenv("IBM_USER", "")
        self.ibm_password: str = os.getenv("IBM_PASSWORD", "")
        self.tn5250_map: str = os.getenv("TN5250_MAP", "285")
        self.tn5250_ssl: bool = os.getenv("TN5250_SSL", "False").lower() in ('true', '1', 't')

        if not all([self.ibm_host, self.ibm_user, self.ibm_password]):
            raise ValueError("Required environment variables IBM_HOST, IBM_USER, IBM_PASSWORD are not set.")

    def _load_environment(self, server_name: str) -> None:
        """
        Loads environment variables from a config/env/.env.{server_name} file.
        """
        env_dir = Path(__file__).parent.parent / "config" / "env"
        env_file = env_dir / f".env.{server_name}"

        if not env_file.exists():
            raise FileNotFoundError(f"Environment file not found: {env_file}")

        load_dotenv(dotenv_path=env_file, override=True)
        print(f"Loaded environment from {env_file}")