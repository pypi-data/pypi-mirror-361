import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import questionary

from src.vue.boiler_playes import app_vue_code, three_canvas_code

app = typer.Typer(help="🚀 Modern CLI Project Scaffolder")
console = Console()

# Template configurations
TEMPLATES = {
    "vue": {
        "name": "Vue 3",
        "description": "Vue 3 with Composition API",
        "command": ["npm", "create", "vue@latest"],
        "package_manager": "npm"
    },
    "nuxt": {
        "name": "Nuxt 3",
        "description": "Nuxt 3 with SSR/SSG support",
        "command": ["npm", "create", "nuxt@latest"],
        "package_manager": "npm"
    },
    "react": {
        "name": "React 18",
        "description": "React 18 with Vite",
        "command": ["npm", "create", "vite@latest"],
        "package_manager": "npm"
    }
}

# Dependencies to install
DEPENDENCIES = ["tailwindcss", "gsap", "three"]
DEV_DEPENDENCIES = ["@types/three"] # TypeScript types for Three.js


def display_welcome():
    """Display welcome message and available templates"""
    console.print()
    # Large, colorful 'VI-CLI' title
    console.print("[bold magenta]██╗   ██╗[/bold magenta] [bold cyan]██╗[/bold cyan]          [bold yellow]██████╗ [/bold yellow] [bold green]██╗[/bold green]      [bold red]██╗[/bold red]")
    console.print("[bold magenta]██║   ██║[/bold magenta] [bold cyan]██║[/bold cyan]          [bold yellow]██╔═══╝ [/bold yellow] [bold green]██║[/bold green]      [bold red]██║[/bold red]")
    console.print("[bold magenta]██║   ██║[/bold magenta] [bold cyan]██║[/bold cyan] ████████ [bold yellow]██║     [/bold yellow] [bold green]██║[/bold green]      [bold red]██║[/bold red]")
    console.print("[bold magenta]╚██╗ ██╔╝[/bold magenta] [bold cyan]██║[/bold cyan]          [bold yellow]██║     [/bold yellow] [bold green]██║[/bold green]      [bold red]██║[/bold red]")
    console.print("[bold magenta] ╚████╔╝[/bold magenta]  [bold cyan]██║[/bold cyan]          [bold yellow]██████╗ [/bold yellow] [bold green]███████╗[/bold green] [bold red]██║[/bold red]")
    console.print("[bold magenta]  ╚═══╝[/bold magenta]   [bold cyan]╚═╝[/bold cyan]          [bold yellow]╚═════╝[/bold yellow]  [bold green]╚══════╝[/bold green] [bold red]╚═╝[/bold red]")
    console.print()
    console.print("[bold white]Life is short code fast !!!![/bold white]")
    console.print()
    
    # List templates as a numbered list for selection
    console.print("[bold magenta]Choose a template to scaffold your project:[/bold magenta]\n")
    for idx, (key, template) in enumerate(TEMPLATES.items(), 1):
        console.print(f"  [bold cyan]{idx}[/bold cyan]. [bold]{template['name']}[/bold] - [dim]{template['description']}[/dim]")
    console.print()


def create_project(template_key: str, project_name: str, destination: Path) -> bool:
    """Create a new project using the official scaffolding tools"""
    try:
        template_config = TEMPLATES[template_key]
        if template_key == "react":
            # For React, use: npm create vite@latest <project_name> -- --template react
            cmd = template_config["command"] + [str(destination.name), "--", "--template", "react"]
        else:
            # For Vue/Nuxt, use only the directory name
            cmd = template_config["command"] + [str(destination.name)]
        cwd = str(destination.parent)

        console.print(f"[blue]Creating {template_config['name']} project...[/blue]")



        # Use shell=True on Windows so npm.cmd is found
        use_shell = sys.platform.startswith("win")
        # Set FORCE_COLOR=1 to force colored output
        env = os.environ.copy()
        env["FORCE_COLOR"] = "1"
        # Run interactively so user can answer prompts
        result = subprocess.run(cmd, cwd=cwd, shell=use_shell, env=env)

        if result.returncode != 0:
            console.print(f"[red]Error creating project: process exited with code {result.returncode}")
            return False

        return True

    except Exception as e:
        console.print(f"[red]Error creating project:[/red] {e}")
        return False


