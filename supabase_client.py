import os
import socket
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def _check_connectivity():
    """Return True if the Supabase host is reachable."""
    try:
        host = SUPABASE_URL.replace("https://", "").replace("http://", "").rstrip("/")
        socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        return True
    except (socket.gaierror, OSError):
        return False


SUPABASE_AVAILABLE = _check_connectivity()

if SUPABASE_AVAILABLE:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Admin client for operations that require service role (e.g. auto-confirm users)
    if SUPABASE_SERVICE_ROLE_KEY:
        supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    else:
        supabase_admin = None  # type: ignore[assignment]
else:
    supabase = None  # type: ignore[assignment]
    supabase_admin = None  # type: ignore[assignment]
