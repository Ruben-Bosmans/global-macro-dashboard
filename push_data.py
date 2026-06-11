import subprocess
import os

CODE_FILES = [
    "app.py",
    "compass.py",
    "process.py",
    "run_all.py",
    "push_data.py",
]

def push():
    print("\n  Pushing updated files to GitHub...")

    commands = [
        (["git", "add"] + CODE_FILES,             "Staging code files"),
        (["git", "add", "-f", "data/processed/"], "Staging data files"),
        (["git", "commit", "-m", "Automated update"], "Committing"),
        (["git", "push"],                          "Pushing to GitHub"),
    ]

    for cmd, label in commands:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
        if result.returncode != 0:
            output = result.stdout + result.stderr
            if "nothing to commit" in output or "nothing added" in output:
                print("  No changes to push — everything is up to date.")
                return
            print(f"  ✗ {label} failed: {output[:200]}")
            return

    print("  ✓ GitHub updated successfully.")

if __name__ == "__main__":
    push()