from importlib.resources import files
from pathlib import Path
import typer


app = typer.Typer(
    pretty_exceptions_show_locals=False,
    help="A CLI tool to help manage Nanda Arch projects."
)


def prompt_with_default(prompt: str, default: str) -> str:
    """Prompts the user for input, offering a default value."""
    val = typer.prompt(prompt, default=default)
    return val.strip()


def create_from_template(template_name: str, target_path: Path, context: dict = None):
    """
    Creates a file from a template, substituting variables from the context.
    """
    if context is None:
        context = {}

    try:
        # O nome do seu pacote parece ser 'nanda_arch', não 'nanda_arch'.
        # Se o nome do pacote no seu pyproject.toml for diferente, ajuste aqui.
        template_file = files('nanda_arch.templates').joinpath(f'{template_name}.template')
        content = template_file.read_text(encoding='utf-8')
    except (FileNotFoundError, ModuleNotFoundError):
        typer.secho(f"Error: Template '{template_name}.template' not found.", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Substitui os placeholders no conteúdo do template
    for key, value in context.items():
        content = content.replace(f"{{{{ {key} }}}}", str(value))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding='utf-8')
    typer.secho(f" ✓ Created: {target_path.relative_to(Path.cwd())}", fg=typer.colors.GREEN)


@app.command()
def startproject():
    """
    Creates the basic structure for a new Nanda Arch project.
    """
    path_input = prompt_with_default("Where should the project be created?", default="./")
    root_path = Path(path_input).expanduser().resolve()
    project_name = root_path.name

    if path_input.strip() in ("", "./", "."):
        typer.echo(f"🚀 Using current directory as project root: '{project_name}'")
    else:
        typer.echo(f"🚀 Project name will be: '{project_name}'")

    try:
        root_path.mkdir(parents=True, exist_ok=True)
        typer.echo(f"Project directory prepared at: '{root_path}'")

        # --- Lógica de Criação de Arquivos Centralizada ---
        system_dir = root_path / 'system'
        context = {'project_name': project_name}

        # Dicionário que mapeia o nome do template ao seu destino e contexto
        files_to_create = {
            # Arquivos na raiz do projeto
            'main': (root_path / 'main.py', {}),
            'env': (root_path / '.env', {}),
            'gitignore': (root_path / '.gitignore', {}),

            # Arquivos no diretório /system
            'core': (system_dir / 'core.py', context),
            'settings': (system_dir / 'settings.py', context),
            'security': (system_dir / 'security.py', context),
            '__init__': (system_dir / '__init__.py', {})
        }

        # Itera sobre o dicionário e cria cada arquivo
        for template_name, (target_path, ctx) in files_to_create.items():
            create_from_template(
                template_name=template_name,
                target_path=target_path,
                context=ctx or context  # Usa o contexto específico ou o geral
            )

    except Exception as e:
        typer.secho(f"❌ Fatal error while creating the project: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"\n✅ Project '{project_name}' initialized successfully!", fg=typer.colors.BRIGHT_GREEN, bold=True)
    typer.echo("Next steps:")
    typer.echo(f"  1. Change into the project directory: cd {root_path}")
    typer.echo("  2. Review your .env file and set your JWT_SECRET_KEY.")
    typer.echo("  3. Set up your environment and install dependencies.")


@app.command()
def startapp(
    app_name: str = typer.Argument(
        ...,
        help="The name of the application to create (e.g., 'users', 'products')."
    )
):
    """
    Creates a new Nanda Arch app within the 'apps' directory.
    """
    project_root = Path.cwd()
    settings_file = project_root / 'system' / 'settings.py'
    if not settings_file.is_file():
        typer.secho(
            "❌ Error: This command must be run from the root of a Nanda Arch project.",
            fg=typer.colors.RED
        )
        raise typer.Exit(1)

    app_path = project_root / 'apps' / app_name

    if app_path.exists():
        typer.secho(
            f"❌ Error: App '{app_name}' already exists in '{app_path.relative_to(project_root)}'.",
            fg=typer.colors.RED
        )
        raise typer.Exit(1)

    typer.echo(f"🚀 Creating app '{app_name}'...")

    try:
        context = {'name': app_name}

        files_to_create = {
            'config': 'config.py',
            'router': 'router.py',
            'models': 'models.py',
            '__init__': '__init__.template'
        }

        for template_name, file_name in files_to_create.items():
            # Renomeei os templates de app para não terem o prefixo 'app_'
            # Ex: 'config.template', 'router.template', etc.
            create_from_template(
                template_name=template_name,
                target_path=app_path / file_name,
                context=context
            )

    except Exception as e:
        typer.secho(f"❌ Fatal error while creating the app: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"\n✅ App '{app_name}' created successfully!", fg=typer.colors.BRIGHT_GREEN, bold=True)
    typer.echo("Next steps:")
    typer.secho(
        f"  1. Add 'apps.{app_name}' to the INSTALLED_APPS list in your 'system/settings.py' file.",
        fg=typer.colors.YELLOW
    )


if __name__ == "__main__":
    app()
