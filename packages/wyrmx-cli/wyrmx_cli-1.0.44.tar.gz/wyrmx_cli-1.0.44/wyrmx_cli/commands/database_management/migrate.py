from pathlib import Path
import subprocess


def migrate(name: str): 

    """
        Apply all pending database migrations.
    """
    
    subprocess.run(
        ["alembic", "upgrade","head"],
        cwd=str(Path().cwd()),
        check=True
    )