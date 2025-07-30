import docker
from rich.console import Console
from rich.table import Table
from rich.text import Text

client = docker.from_env()
console = Console()

def analyze_image(image_name: str):
    try:
        image = client.images.get(image_name)
    except docker.errors.ImageNotFound:
        console.print(Text(f"❌ Image '{image_name}' not found locally. Please pull it first.", style="bold red"))
        return
    except Exception as e:
        console.print(Text(f"❌ Unexpected error accessing image: {e}", style="bold red"))
        return

    try:
        history = image.history()
    except Exception as e:
        console.print(Text(f"⚠️ Failed to retrieve image history: {e}", style="bold red"))
        return

    def format_size(bytes_):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_ < 1024:
                return f"{bytes_:.2f} {unit}"
            bytes_ /= 1024
        return f"{bytes_:.2f} TB"

    table = Table(title=f"🧱 Image Layer Breakdown: {image_name}", style="bold green")
    table.add_column("Layer #", style="cyan", justify="right")
    table.add_column("Command", style="magenta")
    table.add_column("Size", style="yellow", justify="right")

    total_size = 0
    large_layers = []
    apt_layers = []
    temp_file_layers = []
    copy_layers = []

    for idx, layer in enumerate(reversed(history), 1):
        cmd = (layer.get("CreatedBy") or "").strip()
        cmd_safe = Text(cmd[:50].replace("\t", " "))
        if len(cmd) > 50:
            cmd_safe.append("...")
        size = layer.get("Size", 0)
        total_size += size

        if size > 100 * 1024 * 1024:
            large_layers.append((idx, size, cmd))
        if "apt-get" in cmd and "clean" not in cmd:
            apt_layers.append(idx)
        if any(path in cmd for path in ["/tmp", "/var/cache", "/var/log"]):
            temp_file_layers.append(idx)
        if cmd.lower().startswith("copy") or cmd.lower().startswith("add"):
            copy_layers.append((idx, size))

        table.add_row(str(idx), cmd_safe, format_size(size))

    console.print(table)
    console.print(Text(f"📦 Total Image Size: {format_size(total_size)}", style="bold white"))

    tips = []

    if large_layers:
        tips.append("🚨 Large layers detected. Consider using multi-stage builds or minimizing base image.")

    if apt_layers:
        tips.append("💡 You use `apt-get` but forgot `apt-get clean`. This can free up APT cache space.")

    if temp_file_layers:
        tips.append("🧹 Consider deleting temp/cache/log files in those layers to save space.")

    if any(size > 50 * 1024 * 1024 for _, size in copy_layers):
        tips.append("📁 COPY/ADD layer is large. Use `.dockerignore` and avoid copying node_modules or build artifacts.")

    base_suggestions = get_image_suggestions(image_name)

    console.print()
    if tips:
        for tip in tips:
            console.print(Text(tip, style="cyan"))
    else:
        console.print(Text("✅ Image layers look efficient. No major optimizations suggested.", style="bold green"))

    if base_suggestions:
        console.print()
        console.print(Text("💡 Image Suggestions:", style="bold magenta"))
        for suggestion in base_suggestions:
            console.print(Text(f"• {suggestion}", style="bold yellow"))

    console.print()

def get_image_suggestions(image_name: str):
    """
    Provide suggestions based on common base image names.
    """
    suggestions = []
    name = image_name.lower()

    base = name.split(":")[0].split("@")[0]

    if any(x in base for x in ["ubuntu", "debian"]):
        suggestions.append("Consider using Alpine Linux (`alpine` tag) or slim variants to reduce image size.")
        suggestions.append("Use multi-stage builds to separate build and runtime dependencies.")
    elif "node" in base:
        suggestions.append("Consider using `node:alpine` or `node:slim` images for smaller size.")
        suggestions.append("Use `.dockerignore` to avoid copying unnecessary files.")
    elif "python" in base:
        suggestions.append("Use `python:slim` or `python:alpine` for a smaller footprint.")
        suggestions.append("Remove cache and temp files after package installation.")
    elif "golang" in base:
        suggestions.append("Use multi-stage builds to produce minimal final images.")
    elif "openjdk" in base or "java" in base:
        suggestions.append("Consider using Distroless Java images or Alpine OpenJDK for smaller size.")
    elif "mongo" in base or "mysql" in base or "postgres" in base:
        suggestions.append("Use official slim or minimal database images if available.")

    return suggestions
