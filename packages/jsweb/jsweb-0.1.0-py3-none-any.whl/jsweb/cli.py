# jsweb/cli.py
import argparse
import os
import socket
import sys

from jsweb.server import run
from jsweb import __VERSION__

JSWEB_DIR = os.path.dirname(__file__)
TEMPLATE_FILE = os.path.join(JSWEB_DIR, "templates", "starter_template.html")
STATIC_FILE = os.path.join(JSWEB_DIR, "static", "global.css")


def create_project(name):
    os.makedirs(name, exist_ok=True)
    os.makedirs(os.path.join(name, "templates"), exist_ok=True)
    os.makedirs(os.path.join(name, "static"), exist_ok=True)

    # Copy template
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        starter_html = f.read()
    with open(os.path.join(name, "templates", "welcome.html"), "w", encoding="utf-8") as f:
        f.write(starter_html)

    # Copy CSS
    with open(STATIC_FILE, "r", encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(name, "static", "global.css"), "w", encoding="utf-8") as f:
        f.write(css)

    # Create app.py
    with open(os.path.join(name, "app.py"), "w", encoding="utf-8") as f:
        f.write(f"""
from jsweb import JsWebApp, run, render, __VERSION__, html
app = JsWebApp()

@app.route("/")
def home(req):
    return render("welcome.html", {{"name": "JsWeb", "version": __VERSION__}})

if __name__ == "__main__":
    run(app)
""")

    print(f"✔️ Project '{name}' created successfully in the '{os.path.abspath(name)}' directory.")
    print(f"👉 To run the project: cd {name} && jsweb run")


def check_port(host, port):
    """Checks if a port is available on the given host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
        return True
    except OSError:
        return False


def cli():
    parser = argparse.ArgumentParser(prog="jsweb", description="JsWeb CLI - A lightweight Python web framework.")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__VERSION__}"  # Add version
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    run_cmd = sub.add_parser("run", help="Run the JsWeb application in the current directory.")
    run_cmd.add_argument("--host", default="127.0.0.1", help="Host address to bind to (default: 127.0.0.1)")
    run_cmd.add_argument("--port", type=int, default=8000, help="Port number to listen on (default: 8000)")

    new_cmd = sub.add_parser("new", help="Create a new JsWeb project with a basic structure.")
    new_cmd.add_argument("name", help="The name of the new project")

    args = parser.parse_args()

    if args.command == "run":
        if not os.path.exists("app.py"):
            print("❌ Error: Could not find 'app.py'. Ensure you are in a JsWeb project directory.")
            return
        if not check_port(args.host, args.port):
            print(f"❌ Error: Port {args.port} is already in use. Please specify a different port using --port.")
            return
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("app", "app.py")
            if spec is None or spec.loader is None:
                raise ImportError("Could not load app.py")

            app_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(app_module)

            if not hasattr(app_module, "app"):
                raise AttributeError("Application instance 'app' not found in app.py")
            run(app_module.app, host=args.host, port=args.port)

        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user.")
        except ImportError as e:
            print(f"❌ Error: Could not import application.  Check your app.py file. Details: {e}")
        except AttributeError as e:
            print(f"❌ Error: Invalid application file. Ensure 'app.py' defines a JsWebApp instance named 'app'. Details: {e}")
        except Exception as e:
            print(f"❌ Error: Failed to run app.  Details: {e}")

    elif args.command == "new":
        create_project(args.name)

    else:
        parser.print_help()
