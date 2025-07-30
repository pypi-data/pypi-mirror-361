import argparse
from rich.console import Console
from rich.text import Text
from dockwatch.monitor import monitor_containers_threaded
from dockwatch.image_analyzer import analyze_image
from dockwatch.creator import create_dockerfile_interactive

console = Console()

def main():
    parser = argparse.ArgumentParser(prog="dockwatch", description="DockWatch CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    monitor_parser = subparsers.add_parser("monitor", help="Monitor Docker containers")
    monitor_parser.add_argument("containers", nargs="+", help="Container names to monitor")
    monitor_parser.add_argument("-l", "--show-logs", action="store_true", help="Show container logs on crash")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a local Docker image")
    analyze_parser.add_argument("image", help="Docker image name")

    subparsers.add_parser("create", help="Interactively create a multi-stage Dockerfile")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "monitor":
        container_list = ', '.join(args.containers)
        console.print()
        console.print(
            Text("📦 Monitoring started for containers: ", style="bold green") +
            Text(container_list, style="bold yellow")
        )
        console.print()
        monitor_containers_threaded(args.containers, show_logs=getattr(args, "show_logs", False))

    elif args.command == "analyze":
        console.print()
        console.print(Text(f"🔍 Analyzing Docker image: {args.image}", style="bold blue"))
        console.print()
        analyze_image(args.image)

    elif args.command == "create":
        console.print()
        create_dockerfile_interactive()
        console.print()

if __name__ == "__main__":
    main()
