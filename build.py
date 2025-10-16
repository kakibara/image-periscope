import subprocess
from pathlib import Path

# The version of the build backend, not of the package.
__version__ = "1.0.0"


def build_sdist(sdist_name, sdist_directory=None):
    """(poetry-core internal) This function is called when building a source distribution.
    See https://github.com/python-poetry/poetry-core/blob/main/docs/build.md
    """
    _write_commit_hash()
    # Since we are not actually building a sdist, we just return the default sdist name.
    # This is a bit of a hack, but it's the easiest way to hook into the build process.
    return Path(sdist_name).name


def build_wheel(wheel_name, wheel_directory=None):
    """(poetry-core internal) This function is called when building a wheel.
    See https://github.com/python-poetry/poetry-core/blob/main/docs/build.md
    """
    _write_commit_hash()
    # Since we are not actually building a wheel, we just return the default wheel name.
    # This is a bit of a hack, but it's the easiest way to hook into the build process.
    return Path(wheel_name).name


def _write_commit_hash():
    """Get the git commit hash and write it to a file."""
    project_root = Path(__file__).parent
    target_file = project_root / "image_periscope" / "COMMIT_HASH"

    # Only run if in a git repository
    if not (project_root / ".git").exists():
        if target_file.exists():
            target_file.unlink() # remove stale file
        return

    try:
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.STDOUT,
            cwd=project_root
        ).strip().decode("utf-8")

        target_file.write_text(commit_hash + "\n")
        print(f"Wrote commit hash {commit_hash} to {target_file}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Could not get commit hash: {e}")
        if target_file.exists():
            target_file.unlink()
