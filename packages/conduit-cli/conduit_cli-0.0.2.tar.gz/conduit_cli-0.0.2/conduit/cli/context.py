"""
Context object for Conduit CLI.
"""
from pathlib import Path
from typing import Optional

from ..services.config import get_config_service, ConfigService
from ..security.keys import KeyStore

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
    max_content_width=120,
    auto_envvar_prefix='CONDUIT',
)

class ConduitContext:
    """
    Context object for Conduit CLI.
    
    This class holds the configuration and state for the CLI commands.
    It is passed around to commands to access shared resources like config.
    """
    def __init__(self, config_path: Optional[Path] = None, verbosity: int = 0, calling_dir: Optional[Path] = None):
        
        self.verbosity = verbosity
        self.config_service: ConfigService = get_config_service(config_path)
        self.config_service.load()
        self.calling_dir = calling_dir or Path.cwd()
        self.keystore = KeyStore(Path(self.config_service.get("keys_dir")))

# repo = click.make_pass_decorator(ConduitContext, ensure=True)
# class ConduitContext:
#     CONDUIT_VERSION = "0.1.0"  # update as needed
#     API_VERSION = "v1"

#     def __init__(self, config_path: Optional[Path] = None):
#         # Use provided config_path or default to ~/.conduit/config.yaml
#         self.home_dir = Path.home() / ".conduit"
#         self.config_path = config_path or self.home_dir / "config.yaml"
#         self.cache_path = self.home_dir / "cache"
#         self.env_prefix = "CONDUIT"

#         # Ensure directories exist and create default config if needed.
#         self._ensure_directories()
#         self._load_or_create_config()

#         # Placeholder for plugins.
#         self.plugins: Dict[str, Any] = {}

#     def _ensure_directories(self):
#         self.home_dir.mkdir(parents=True, exist_ok=True)
#         self.cache_path.mkdir(parents=True, exist_ok=True)

#     def _load_or_create_config(self):
#         if not self.config_path.exists():
#             default_config = {
#                 "version": self.CONDUIT_VERSION,
#                 "apiVersion": self.API_VERSION,
#                 "cache": {
#                     "path": str(self.cache_path),
#                     "maxSize": "1GB"
#                 },
#                 "registry": {
#                     "default": "https://registry.conduit.io"
#                 },
#                 "plugins": {}
#             }
#             with open(self.config_path, "w") as fp:
#                 yaml.safe_dump(default_config, fp)
#             self._config = default_config
#         else:
#             with open(self.config_path, "r") as fp:
#                 self._config = yaml.safe_load(fp) or {}

#         self._load_env_vars()

#     def _load_env_vars(self):
#         # Override configuration with any CONDUIT_* environment variables.
#         for key, value in os.environ.items():
#             if key.startswith(f"{self.env_prefix}_"):
#                 config_key = key[len(self.env_prefix)+1:].lower().replace('_', '.')
#                 self.set_config(config_key, value)

#     def get_config(self, key: str, default: Any = None) -> Any:
#         keys = key.split(".")
#         res = self._config
#         for k in keys:
#             res = res.get(k, {})
#         return res or default

#     def set_config(self, key: str, value: Any):
#         keys = key.split(".")
#         cfg = self._config
#         for k in keys[:-1]:
#             cfg = cfg.setdefault(k, {})
#         cfg[keys[-1]] = value

#     def save_config(self):
#         with open(self.config_path, "w") as fp:
#             yaml.safe_dump(self._config, fp)
