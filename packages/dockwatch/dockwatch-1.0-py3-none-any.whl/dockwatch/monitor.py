import time
import threading
import docker
from rich.console import Console
from rich.text import Text
from dockwatch.analyzer import analyze_logs, analyze_startup_error

console = Console()
client = docker.from_env()
stop_event = threading.Event()

created_since = {}

def monitor_single_container(name, show_logs, poll_interval=3, created_timeout=5):
    last_status = None
    printed_created_error = False

    console.print(Text(f"🛡️ Starting monitoring for container: {name}", style="bold blue"))

    while not stop_event.is_set():
        try:
            container = client.containers.get(name)
            current_status = container.status

            if last_status != current_status:
                last_status = current_status

                console.print(
                    Text(f"📦 Container ", style="bold white") +
                    Text(name, style="bold yellow") +
                    Text(" status updated: ", style="bold white") +
                    Text(current_status.upper(), style="bold magenta")
                )

                if current_status == "exited":
                    exit_code = container.attrs["State"]["ExitCode"]
                    if exit_code == 0:
                        console.print(
                            Text("✅ Container ", style="green") +
                            Text(name, style="bold yellow") +
                            Text(" exited normally with code 0", style="white")
                        )
                    else:
                        console.print(
                            Text("💥 Crash detected: ", style="bold red") +
                            Text(name, style="bold yellow") +
                            Text(f" exited with code {exit_code}", style="bold white")
                        )
                        if show_logs:
                            analyze_logs(container)

                elif current_status == "created":
                    created_since[name] = time.time()
                    printed_created_error = False

            if current_status == "created":
                start_time = created_since.get(name)
                if start_time and time.time() - start_time > created_timeout and not printed_created_error:
                    console.print(
                        Text("🚫 Container ", style="bold red") +
                        Text(name, style="bold yellow") +
                        Text(" is stuck in CREATED state.", style="white")
                    )

                    error_msg = container.attrs["State"].get("Error")
                    analyze_startup_error(error_msg, name)

                    printed_created_error = True

        except docker.errors.NotFound:
            console.print(Text(f"⏳ Waiting for container: {name} (not found)", style="dim"))
            last_status = None
            created_since.pop(name, None)
            printed_created_error = False

        except Exception as e:
            console.print(Text(f"⚠️ Error monitoring {name}: {e}", style="bold red"))

        time.sleep(poll_interval)

def monitor_containers_threaded(container_names, show_logs):
    threads = []
    for name in container_names:
        thread = threading.Thread(target=monitor_single_container, args=(name, show_logs, ), daemon=True)
        thread.start()
        threads.append(thread)

    console.print(
        Text("🛡️  Monitoring ", style="bold green") +
        Text(str(len(container_names)), style="bold yellow") +
        Text(" containers: ", style="bold green") +
        Text(", ".join(container_names), style="bold yellow")
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print(Text("\n👋 Stopping DockWatch monitors. Goodbye!", style="bold red"))
        stop_event.set()
        for thread in threads:
            thread.join()
