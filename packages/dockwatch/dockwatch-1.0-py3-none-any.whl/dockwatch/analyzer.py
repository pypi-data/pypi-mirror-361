from rich.console import Console
from rich.text import Text

console = Console()

EXIT_CODE_INFO = {
    0: ("✅ Container exited normally with code 0.", "green"),
    1: ("❌ General error (Exit code 1). Check application logs.", "red"),
    137: ("💥 Container was killed (SIGKILL / Exit code 137). Possibly out of memory or manually killed.", "red"),
    139: ("💥 Segmentation fault detected (Exit code 139). Check native code or memory access errors.", "red"),
    143: ("💡 Container terminated by SIGTERM (Exit code 143). Possibly graceful shutdown or docker stop.", "yellow"),
    126: ("❌ Command invoked cannot execute (Exit code 126). Check entrypoint or cmd.", "red"),
    127: ("❌ Command not found (Exit code 127). Check entrypoint or cmd.", "red"),
}

def analyze_logs(container):
    try:
        logs = container.logs(tail=50).decode("utf-8", errors="replace")
    except Exception as e:
        console.print(Text(f"⚠️ Failed to read logs for {container.name}: {e}", style="bold red"))
        return

    exit_code = container.attrs["State"].get("ExitCode", None)
    exit_msg, style = EXIT_CODE_INFO.get(exit_code, (f"❌ Container exited with code {exit_code}. Check logs for details.", "red"))

    console.print()
    console.print(
        Text("🧠 Crash Analysis for ", style="bold cyan") +
        Text(container.name, style="bold magenta") +
        Text(":", style="bold cyan")
    )
    console.print(Text(exit_msg, style=f"bold {style}"))

    console.print(
        Text("\n📜 Last 50 lines of container logs for ", style="bold white") + 
        Text(container.name, style="bold magenta") +
        Text(":", style="bold white")
    )
    console.print(Text(logs, style="white"))
    console.print()

def analyze_startup_error(error_msg: str, container_name: str):
    if not error_msg:
        console.print(Text("💡 Possible causes: port conflict, invalid mounts, or startup issues.", style="bold cyan"))
        return

    console.print(
        Text(f"🧠 Docker Startup Error for container ", style="bold magenta") +
        Text(container_name, style="bold yellow") +
        Text(":", style="bold magenta")
    )

    simplified_reason = None
    suggestion = None

    lower_msg = error_msg.lower()

    if "port is already allocated" in lower_msg or "bind for" in lower_msg:
        simplified_reason = "🔌 Port conflict: Another container or service is already using the requested port."
        suggestion = (
            "💡 Try using a different port in your run command:\n"
            "   docker run -p 8081:80 ...\n"
            "💡 Or free the port using:\n"
            "   sudo lsof -i :<port> && sudo kill -9 <PID>"
        )

    elif "mount" in lower_msg or "invalid" in lower_msg:
        simplified_reason = "📁 Mount error: One of the volumes may be incorrectly configured or missing."
        suggestion = "💡 Double-check your volume paths and use absolute paths where possible."

    elif "network" in lower_msg:
        simplified_reason = "🌐 Network setup failure: Docker couldn’t set up networking for the container."
        suggestion = "💡 Check your Docker network configuration or try restarting the Docker daemon."

    elif "permission denied" in lower_msg:
        simplified_reason = "🔐 Permission issue: Docker doesn’t have permission to access a resource."
        suggestion = "💡 Use sudo or ensure the Docker group has the right access."

    else:
        simplified_reason = "⚠️ Unknown startup issue occurred."
        suggestion = (
            "💡 Check the full error above or inspect the container manually using:\n"
            f"   docker inspect {container_name}"
        )

    console.print(Text(f"{simplified_reason}", style="bold red"))
    if suggestion:
        console.print(Text(suggestion, style="bold cyan"))
