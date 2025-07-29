import subprocess
import sys
import textwrap
import typer

from pathlib import Path

def new(project_name: str):


    """
    Create a new Wyrmx project.
    """


    def createProjectFolder(projectName: str):
        projectPath = Path(projectName)

        try:
            projectPath.mkdir(parents=True, exist_ok=False)
            typer.echo(f"Created project folder: {projectPath.resolve()} ✅")
        except FileExistsError:
            typer.echo(f"Error: Folder '{projectName}' already exists.")


    
    def createReadmeMarkdown(projectName: str):

        try:
            readmeMarkdown = Path(projectName)/"README.md"
            readmeMarkdown.write_text("")

            typer.echo(f"Created README default documentation ✅")
        except FileExistsError:
            typer.echo(f"Error: File '{str(readmeMarkdown)}' already exists.")
    

    def createAlembicFiles(projectName: str):

        def createAlembicIni(projectName: str):

            try:
                alembicIni = Path(projectName)/"alembic.ini"

                template = (
                    f"[alembic]\n"
                    f"script_location = src/migrations\n"
                    f"sqlalchemy.url = postgresql://user:pass@host/db # or read from .env \n"
                )

                alembicIni.write_text(template)

                typer.echo(f"Created Alembic ini file ✅")
            except FileExistsError:
                typer.echo(f"Error: File '{str(alembicIni)}' already exists.")

        

        def createAlembicEnv(projectName: str): 

            try: 
                alembicEnv = Path(projectName)/"env.py"
                alembicEnv.write_text("")

                typer.echo(f"Created Alembic env file ✅")
            
            except FileExistsError:
                typer.echo(f"Error: File '{str(alembicEnv)}' already exists.")
        
        createAlembicIni(projectName)
        createAlembicEnv(projectName)



    def createVirtualEnvironment(projectName: str):

        typer.echo(f"Initializing Poetry & pyproject.toml and creating virtual environment...", )
        projectPath = Path(projectName)

        try :

            commands = [
                ["poetry", "init", "--no-interaction"],
                ["poetry", "config", "virtualenvs.in-project", "true"],
                ["poetry", "install", "--no-root"],
            ]

            for command in commands: subprocess.run(
                command,
                cwd=str(projectPath),
                check=True

            )
        
        except FileNotFoundError:

            typer.echo(
                "Error: Poetry is not installed.\n"
                "Install it with: `pip install poetry` or follow https://python-poetry.org/docs/#installation"
            )
            raise typer.Exit(1)


    def initDependencies(projectName: str):
        typer.echo(f"Installing initial dependencies...", )

        projectPath = Path(projectName)

        try:

            for initialDependency in ["fastapi", "uvicorn", "wyrmx-core", "alembic"]: subprocess.run(
                ["poetry", "add", initialDependency],
                cwd=str(projectPath),
                check=True
            )

        except FileNotFoundError:

            typer.echo(
                "Error: Poetry is not installed.\n"
                "Install it with: `pip install poetry` or follow https://python-poetry.org/docs/#installation"
            )
            raise typer.Exit(1)
        

    
    def updateGitignore(projectName: str):
        gitignorePath = Path(projectName)/".gitignore"
        gitignorePath.write_text(
            textwrap.dedent("""\
                # Python virtual environment
                .venv/
                bin/
                include/
                lib/
                lib64/
                local/
                pyvenv.cfg
                .env

                # Bytecode cache
                **/__pycache__/**
            """)
        )
    

    def initSourceCode(projectName: str):
        

        def createSrc():
            srcPath = Path(projectName)/"src"
            srcPath.mkdir(parents=True, exist_ok=True)
        
            for folder in ["controllers", "services", "models"] : (srcPath/folder).mkdir(parents=True, exist_ok=True)
        
        def createAppModule():
            appModulePath = Path(projectName)/"src"/"app_module.py"
            appModulePath.write_text("")

        
        def createMain():
            mainPath = Path(projectName)/"src"/"main.py"

            template = (

                f"from wyrmx_core import WyrmxAPP\n"
                f"from . import app_module\n\n"
                f"app = WyrmxAPP()"
            )

            mainPath.write_text(template)
        
        def createEnv():

            for file in [".env", ".env.example"] : 
                path = Path(projectName) / file
                path.write_text("")
        

        createSrc()
        createAppModule()
        createMain()
        createEnv()

        
            
    def initGit(projectName: str):

        subprocess.run(
            ["git", "init"],
            cwd=str(Path(projectName)),
            check=True
        )
        



    projectName: str = project_name


    typer.echo(f"Initializing Wyrmx project: {projectName}")

    createProjectFolder(projectName)
    createReadmeMarkdown(projectName)
    createAlembicFiles(projectName)
    createVirtualEnvironment(projectName)
    initDependencies(projectName)
    updateGitignore(projectName)
    initSourceCode(projectName)
    initGit(projectName)