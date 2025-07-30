from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()

RUNTIMES = {
    "node": {
        "default_version": "18",
        "default_workdir": "/app",
        "copy_files": ["package.json", "package-lock.json"],
        "install_cmd": "npm install",
        "build_cmd": "npm run build",
        "start_cmd": "npm start",
        "default_ports": ["3000"],
        "multi_stage_base_variants": ["alpine", "slim", "full"]
    },
    "python": {
        "default_version": "3.12",
        "default_workdir": "/app",
        "copy_files": ["requirements.txt"],
        "install_cmd": "pip install -r requirements.txt",
        "build_cmd": "",
        "start_cmd": "python app.py",
        "default_ports": ["8000"],
        "multi_stage_base_variants": ["alpine", "slim", "full"]
    },
    "golang": {
        "default_version": "1.21",
        "default_workdir": "/app",
        "copy_files": ["go.mod", "go.sum"],
        "install_cmd": "go mod download",
        "build_cmd": "go build -o main .",
        "start_cmd": "./main",
        "default_ports": ["8080"],
        "multi_stage_base_variants": ["alpine", "buster", "bullseye"]
    },
    "java": {
        "default_version": "17",
        "default_workdir": "/app",
        "copy_files": ["pom.xml"],
        "install_cmd": "mvn install",
        "build_cmd": "mvn package",
        "start_cmd": "java -jar target/*.jar",
        "default_ports": ["8080"],
        "multi_stage_base_variants": ["openjdk"]
    },
    "ruby": {
        "default_version": "3.2",
        "default_workdir": "/app",
        "copy_files": ["Gemfile", "Gemfile.lock"],
        "install_cmd": "bundle install",
        "build_cmd": "",
        "start_cmd": "ruby app.rb",
        "default_ports": ["4567"],
        "multi_stage_base_variants": ["alpine", "buster"]
    },
    "php": {
        "default_version": "8.2",
        "default_workdir": "/var/www/html",
        "copy_files": ["composer.json", "composer.lock"],
        "install_cmd": "composer install",
        "build_cmd": "",
        "start_cmd": "php -S 0.0.0.0:8000 -t .",
        "default_ports": ["8000"],
        "multi_stage_base_variants": ["alpine", "buster"]
    },
    "dotnet": {
        "default_version": "7.0",
        "default_workdir": "/app",
        "copy_files": ["*.csproj"],
        "install_cmd": "dotnet restore",
        "build_cmd": "dotnet publish -c Release -o out",
        "start_cmd": "dotnet out/YourApp.dll",
        "default_ports": ["5000"],
        "multi_stage_base_variants": ["alpine", "buster", "slim"]
    }
}

def add_copy_lines(files):
    if not files:
        return []
    elif len(files) == 1:
        return [f"COPY {files[0]} ./"]
    else:
        return [f"COPY {' '.join(files)} ./"]

def create_dockerfile_interactive():
    console.print(Text("🚀 Welcome to DockWatch Dockerfile Creator!", style="bold green"))
    console.print(Text("Let's create your Dockerfile step by step.\n", style="bold"))

    multi_stage = Confirm.ask("Do you want to create a multi-stage Dockerfile?", default=False)

    runtime = Prompt.ask(
        "Choose your runtime",
        choices=list(RUNTIMES.keys()),
        default="node"
    )
    runtime_info = RUNTIMES[runtime]

    version = Prompt.ask(f"Enter {runtime} version", default=runtime_info["default_version"])

    workdir = Prompt.ask("Working directory inside container", default=runtime_info["default_workdir"])

    copy_files_input = Prompt.ask(
        f"Files to COPY (comma-separated) [default: {', '.join(runtime_info['copy_files'])}]",
        default=", ".join(runtime_info["copy_files"])
    )
    copy_files = [f.strip() for f in copy_files_input.split(",") if f.strip()]

    install_cmd = Prompt.ask("Command to install dependencies", default=runtime_info["install_cmd"])

    if multi_stage:
        base_variant = Prompt.ask(
            "Base image variant",
            choices=runtime_info.get("multi_stage_base_variants", ["alpine", "slim", "full"]),
            default="alpine"
        )

        if runtime in ["java", "dotnet"] and base_variant == "alpine":
            build_image = f"{runtime}:{version}"
        else:
            build_image = f"{runtime}:{version}-{base_variant}"

        if base_variant == "alpine" and runtime not in ["java", "dotnet"]:
            runtime_image = f"{runtime}:{version}-slim"
        else:
            runtime_image = build_image

        build_cmd = Prompt.ask("Build command (leave empty if none)", default=runtime_info["build_cmd"])
        start_cmd = Prompt.ask("Start command", default=runtime_info["start_cmd"])

        ports_input = Prompt.ask(
            "Expose port(s) (comma separated)",
            default=", ".join(runtime_info["default_ports"])
        )
        ports = [p.strip() for p in ports_input.split(",") if p.strip()]

        dockerfile_lines = [
            f"# Build stage",
            f"FROM {build_image} AS build",
            f"WORKDIR {workdir}"
        ]
        dockerfile_lines += add_copy_lines(copy_files)
        dockerfile_lines.append(f"RUN {install_cmd}")
        if build_cmd:
            dockerfile_lines.append(f"RUN {build_cmd}")
        dockerfile_lines.append("")
        dockerfile_lines.append(f"# Final stage")
        dockerfile_lines.append(f"FROM {runtime_image}")
        dockerfile_lines.append(f"WORKDIR {workdir}")
        dockerfile_lines.append(f"COPY --from=build {workdir} {workdir}")
        dockerfile_lines.append(f"EXPOSE {' '.join(ports)}")
        dockerfile_lines.append(
            f'CMD ["{start_cmd.split()[0]}"' + "".join(f', "{arg}"' for arg in start_cmd.split()[1:]) + "]"
        )

    else:
        base_image = f"{runtime}:{version}"
        start_cmd = Prompt.ask("Start command", default=runtime_info["start_cmd"])

        ports_input = Prompt.ask(
            "Expose port(s) (comma separated)",
            default=", ".join(runtime_info["default_ports"])
        )
        ports = [p.strip() for p in ports_input.split(",") if p.strip()]

        dockerfile_lines = [
            f"FROM {base_image}",
            f"WORKDIR {workdir}"
        ]
        dockerfile_lines += add_copy_lines(copy_files)
        dockerfile_lines.append(f"RUN {install_cmd}")
        dockerfile_lines.append(f"EXPOSE {' '.join(ports)}")
        dockerfile_lines.append(
            f'CMD ["{start_cmd.split()[0]}"' + "".join(f', "{arg}"' for arg in start_cmd.split()[1:]) + "]"
        )

    try:
        with open("Dockerfile", "w") as f:
            f.write("\n".join(dockerfile_lines) + "\n")
    except Exception as e:
        console.print(Text(f"❌ Failed to write Dockerfile: {e}", style="bold red"))
        return

    console.print(Text("\n✅ Dockerfile created successfully!", style="bold green"))
    console.print(Text("You can now build your Docker image with:\n", style="bold"))
    console.print(Text("    docker build -t your-image-name .\n", style="bold yellow"))