def install_dependencies(project_dir: Path) -> bool:
    """Install additional npm dependencies in the project directory"""
    try:
        os.chdir(project_dir)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Install additional dependencies
            task = progress.add_task("Installing additional dependencies...", total=None)

            # Detect if this is a Vue or React project (by vite.config.ts/js and package.json)
            is_vue = False
            is_react = False
            pkg_json = project_dir / "package.json"
            if pkg_json.exists():
                try:
                    import json
                    pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
                    deps = pkg.get("dependencies", {})
                    dev_deps = pkg.get("devDependencies", {})
                    if "vue" in deps or "vue" in dev_deps:
                        is_vue = True
                    if "react" in deps or "react" in dev_deps:
                        is_react = True
                except Exception:
                    pass

            # For Vue/React, add @tailwindcss/vite
            extra_tailwind = ["@tailwindcss/vite"] if is_vue or is_react else []

            use_shell = sys.platform.startswith("win")
            env = os.environ.copy()
            env["FORCE_COLOR"] = "1"
            cmd = ["npm", "install"] + DEPENDENCIES + extra_tailwind
            result = subprocess.run(cmd, capture_output=True, text=True, shell=use_shell, env=env)
            if result.returncode != 0:
                console.print(f"[red]Error installing dependencies:[/red] {result.stderr}")
                return False

            # Install dev dependencies
            progress.update(task, description="Installing dev dependencies...")
            cmd = ["npm", "install", "--save-dev"] + DEV_DEPENDENCIES
            result = subprocess.run(cmd, capture_output=True, text=True, shell=use_shell, env=env)
            if result.returncode != 0:
                console.print(f"[yellow]Warning:[/yellow] Could not install dev dependencies: {result.stderr}")

            # Patch vite.config.js or vite.config.ts for Vue or React
            if is_vue or is_react:
                for vite_name in ["vite.config.ts", "vite.config.js"]:
                    vite_config = project_dir / vite_name
                    if vite_config.exists():
                        try:
                            content = vite_config.read_text(encoding="utf-8")
                            # Add import if not present
                            if "import tailwindcss from '@tailwindcss/vite'" not in content:
                                # Place after last import
                                lines = content.splitlines()
                                last_import = 0
                                for i, line in enumerate(lines):
                                    if line.strip().startswith("import"):
                                        last_import = i + 1
                                lines.insert(last_import, "import tailwindcss from '@tailwindcss/vite'")
                                content = "\n".join(lines)
                            # Add tailwindcss() to plugins array if not present
                            import re
                            def add_tailwind_plugin(match):
                                plugins = match.group(1)
                                # If tailwindcss() already present, skip
                                if "tailwindcss()" in plugins:
                                    return match.group(0)
                                # Insert tailwindcss() after [
                                plugins_new = plugins.replace('[', '[\n    tailwindcss(),', 1)
                                return f"plugins: {plugins_new}"
                            content_new, n = re.subn(r"plugins:\s*(\[[^\]]*\])", add_tailwind_plugin, content, flags=re.DOTALL)
                            if n == 0:
                                content_new = content
                            vite_config.write_text(content_new, encoding="utf-8")
                        except Exception as e:
                            console.print(f"[yellow]Warning:[/yellow] Could not patch {vite_config}: {e}")

            # Patch nuxt.config.ts or nuxt.config.js for Nuxt
            is_nuxt = False
            pkg_json = project_dir / "package.json"
            if pkg_json.exists():
                try:
                    import json
                    pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
                    deps = pkg.get("dependencies", {})
                    dev_deps = pkg.get("devDependencies", {})
                    if "nuxt" in deps or "nuxt" in dev_deps:
                        is_nuxt = True
                except Exception:
                    pass
            if is_nuxt:
                import re
                for nuxt_name in ["nuxt.config.ts", "nuxt.config.js"]:
                    nuxt_config = project_dir / nuxt_name
                    if nuxt_config.exists():
                        try:
                            content = nuxt_config.read_text(encoding="utf-8")
                            # 1. Add import tailwindcss from "@tailwindcss/vite" if not present
                            if 'import tailwindcss from "@tailwindcss/vite"' not in content:
                                # Insert after last import
                                lines = content.splitlines()
                                last_import = 0
                                for i, line in enumerate(lines):
                                    if line.strip().startswith("import"):
                                        last_import = i + 1
                                lines.insert(last_import, 'import tailwindcss from "@tailwindcss/vite"')
                                content = "\n".join(lines)
                            # 2. Add css: ["~/assets/css/main.css"] to config if not present
                            if 'css:' not in content:
                                # Try to insert after defineNuxtConfig({
                                content = re.sub(r'(defineNuxtConfig\s*\(\s*{)', r"\1\n  css: ['~/assets/css/main.css'],", content)
                            elif '"~/assets/css/main.css"' not in content and "'~/assets/css/main.css'" not in content:
                                # Add to existing css array
                                content = re.sub(r'css:\s*\[([^\]]*)\]', r"css: [\1, '~/assets/css/main.css']", content)
                            # 3. Add tailwindcss() to vite.plugins if not present
                            def add_tailwind_plugin(match):
                                plugins = match.group(1)
                                if 'tailwindcss()' in plugins:
                                    return match.group(0)
                                plugins_new = plugins.replace('[', '[\n      tailwindcss(),', 1)
                                return f"plugins: {plugins_new}"
                            content, _ = re.subn(r'plugins:\s*(\[[^\]]*\])', add_tailwind_plugin, content, flags=re.DOTALL)
                            # If vite/plugins not present, add vite: { plugins: [tailwindcss()] } to config
                            if 'vite:' not in content:
                                content = re.sub(r'(defineNuxtConfig\s*\(\s*{)', r"\1\n  vite: { plugins: [tailwindcss()] },", content)
                            nuxt_config.write_text(content, encoding="utf-8")
                        except Exception as e:
                            console.print(f"[yellow]Warning:[/yellow] Could not patch {nuxt_config}: {e}")
                # Ensure assets/css/main.css exists and has Tailwind import
                main_css = project_dir / "assets" / "css" / "main.css"
                if not main_css.parent.exists():
                    try:
                        main_css.parent.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        console.print(f"[yellow]Warning:[/yellow] Could not create assets/css directory: {e}")
                try:
                    main_css.write_text("@import 'tailwindcss';\n", encoding="utf-8")
                except Exception as e:
                    console.print(f"[yellow]Warning:[/yellow] Could not write main.css: {e}")


            # Patch main CSS for Tailwind (Vue)
            if is_vue:
                css_candidates = list(project_dir.glob("src/**/*.*"))
                for css_file in css_candidates:
                    if css_file.suffix in {".css", ".scss", ".less", ".styl", ".postcss"}:
                        try:
                            css_content = css_file.read_text(encoding="utf-8")
                            if "@import 'tailwindcss'" not in css_content and '@import "tailwindcss"' not in css_content and '@import tailwindcss' not in css_content:
                                css_file.write_text(f"@import 'tailwindcss';\n" + css_content, encoding="utf-8")
                                break
                        except Exception as e:
                            console.print(f"[yellow]Warning:[/yellow] Could not patch {css_file}: {e}")

                # Use boilerplate from local 'vue' folder (as string literals) for Vue projects
                try:
                    # App.vue boilerplate
                    
                    # Write App.vue
                    app_vue = project_dir / "src" / "App.vue"
                    if app_vue.exists():
                        app_vue.write_text(app_vue_code, encoding="utf-8")
                    # Write ThreeCanvas.vue
                    components_dir = project_dir / "src" / "components"
                    components_dir.mkdir(parents=True, exist_ok=True)
                    three_canvas = components_dir / "ThreeCanvas.vue"
                    three_canvas.write_text(three_canvas_code, encoding="utf-8")
                    # Clear src/assets/base.css and main.css
                    assets_dir = project_dir / "src" / "assets"
                    for css_name in ["base.css", "main.css"]:
                        css_file = assets_dir / css_name
                        if css_file.exists():
                            if css_name == "main.css":
                                css_file.write_text("@import 'tailwindcss';\n", encoding="utf-8")
                            else:
                                css_file.write_text("", encoding="utf-8")
                except Exception as e:
                    console.print(f"[yellow]Warning:[/yellow] Could not clear Vue boilerplate: {e}")

            # For React: clear App.css, index.css, and replace App.jsx with minimal component
            if is_react:
                try:
                    src_dir = project_dir / "src"
                    # Clear App.css
                    app_css = src_dir / "App.css"
                    if app_css.exists():
                        app_css.write_text("", encoding="utf-8")
                    # Clear index.css
                    index_css = src_dir / "index.css"
                    if index_css.exists():
                        index_css.write_text("@import 'tailwindcss';", encoding="utf-8")
                    # Replace App.jsx with minimal React component
                    app_jsx = src_dir / "App.jsx"
                    if app_jsx.exists():
                        app_jsx.write_text(
                            "import React from 'react'\n\n"
                            "function App() {\n"
                            "  return (\n"
                            "    <div>\n"
                            "      <h1>Hello, React + Tailwind!</h1>\n"
                            "    </div>\n"
                            "  );\n"
                            "}\n\n"
                            "export default App\n",
                            encoding="utf-8"
                        )
                except Exception as e:
                    console.print(f"[yellow]Warning:[/yellow] Could not clear React boilerplate: {e}")

            progress.update(task, description="Additional dependencies installed!", completed=True)
        
        return True
        
    except Exception as e:
        console.print(f"[red]Error installing dependencies:[/red] {e}")
        return False


