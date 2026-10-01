"""Google Colab setup shared by the tutorial notebooks.

The notebooks point here instead of embedding a setup cell. On Colab, clone
this repository into the session first (a fresh runtime cannot import this
module until the repo is on disk), then call :func:`setup_colab`. That
installs the tutorial packages, clones this repository into
``/content/book-agents`` when it is missing, and copies a secret named
``OPENAI_API_KEY`` into the environment. The key is not printed.

Local Jupyter and VS Code print a skip line and do not clone or install.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/junlinghu/book-agents.git"
COLAB_REPO = Path("/content/book-agents")
READY_MARKER = Path("tutorial") / "common" / "client.py"

REQUIREMENTS = (
    ("openai", "openai>=1.40.0"),
    ("dotenv", "python-dotenv>=1.0.1"),
    ("httpx", "httpx>=0.27.0"),
)

MISSING_KEY = (
    "OPENAI_API_KEY is empty. On Colab, add a secret named OPENAI_API_KEY "
    "(the key icon) and rerun this cell. Locally, copy .env.example to .env "
    "and paste a key from https://platform.openai.com/api-keys. Never commit .env."
)


def in_colab():
    """True on Google Colab. False in local Jupyter and VS Code."""
    try:
        import google.colab
    except ImportError:
        return False
    return Path("/content").is_dir() and google.colab is not None


def _install_missing():
    missing = []
    for module_name, requirement in REQUIREMENTS:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(requirement)
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *missing])


def _ensure_repo():
    repo = COLAB_REPO
    marker = repo / READY_MARKER
    if marker.is_file():
        return repo
    if repo.exists() and not (repo / ".git").exists():
        raise RuntimeError(
            str(repo) + " exists but is not a git checkout. "
            "Move that folder aside and run this cell again."
        )
    if repo.exists():
        shutil.rmtree(repo)
    try:
        subprocess.check_call([
            "git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
            REPO_URL, str(repo),
        ])
        subprocess.check_call([
            "git", "-C", str(repo), "sparse-checkout", "set", "tutorial",
        ])
    except subprocess.CalledProcessError:
        if repo.exists():
            shutil.rmtree(repo)
        subprocess.check_call(["git", "clone", "--depth", "1", REPO_URL, str(repo)])
    if not marker.is_file():
        raise RuntimeError(
            "Colab setup could not find tutorial/common/client.py after cloning."
        )
    return repo


def _copy_secret():
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return
    try:
        from google.colab import userdata
        secret = userdata.get("OPENAI_API_KEY")
    except Exception:
        secret = ""
    if secret and str(secret).strip():
        os.environ["OPENAI_API_KEY"] = str(secret).strip()


def setup_colab():
    """Clone and install on Colab. Skip both when the kernel is local.

    On Colab, raise if ``OPENAI_API_KEY`` is still empty. Do not print the key.
    """
    if not in_colab():
        print("Not Colab. Skipped clone and pip install.")
        return

    _install_missing()
    repo = _ensure_repo()
    os.chdir(repo)
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    _copy_secret()
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise RuntimeError(MISSING_KEY)
    print("Colab: tutorial/ is ready. OPENAI_API_KEY is set (value hidden).")
