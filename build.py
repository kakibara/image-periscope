import subprocess
from pathlib import Path


def _write_commit_hash():
    """Get the git commit hash and write it to a file."""
    project_root = Path(__file__).parent
    target_file = project_root / "image_periscope" / "COMMIT_HASH"

    # Only run if in a git repository
    if not (project_root / ".git").exists():
        if target_file.exists():
            target_file.unlink()  # remove stale file
        return

    try:
        commit_hash = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.STDOUT,
                cwd=project_root,
            )
            .strip()
            .decode("utf-8")
        )

        target_file.write_text(commit_hash + "\n")
        print(f"Wrote commit hash {commit_hash} to {target_file}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Could not get commit hash: {e}")
        if target_file.exists():
            target_file.unlink()


if __name__ == "__main__":
    _write_commit_hash()
