from pathlib import Path
import subprocess



def make_migration(migrationText: str):

    """
    Create a new database migration based on your current schemas.
    """

    subprocess.run(
        ["alembic", "revision","--autogenerate", "-m", f"'{migrationText}'"],
        cwd=str(Path().cwd()),
        check=True
    )
    