def check_requirements() -> bool:
    """Check if required tools are installed"""
    try:
        # On Windows, npm may be a .cmd or .exe, so use shell=True
        result = subprocess.run(
            "npm --version",
            capture_output=True,
            text=True,
            shell=True
        )
        print(result.stdout.strip())
        if 'error' in result.stdout.lower():
            raise FileNotFoundError("npm not found")
            
        return True 
    except Exception:
        console.print("[red]Error:[/red] npm is not installed or not in PATH")
        console.print("Please install Node.js and npm first: https://nodejs.org/")
        return False


def validate_project_name(name: str) -> bool:
    """Validate project name"""
    if not name:
        return False
    
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', ' ']
    if any(char in name for char in invalid_chars):
        return False
    
    # Check if it's a valid directory name
    try:
        Path(name)
        return True
    except (OSError, ValueError):
        return False


@app.command()
def create(
    template: Optional[str] = typer.Argument(None, help="Template to use (vue, nuxt, react)"),
    project_name: Optional[str] = typer.Argument(None, help="Name of the project"),
    destination: Optional[str] = typer.Option(None, "--dest", "-d", help="Destination directory")
):
    """Create a new project from template"""
    
    display_welcome()

    # Get template selection using questionary (arrow keys) FIRST
    template_keys = list(TEMPLATES.keys())
    if not template:
        choices = [
            questionary.Choice(
                title=f"{TEMPLATES[key]['name']} - {TEMPLATES[key]['description']}",
                value=key
            ) for key in template_keys
        ]
        try:
            template = questionary.select(
                "Select a template:",
                choices=choices,
                qmark="🚀",
                force_interactive=True
            ).ask()
        except TypeError:
            template = questionary.select(
                "Select a template:",
                choices=choices,
                qmark="🚀"
            ).ask()
        if not template:
            console.print("[red]No template selected. Exiting.[/red]")
            raise typer.Exit(1)

    # Now check requirements
    if not check_requirements():
        raise typer.Exit(1)

    if template not in TEMPLATES:
        console.print(f"[red]Error:[/red] Invalid template '{template}'")
        raise typer.Exit(1)

    # Get project name using questionary
    if not project_name:
        project_name = questionary.text("Enter project name:").ask()
        if not project_name:
            console.print("[red]No project name provided. Exiting.[/red]")
            raise typer.Exit(1)

    if not validate_project_name(project_name):
        console.print("[red]Error:[/red] Invalid project name")
        raise typer.Exit(1)

    # Determine destination
    if destination:
        dest_path = Path(destination) / str(project_name)
    else:
        dest_path = Path.cwd() / str(project_name)

    # Check if destination already exists
    if dest_path.exists():
        console.print(f"[red]Error:[/red] Directory '{dest_path}' already exists!")
        if not Confirm.ask("Do you want to overwrite it?"):
            console.print("Project creation cancelled.")
            raise typer.Exit(0)
        shutil.rmtree(dest_path)



    # Create project using official scaffolding tools
    if not create_project(template, project_name, dest_path):
        raise typer.Exit(1)

    # Install additional dependencies
    console.print(f"[blue]Installing additional dependencies in {dest_path}...[/blue]")
    if not install_dependencies(dest_path):
        console.print("[yellow]Warning:[/yellow] Project created but additional dependencies installation failed")
        console.print(f"You can manually install dependencies by running:")
        console.print(f"  cd {dest_path}")
        console.print(f"  npm install {' '.join(DEPENDENCIES)}")

    # Success message
    console.print()
    console.print(Panel.fit(
        f"[bold green]✅ Project '{project_name}' created successfully![/bold green]\n"
        f"[dim]Location: {dest_path}[/dim]",
        border_style="green"
    ))

    # Next steps
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  cd {project_name}")
    console.print("  npm run dev")
    console.print()


@app.command()
def list_templates():
    """List available templates"""
    display_welcome()
    
    for key, template in TEMPLATES.items():
        console.print(f"✅ [bold]{key}[/bold] - {template['name']}: {template['description']}")
        console.print(f"   Command: {' '.join(template['command'])}")
        console.print()


@app.command()
def version():
    """Show version information"""
    console.print("[bold blue]Modern CLI Project Scaffolder[/bold blue]")
    console.print("Version: 1.0.0")
    console.print("Dependencies: tailwindcss, gsap, three")


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    # If no subcommand is provided, run the create command interactively
    if ctx.invoked_subcommand is None:
        # Show welcome and run create interactively
        create(template=None, project_name=None, destination=None)

if __name__ == "__main__":
    app()