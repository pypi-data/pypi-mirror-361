from importlib import metadata

try:
    __version__ = metadata.version(__package__) if __package__ else "0.0.0"
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"


def main() -> None:
    from zet.cli import zet

    zet()
