from dataclasses import dataclass, field
from os import PathLike
import toml
from pathlib import Path


@dataclass
class PrivacySettings:
    enable_folder_listing: bool = True
    arbitrary_files: bool = True
    path_traversal: bool = True


@dataclass
class ServerSettings:
    port: int = 8080
    bind: str = "127.0.0.1"


@dataclass
class FileSettings:
    wildcard_folders: list[Path] = field(default_factory=list)

    def __post_init__(self):
        # make sure all paths are Path objects and resolve them to absolute paths
        self.wildcard_folders = [Path(x).absolute() for x in self.wildcard_folders]


@dataclass
class Settings:
    privacy: PrivacySettings = field(default_factory=PrivacySettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    files: FileSettings = field(default_factory=FileSettings)

    def __post_init__(self):
        # resolve recursive dataclasses; pydantic does this automatically but it's another dependency
        self.privacy = PrivacySettings(**self.privacy)
        self.server = ServerSettings(**self.server)
        self.files = FileSettings(**self.files)


def get_config(config_file: PathLike = Path("config.toml")) -> Settings:
    return Settings(**toml.load(config_file))
