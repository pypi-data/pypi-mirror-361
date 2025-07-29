from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

def project_path(*subdirs) -> Path:
    return _REPO_ROOT.joinpath(*subdirs).resolve()
