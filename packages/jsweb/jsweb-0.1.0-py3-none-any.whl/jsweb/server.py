import threading
from wsgiref.simple_server import make_server
import socket
import time  # For potential delays during shutdown


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def run(app, host=None, port=8000):
    if host is None:
        host = "127.0.0.1"

    # Display local & LAN info
    if host == "0.0.0.0":
        local_ip = get_local_ip()
        print("🚀 JsWeb server running on:")
        print(f"   • http://localhost:{port}")
        print(f"   • http://{local_ip}:{port}  (LAN access)")
    else:
        print(f"🚀 JsWeb server running on http://{host}:{port}")
    print("⏹ Press Ctrl+C to stop the server")

    # Start server
    try:
        httpd = make_server(host, port, app)
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)  # Important: Daemon thread
        server_thread.start()

        print("✅ Server started successfully.")

        while True:  # Keep the main thread alive until interrupted
            time.sleep(1)  # Short sleep to prevent busy-waiting

    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"\n❌ Error: Port {port} is already in use. Please try a different port.")
        else:
            print(f"\n❌ An unexpected error occurred: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Stopping JsWeb server...")
    finally:
        if 'httpd' in locals():  # Ensure httpd exists before shutting down
            print("   • Shutting down the server...")
            httpd.shutdown()
            print("   • Waiting for the server thread to finish...")
        if 'server_thread' in locals() and server_thread.is_alive():
            server_thread.join()
        print("✅ Server stopped successfully.")
