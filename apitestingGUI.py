"""
API Testing GUI for Music Room Application - Refactored & Organized

ARCHITECTURE:
- Modular design with clear separation of concerns within single file
- Centralized cache management per user with proper lifecycle
- Thread-safe operations with proper locking mechanisms
- Separate client terminals for individual API call logging
- Clean code organization: Classes -> Helper Functions -> UI Components -> Main

FEATURES:
- Multi-user simulation with isolated state per client
- Real-time WebSocket communication with proper reconnection
- ETag-based image caching for bandwidth optimization
- Comprehensive API testing for rooms, songs, and playlists
- Individual client consoles for debugging API interactions
"""

import os
import requests
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
from dotenv import load_dotenv
import json
import threading
from PIL import Image
import io
import asyncio
import websockets

# === Load .env ===
load_dotenv()
# Hardcoded Firebase credentials for internal testing (NOT SAFE FOR PRODUCTION)
FIREBASE_API_KEY = "AIzaSyAQ3r-8kqsWOgBkWRKs-bApV33oeu-AICs"
FIREBASE_JSON = {
    "type": "service_account",
    "project_id": "hopekcc-2024-summer-intern-api",
    "private_key_id": "0149c446ecc6cf8fa39b4b4ddcd36de9a6d07151",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDTrfMNo4MqpAvn\n3tr0VkeD9WojYCac/Hcn1wfFhqS5g79Z/sh8MDbfaC+fU5l8Yf7e8zPqFkEAsVYX\nzXemCNR6yDm+5xitn76fwDjTOxRHsdFSlIpmMYz3hjKogwxYolUfqtH88mIKy3km\nTxpBBGk89EI1lVSp4TWmdz5aqH1sDrPBodVKUzeXoKE4QsqCuJtWrqghAnZHyD9l\n+xAXARN9I/iRHM1kryIWhuntGnH9mm7cS5N9BtesCnlfEi6tCVeb9YfygO2K01Fc\nMDOdpKvi0NydMiCZt0xG8W/caFLAFHL4xKs1f6XBcdaWkA0+PCQGnHWrQblNt6mN\nJDscXgCLAgMBAAECggEAEamvoME2li3HEot9cKrsX73wI9CHmEzWsnvWWayQ/SvZ\noSxJ1Vb+lSiv5JcItSDGMBtSByPhO6oQeX77D18oP7CKZPwKip5MPS9Abpu85viW\n81GStNFIpnTLsFTzCEhPWwuZZwZgmO7+hmxOUAOKtnvZNHhn7p7sp53GlbD+ejAf\nA+iCgRNigSqeaUkx9w8t23Q0Wrny7CtZ1bQGOKL1hY613qTpajUfLIsh73McOMPV\nQ8lxoMGljeNHxZRr8uek1nUlzthfYjTlyjlCdE1O1GB5thC9jf+geacLhjhE9IGN\nBW2igxHlnPYPZ/13jDWFisvR8csRrDQ9zAdij2gadQKBgQDs4bSA9cWUTxuHTsqI\nFmPkly9CNmMw/vfBSj6Qdw17/FI592U7FmW4cD6QTZMVJzrDgjY2OnAFtZbT+bzo\n5+bQKnsPtNNMdHwFo9Lp3jrE3zcevpfaiUg9jzzr43HlW1RQW9z7mUDx6wJL94ae\nnyOX1XGXCZnSnsqDb5C3Sy+HXQKBgQDkw4iROxGIAxDz/1mhs0Um+jLv5xjQqpJe\n7Y+zlJFAo800/6/wKVNjuEqfHTKZQZL/wEqGbFt+KjBAHwiRMeDilaR+74O4a41L\nnvE76VKtPMreTzcF9xljz8Qwlcw3eY8SxHqFABo/4xc14uYoBLOVGFza84g7uxQZ\nBLutQcKxBwKBgQDG/bvycYPu2J2ZhvjgZV65Er/icWnWKPnb6BCyrzAmrYoto8Po\nZSJCVBhahLBAHtpgjqwX1fNw+GCh5bNqPBVLXcRPJ2oxWdEts7dkOwlHhPP64cUT\nEiwbeo6E4mY1dAlaEDGNMeq6zt75DhCKg8kUrXtkk+4iXr5kt33sXD6rCQKBgQCd\n/Bu4kJ6O2+89Ur/H2FKNlITRATw1/1aOkGmJj7Swe28ghuQua5vXZlLCiBuFk6+9\nSEMvim21N9WSstvryhKQ6N9temPxXPV7oAzhX0VltnI0DWjmibvTHo1TMGCUfzK7\nt00VxPhb3q0M3eItCPIsqWKXI1CWT6CVlps2EBAwyQKBgFgyu8xEx2VFEPYto94s\ndtneZ+mdLB4BqezsNw31wTDLTP+FHVaUlUezpUH+UdoBRhczCgDZliaqUU07CbxY\n72NIvHhtKZflIapGpr0wLRpxph+FuJt3ykRBGXj15J/4lnl3/B991lq4PYIDwuGp\nbJFp698jLPpTKLz4pX5a6N4c\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@hopekcc-2024-summer-intern-api.iam.gserviceaccount.com",
    "client_id": "111475537004916408901",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40hopekcc-2024-summer-intern-api.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# === Firebase test credentials ===
HOST_EMAIL = "a@a.com"
HOST_PASSWORD = "aaaaaa"
TEST_USERS = [
    {"email": "b@b.com", "password": "bbbbbb"},
    {"email": "c@c.com", "password": "cccccc"},
]

# === Backend URLs ===
LOCAL_BASE_URL = "http://127.0.0.1:8000/"
BASE_URL = LOCAL_BASE_URL
WEBSOCKET_URL = "ws://127.0.0.1:8766/"

# Static target environments (extend via env variables)
# You can set VM1_BASE_URL / VM1_WS_URL, VM2_BASE_URL / VM2_WS_URL, etc. in .env
ENV_TARGETS = {
    "Production": {
        "base_url": "http://34.125.143.141:8000/",
        "ws_url": "ws://34.125.143.141:8000/ws"
    },
    "Local": {
        "base_url": LOCAL_BASE_URL,
        "ws_url": WEBSOCKET_URL,
    }
}
for i in range(1, 5):
    base = os.getenv(f"VM{i}_BASE_URL")
    ws = os.getenv(f"VM{i}_WS_URL")
    if base and ws:
        ENV_TARGETS[f"VM{i}"] = {"base_url": base, "ws_url": ws}

# === Centralized Cache and State Management ===
class UserCache:
    """Centralized cache for a single user with all their data and clients."""
    def __init__(self, user_email):
        self.user_email = user_email
        self.id_token = None
        self.room_id = None
        
        # Host state
        self.host_current_page = 1
        self.host_total_pages = 1
        self.host_current_song_id = None
        self.host_last_image_etag = None
        self.host_last_image_bytes = None
        self.host_ws_thread = None
        self.host_ws_connection = None
        self.host_is_disconnecting = False
        self.host_state_lock = threading.Lock()
        
        # Songs tab cache
        self.songs_current_list = []
        self.songs_selected_items = []
        
        # Playlists tab cache
        self.playlists_current_list = []
        self.playlists_selected_playlist = None
        self.available_songs_for_playlist = []
        
        # Client management
        self.simulated_clients = []  # List of SimulatedClient objects
        self.client_user_index = 0
        
        # WebSocket connections cache
        self.ws_connections = {}  # client_id -> connection info
        
        # Image cache for all clients
        self.image_cache = {}  # etag -> image_bytes
        
        # API response cache
        self.api_cache = {}  # endpoint -> cached_response
        
    def clear_all_caches(self):
        """Clear all cached data for this user."""
        self.songs_current_list.clear()
        self.songs_selected_items.clear()
        self.playlists_current_list.clear()
        self.playlists_selected_playlist = None
        self.available_songs_for_playlist.clear()
        self.image_cache.clear()
        self.api_cache.clear()
        
        # Clear host state
        self.host_current_page = 1
        self.host_total_pages = 1
        self.host_current_song_id = None
        self.host_last_image_etag = None
        self.host_last_image_bytes = None
        
        # Disconnect all clients
        for client in self.simulated_clients[:]:
            client.disconnect()
        self.simulated_clients.clear()
        self.ws_connections.clear()
        self.client_user_index = 0
        
        log("Cache", "success", f"Cleared all caches for user {self.user_email}")
    
    def add_client(self, client):
        """Add a client to this user's cache."""
        self.simulated_clients.append(client)
        self.client_user_index += 1
        log("Cache", "info", f"Added client {client.client_id} to user {self.user_email}")
    
    def remove_client(self, client):
        """Remove a client from this user's cache."""
        if client in self.simulated_clients:
            self.simulated_clients.remove(client)
            if client.client_id in self.ws_connections:
                del self.ws_connections[client.client_id]
            log("Cache", "info", f"Removed client {client.client_id} from user {self.user_email}")
    
    def cache_image(self, etag, image_bytes):
        """Cache an image with its ETag."""
        if etag and image_bytes:
            self.image_cache[etag] = image_bytes
            log("Cache", "info", f"Cached image with ETag {etag[:10]}... ({len(image_bytes)} bytes)")
    
    def get_cached_image(self, etag):
        """Get cached image by ETag."""
        if etag in self.image_cache:
            log("Cache", "info", f"Retrieved cached image for ETag {etag[:10]}...")
            return self.image_cache[etag]
        return None
    
    def cache_api_response(self, endpoint, response):
        """Cache an API response."""
        self.api_cache[endpoint] = {
            'response': response,
            'timestamp': time.time()
        }
        log("Cache", "info", f"Cached API response for {endpoint}")
    
    def get_cached_api_response(self, endpoint, max_age_seconds=60):
        """Get cached API response if not expired."""
        if endpoint in self.api_cache:
            cached = self.api_cache[endpoint]
            if time.time() - cached['timestamp'] < max_age_seconds:
                log("Cache", "info", f"Retrieved cached API response for {endpoint}")
                return cached['response']
            else:
                del self.api_cache[endpoint]
                log("Cache", "info", f"Expired cached response for {endpoint}")
        return None

# === Global Cache Management ===
user_caches = {}  # user_email -> UserCache
current_user_email = HOST_EMAIL  # Default user

def get_current_user_cache():
    """Get or create cache for current user."""
    global current_user_email
    if current_user_email not in user_caches:
        user_caches[current_user_email] = UserCache(current_user_email)
        log("Cache", "info", f"Created new cache for user {current_user_email}")
    return user_caches[current_user_email]

def switch_user(user_email):
    """Switch to a different user and clear their cache."""
    global current_user_email
    if current_user_email != user_email:
        # Clear previous user's cache
        if current_user_email in user_caches:
            user_caches[current_user_email].clear_all_caches()
        
        current_user_email = user_email
        log("Cache", "success", f"Switched to user {user_email}")

def clear_all_user_caches():
    """Clear all caches for all users."""
    for user_cache in user_caches.values():
        user_cache.clear_all_caches()
    user_caches.clear()
    log("Cache", "success", "Cleared all user caches")

# === SECTION 1: CORE CLASSES & CACHE MANAGEMENT ===
# All classes and cache management logic grouped here

# Import time for cache timestamps
import time

# === SECTION 2: HELPER CLASSES & UTILITIES ===

class Logger:
    """Centralized logging system with color-coded output."""
    output_widget = None
    
    @classmethod
    def set_output_widget(cls, widget):
        """Set the main output widget for logging."""
        cls.output_widget = widget
    
    @classmethod
    def log(cls, source, log_type, text, payload=None):
        """Log a message with proper formatting and colors."""
        if not cls.output_widget or not cls.output_widget.winfo_exists():
            return
        
        prefix_map = {
            "api_call": "[API CALL] >", "api_resp": "[API RESP] <",
            "ws_send": "[WS SEND]  >", "ws_recv": "[WS RECV]  <",
            "cache": "[CACHE] *", "info": "[INFO]",
            "success": "[SUCCESS]", "error": "[ERROR]", "warning": "[WARNING]"
        }
        
        color_map = {
            "api_call": "api_call", "api_resp": "api_resp",
            "ws_send": "ws_send", "ws_recv": "ws_recv",
            "cache": "cache", "info": "info",
            "success": "success", "error": "error", "warning": "warning"
        }

        prefix = prefix_map.get(log_type, "[INFO]")
        tag = color_map.get(log_type, "info")
        
        full_message = f"[{source}] {prefix} {text}\n"
        if payload:
            # Truncate long tokens or data for readability
            if isinstance(payload, dict):
                if 'idToken' in payload: 
                    payload['idToken'] = f"{payload['idToken'][:15]}..."
                if 'token' in payload: 
                    payload['token'] = f"{payload['token'][:15]}..."
            payload_str = json.dumps(payload, indent=2)
            full_message += f"  Payload: {payload_str}\n"

        cls.output_widget.configure(state='normal')
        cls.output_widget.insert(tk.END, full_message, tag)
        cls.output_widget.configure(state='disabled')
        cls.output_widget.see(tk.END)

class APIHelper:
    """Helper class for making API requests with proper logging."""
    
    @staticmethod
    def make_request(source, method, endpoint, json_payload=None, token=None, base_url=None):
        """Make an API request with proper logging and error handling."""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Use global BASE_URL if not specified
        if not base_url:
            base_url = BASE_URL
        
        clean_url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        Logger.log(source, "api_call", f"{method} {clean_url}", payload=json_payload)

        try:
            resp = requests.request(method, clean_url, json=json_payload, headers=headers, timeout=10)
            content = resp.json() if resp.content else None
            
            log_text = f"Status {resp.status_code}"
            log_payload = content if content and len(str(content)) < 1000 else (f"<{len(resp.content)} bytes of data>" if resp.content else None)
            Logger.log(source, "api_resp", log_text, payload=log_payload)

            return {"status": resp.status_code, "content": content}
        except requests.RequestException as e:
            Logger.log(source, "error", f"API request failed: {e}")
            return None

class ImageHelper:
    """Helper class for image operations and ETag handling."""
    
    @staticmethod
    def normalize_etag(etag_header):
        """Normalize ETag by removing quotes and W/ prefix for consistent comparison."""
        if not etag_header: 
            return None
        et = etag_header.strip()
        # Remove W/ prefix for weak ETags
        if et.startswith('W/'):
            et = et[2:].strip()
        # Remove surrounding quotes
        if et.startswith('"') and et.endswith('"') and len(et) >= 2:
            et = et[1:-1]
        return et
    
    @staticmethod
    def fetch_room_image(source_log, token, room_id, prev_etag):
        """Fetch room image with ETag caching."""
        headers = {"Authorization": f"Bearer {token}"}
        if prev_etag:
            # Normalize ETag for If-None-Match header
            normalized_etag = prev_etag.strip()
            if not normalized_etag.startswith('"'):
                normalized_etag = f'"{normalized_etag}"'
            headers["If-None-Match"] = normalized_etag
            Logger.log(source_log, "cache", f"Requesting image with If-None-Match header for ETag: {normalized_etag[:15]}...")
        else:
            Logger.log(source_log, "cache", "No previous ETag. Requesting full image.")

        Logger.log(source_log, "api_call", f"GET /rooms/{room_id}/image")

        try:
            resp = requests.get(f"{BASE_URL.rstrip('/')}/rooms/{room_id}/image", headers=headers, timeout=10)
            if resp.status_code == 200:
                etag_raw = resp.headers.get('ETag', '')
                etag_normalized = ImageHelper.normalize_etag(etag_raw)
                Logger.log(source_log, "api_resp", f"Status 200 OK. Received new image ({len(resp.content)} bytes). New ETag: {etag_normalized} (Raw: {etag_raw})")
                return 200, resp.content, etag_normalized
            elif resp.status_code == 304:
                Logger.log(source_log, "api_resp", "Status 304 Not Modified. Server confirms cached image is still valid.")
                return 304, None, prev_etag
            else:
                Logger.log(source_log, "error", f"Image fetch failed: {resp.status_code} - {resp.text}")
                return resp.status_code, None, prev_etag
        except requests.RequestException as e:
            Logger.log(source_log, "error", f"Image fetch error: {e}")
            return 0, None, prev_etag
    
    @staticmethod
    def display_image_bytes(target_frame, image_bytes, max_size=(400, 400)):
        """Display image bytes in a frame."""
        for widget in target_frame.winfo_children(): 
            widget.destroy()
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            img_label = ctk.CTkLabel(target_frame, image=ctk_img, text="")
            img_label.image = ctk_img
            img_label.pack(expand=True)
        except Exception as e:
            Logger.log("Image", "error", f"Error displaying image: {e}")
            ctk.CTkLabel(target_frame, text=f"Error displaying image:\n{e}", text_color="red").pack(expand=True)

# === SECTION 3: GLOBAL STATE VARIABLES ===
# UI References
window = None
main_frame = None
output = None
song_dropdown_var = None
song_display_frame = None
song_info_label = None
page_indicator = None
target_dropdown_var = None

# Playlist management global variables
available_songs_for_playlist = []
selected_song_ids = set()
playlists_current_list = []
simulated_clients = []

# UI widget references
songs_search_entry = None
songs_id_entry = None
playlists_name_entry = None
playlists_song_entry = None
playlists_info_label = None
playlists_display_frame = None
songs_scrollable_frame = None
playlists_scrollable_frame = None
host_ws_connection = None
songs_display_frame = None

# Legacy log function for backward compatibility
def log(source, log_type, text, payload=None):
    """Legacy log function that delegates to Logger class."""
    Logger.log(source, log_type, text, payload)

# === SECTION 4: STATE MANAGEMENT & NAVIGATION ===
def reset_global_state():
    """Clears all session state for a fresh start."""
    if output and output.winfo_exists():
        output.configure(state='normal')
        output.delete(1.0, tk.END)
        output.configure(state='disabled')

    # Clear current user's cache
    cache = get_current_user_cache()
    cache.clear_all_caches()
    
    log("System", "success", "Reset global state and cleared all caches")

def clear_cache_button_handler():
    """Handler for clear cache button."""
    cache = get_current_user_cache()
    cache.clear_all_caches()
    
    # Also clear UI state
    if output and output.winfo_exists():
        output.configure(state='normal')
        output.delete(1.0, tk.END)
        output.configure(state='disabled')
    
    # Reset UI elements
    if song_display_frame:
        for widget in song_display_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(song_display_frame, text="Cache cleared. Select a song to display.").pack(expand=True)
    
    log("System", "success", "Manual cache clear completed")

def setup_mode_selection_ui():
    """Sets up the initial screen for selecting the mode."""
    reset_global_state()
    clear_main_frame()
    mode_frame = ctk.CTkFrame(main_frame)
    mode_frame.pack(expand=True)
    ctk.CTkLabel(mode_frame, text="Select Target Environment", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    # Dropdown of static targets
    global target_dropdown_var
    target_dropdown_var = ctk.StringVar(value=list(ENV_TARGETS.keys())[0])
    env_dropdown = ctk.CTkComboBox(mode_frame, values=list(ENV_TARGETS.keys()), variable=target_dropdown_var, state="readonly", width=320)
    env_dropdown.pack(pady=10)

    def apply_target_environment():
        global BASE_URL, WEBSOCKET_URL
        choice = target_dropdown_var.get()
        target = ENV_TARGETS.get(choice)
        if not target:
            log("Host", "error", f"Unknown target: {choice}")
            return
            
        # Update URLs
        BASE_URL = target["base_url"].rstrip('/') + '/'
        WEBSOCKET_URL = target["ws_url"]
        
        log("Host", "info", f"Environment changed to {choice}")
        log("Host", "info", f"  Base URL set to: {BASE_URL}")
        log("Host", "info", f"  WebSocket URL set to: {WEBSOCKET_URL}")
        
        setup_main_ui()

    ctk.CTkButton(mode_frame, text="Use Target", command=apply_target_environment, height=40).pack(pady=10, padx=20, fill='x')

def setup_main_ui():
    """Sets up the main tabbed interface."""
    clear_main_frame()
    
    # Create notebook for tabs
    notebook = ctk.CTkTabview(main_frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add tabs
    room_tab = notebook.add("Room Simulator")
    songs_tab = notebook.add("Songs")
    playlists_tab = notebook.add("Playlists")
    
    # Setup each tab
    setup_room_simulator_tab(room_tab)
    setup_songs_tab(songs_tab)
    setup_playlists_tab(playlists_tab)

def setup_room_simulator_tab(tab_frame):
    """Sets up the room simulator tab."""
    global song_display_frame, song_info_label, page_indicator
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_columnconfigure(1, weight=1)
    tab_frame.grid_rowconfigure(0, weight=1)

    # Host
    host_frame = ctk.CTkFrame(tab_frame)
    host_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    host_frame.grid_rowconfigure(2, weight=1)
    ctk.CTkLabel(host_frame, text="Host Controls", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)
    ctk.CTkButton(host_frame, text="Sign In", command=get_host_token).grid(row=1, column=0, pady=5, padx=5, sticky="ew")
    ctk.CTkButton(host_frame, text="Create Room", command=create_host_room).grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    
    song_display_frame = ctk.CTkFrame(host_frame, fg_color="#1a1a1a")
    song_display_frame.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
    ctk.CTkLabel(song_display_frame, text="Select a song to display.").pack(expand=True)
    
    song_info_label = ctk.CTkLabel(host_frame, text="No song selected")
    song_info_label.grid(row=3, column=0, columnspan=2, pady=(5,0))
    page_indicator = ctk.CTkLabel(host_frame, text="Page: 0/0")
    page_indicator.grid(row=4, column=0, columnspan=2, pady=(0,5))
    
    page_nav = ctk.CTkFrame(host_frame)
    page_nav.grid(row=5, column=0, columnspan=2, pady=5)
    ctk.CTkButton(page_nav, text="< Prev", command=lambda: host_change_page('prev')).pack(side="left", padx=20)
    ctk.CTkButton(page_nav, text="Next >", command=lambda: host_change_page('next')).pack(side="left", padx=20)

    song_select = ctk.CTkFrame(host_frame)
    song_select.grid(row=6, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
    song_select.grid_columnconfigure(0, weight=1)
    song_dropdown = ctk.CTkComboBox(song_select, variable=song_dropdown_var, state="readonly")
    song_dropdown.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    ctk.CTkButton(song_select, text="Load Songs", command=lambda: populate_song_list(song_dropdown)).grid(row=0, column=1, padx=5, pady=5)
    ctk.CTkButton(song_select, text="Select Song", command=host_select_song).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    # Client controls
    client_frame = ctk.CTkFrame(tab_frame)
    client_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    ctk.CTkLabel(client_frame, text="Client Controls", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    ctk.CTkButton(client_frame, text="Add Client", command=add_client_user).pack(pady=5, padx=10, fill="x")
    ctk.CTkButton(client_frame, text="Show Guide", command=show_educational_guide).pack(pady=5, padx=10, fill="x")

def setup_songs_tab(tab_frame):
    """Clean Songs tab - tests all song endpoints."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_columnconfigure(1, weight=1)
    tab_frame.grid_rowconfigure(0, weight=1)
    
    # Left side - Controls
    controls_frame = ctk.CTkFrame(tab_frame, fg_color="#2b2b2b")
    controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    controls_frame.grid_rowconfigure(4, weight=1)
    
    ctk.CTkLabel(controls_frame, text="Songs API Testing", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)
    
    # Auth
    songs_auth_button = ctk.CTkButton(controls_frame, text="Sign In", command=lambda: authenticate_songs_tab())
    songs_auth_button.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
    
    # Load songs
    ctk.CTkButton(controls_frame, text="Load All Songs", command=load_all_songs_clean).grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    
    # Search
    search_frame = ctk.CTkFrame(controls_frame)
    search_frame.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
    search_frame.grid_columnconfigure(0, weight=1)
    
    global songs_search_entry
    songs_search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search songs...")
    songs_search_entry.grid(row=0, column=0, pady=5, padx=5, sticky="ew")
    
    ctk.CTkButton(search_frame, text="Search", command=search_songs_clean).grid(row=0, column=1, pady=5, padx=5)
    
    # Get by ID
    id_frame = ctk.CTkFrame(controls_frame)
    id_frame.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
    id_frame.grid_columnconfigure(0, weight=1)
    
    global songs_id_entry
    songs_id_entry = ctk.CTkEntry(id_frame, placeholder_text="Song ID...")
    songs_id_entry.grid(row=0, column=0, pady=5, padx=5, sticky="ew")
    
    ctk.CTkButton(id_frame, text="Get Song", command=get_song_by_id_clean).grid(row=0, column=1, pady=5, padx=5)
    
    # Song display area
    global songs_display_frame
    songs_display_frame = ctk.CTkFrame(controls_frame, fg_color="#1a1a1a")
    songs_display_frame.grid(row=4, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
    
    ctk.CTkLabel(songs_display_frame, text="Sign in and load songs to test endpoints.").pack(expand=True)
    
    # Right side - Song list
    songs_list_frame = ctk.CTkFrame(tab_frame)
    songs_list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    ctk.CTkLabel(songs_list_frame, text="Songs List", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
    global songs_scrollable_frame
    songs_scrollable_frame = ctk.CTkScrollableFrame(songs_list_frame)
    songs_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Store references
    tab_frame.songs_auth_button = songs_auth_button

def setup_playlists_tab(tab_frame):
    """Clean Playlists tab - tests all playlist endpoints."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_columnconfigure(1, weight=1)
    tab_frame.grid_rowconfigure(0, weight=1)
    
    # Left side - Controls
    controls_frame = ctk.CTkFrame(tab_frame, fg_color="#2b2b2b")
    controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    controls_frame.grid_rowconfigure(5, weight=1)
    
    ctk.CTkLabel(controls_frame, text="Playlists API Testing", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)
    
    # Auth
    playlists_auth_button = ctk.CTkButton(controls_frame, text="Sign In", command=lambda: authenticate_playlists_tab())
    playlists_auth_button.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
    
    # Load playlists
    ctk.CTkButton(controls_frame, text="Load My Playlists", command=load_playlists_clean).grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    
    # Create playlist
    create_frame = ctk.CTkFrame(controls_frame)
    create_frame.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
    create_frame.grid_columnconfigure(0, weight=1)
    
    global playlists_name_entry
    playlists_name_entry = ctk.CTkEntry(create_frame, placeholder_text="New playlist name...")
    playlists_name_entry.grid(row=0, column=0, pady=5, padx=5, sticky="ew")
    
    ctk.CTkButton(create_frame, text="Create", command=create_playlist_clean).grid(row=0, column=1, pady=5, padx=5)
    
    # Add songs to playlist
    add_frame = ctk.CTkFrame(controls_frame)
    add_frame.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
    add_frame.grid_columnconfigure(0, weight=1)
    
    global playlists_song_entry
    playlists_song_entry = ctk.CTkEntry(add_frame, placeholder_text="Song ID to add...")
    playlists_song_entry.grid(row=0, column=0, pady=5, padx=5, sticky="ew")
    
    ctk.CTkButton(add_frame, text="Add Song", command=add_song_to_playlist_clean).grid(row=0, column=1, pady=5, padx=5)
    
    # Selected playlist info
    global playlists_info_label
    playlists_info_label = ctk.CTkLabel(controls_frame, text="No playlist selected", font=ctk.CTkFont(size=14))
    playlists_info_label.grid(row=4, column=0, columnspan=2, pady=5)
    
    # Playlist display area
    global playlists_display_frame
    playlists_display_frame = ctk.CTkFrame(controls_frame, fg_color="#1a1a1a")
    playlists_display_frame.grid(row=5, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
    
    ctk.CTkLabel(playlists_display_frame, text="Sign in and load playlists to test endpoints.").pack(expand=True)
    
    # Right side - Playlists list
    playlists_list_frame = ctk.CTkFrame(tab_frame)
    playlists_list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    ctk.CTkLabel(playlists_list_frame, text="My Playlists", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
    global playlists_scrollable_frame
    playlists_scrollable_frame = ctk.CTkScrollableFrame(playlists_list_frame)
    playlists_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Store references
    tab_frame.playlists_auth_button = playlists_auth_button

# --- Instructional Logging ---
def log(source, log_type, text, payload=None):
    if not output or not output.winfo_exists(): return
    
    prefix_map = {
        "api_call": "[API CALL] >", "api_resp": "[API RESP] <",
        "ws_send":  "[WS SEND]  >", "ws_recv":  "[WS RECV]  <",
        "cache":    "[CACHE LOGIC] *", "info":     "[INFO]",
        "success":  "[SUCCESS]", "error":    "[ERROR]", "warning":  "[WARNING]"
    }
    
    color_map = {
        "api_call": "api_call", "api_resp": "api_resp",
        "ws_send": "ws_send", "ws_recv": "ws_recv",
        "cache": "cache", "info": "info",
        "success": "success", "error": "error", "warning": "warning"
    }

    prefix = prefix_map.get(log_type, "[INFO]")
    tag = color_map.get(log_type, "info")
    
    full_message = f"[{source}] {prefix} {text}\n"
    if payload:
        # Truncate long tokens or data for readability
        if isinstance(payload, dict):
            if 'idToken' in payload: payload['idToken'] = f"{payload['idToken'][:15]}..."
            if 'token' in payload: payload['token'] = f"{payload['token'][:15]}..."
        payload_str = json.dumps(payload, indent=2)
        full_message += f"  Payload: {payload_str}\n"

    output.configure(state='normal')
    output.insert(tk.END, full_message, tag)
    output.configure(state='disabled')
    output.see(tk.END)

# --- API Request Logic ---
def make_api_request(source, method, endpoint, json_payload=None, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Clean URL construction to avoid double slashes
    clean_url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    log(source, "api_call", f"{method} {clean_url}", payload=json_payload)

    try:
        resp = requests.request(method, clean_url, json=json_payload, headers=headers, timeout=10)
        content = resp.json() if resp.content else None
        
        log_text = f"Status {resp.status_code}"
        log_payload = content if content and len(str(content)) < 1000 else (f"<{len(resp.content)} bytes of data>" if resp.content else None)
        log(source, "api_resp", log_text, payload=log_payload)

        return {"status": resp.status_code, "content": content}
    except requests.RequestException as e:
        log(source, "error", f"API request failed: {e}")
        return None

# --- Image Fetching Helpers (HTTP + ETag) ---
def _normalize_etag(etag_header):
    """Normalize ETag by removing quotes and W/ prefix for consistent comparison."""
    if not etag_header: 
        return None
    et = etag_header.strip()
    # Remove W/ prefix for weak ETags
    if et.startswith('W/'):
        et = et[2:].strip()
    # Remove surrounding quotes
    if et.startswith('"') and et.endswith('"') and len(et) >= 2:
        et = et[1:-1]
    return et

def fetch_room_image(source_log, token, room_id, prev_etag):
    headers = {"Authorization": f"Bearer {token}"}
    if prev_etag:
        # Normalize ETag for If-None-Match header - ensure it's properly quoted
        normalized_etag = prev_etag.strip()
        if not normalized_etag.startswith('"'):
            normalized_etag = f'"{normalized_etag}"'
        headers["If-None-Match"] = normalized_etag
        log(source_log, "cache", f"Requesting image with If-None-Match header for ETag: {normalized_etag[:15]}...")
    else:
        log(source_log, "cache", "No previous ETag. Requesting full image.")

    log(source_log, "api_call", f"GET /rooms/{room_id}/image")

    try:
        resp = requests.get(f"{BASE_URL.rstrip('/')}/rooms/{room_id}/image", headers=headers, timeout=10)
        if resp.status_code == 200:
            etag_raw = resp.headers.get('ETag', '')
            etag_normalized = _normalize_etag(etag_raw)
            log(source_log, "api_resp", f"Status 200 OK. Received new image ({len(resp.content)} bytes). New ETag: {etag_normalized} (Raw: {etag_raw})")
            return 200, resp.content, etag_normalized
        elif resp.status_code == 304:
            log(source_log, "api_resp", "Status 304 Not Modified. Server confirms cached image is still valid.")
            return 304, None, prev_etag
        else:
            log(source_log, "error", f"Image fetch failed: {resp.status_code} - {resp.text}")
            return resp.status_code, None, prev_etag
    except requests.RequestException as e:
        log(source_log, "error", f"Image fetch error: {e}")
        return 0, None, prev_etag

def display_image_bytes(target_frame, image_bytes, max_size=(400, 400)):
    for widget in target_frame.winfo_children(): widget.destroy()
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        img_label = ctk.CTkLabel(target_frame, image=ctk_img, text="")
        img_label.image = ctk_img
        img_label.pack(expand=True)
    except Exception as e:
        log("Host", "error", f"Error displaying image: {e}")
        ctk.CTkLabel(target_frame, text=f"Error displaying image:\n{e}", text_color="red").pack(expand=True)

def host_fetch_and_display_image(expected_etag):
    cache = get_current_user_cache()
    if not cache.id_token or not cache.room_id: 
        return
    
    # Normalize both ETags for consistent comparison
    expected_normalized = _normalize_etag(expected_etag) if expected_etag else None
    cached_normalized = _normalize_etag(cache.host_last_image_etag) if cache.host_last_image_etag else None
    
    # First check the centralized image cache
    if expected_normalized:
        cached_image = cache.get_cached_image(expected_normalized)
        if cached_image:
            log("Host", "cache", f"ETag from WebSocket ({expected_normalized[:10]}...) found in centralized cache. Using stored image.")
            display_image_bytes(song_display_frame, cached_image, max_size=(400, 400))
            return
    
    # Check legacy cache for backward compatibility
    if expected_normalized and cached_normalized == expected_normalized and cache.host_last_image_bytes:
        log("Host", "cache", f"ETag from WebSocket ({expected_normalized[:10]}...) matches legacy cache. Using stored image.")
        display_image_bytes(song_display_frame, cache.host_last_image_bytes, max_size=(400, 400))
        # Migrate to centralized cache
        cache.cache_image(expected_normalized, cache.host_last_image_bytes)
        return

    status, img_bytes, etag_hex = fetch_room_image("Host", cache.id_token, cache.room_id, cache.host_last_image_etag)
    if status == 200 and img_bytes:
        # Update both legacy and new cache
        cache.host_last_image_bytes = img_bytes
        cache.host_last_image_etag = etag_hex or expected_normalized
        
        # Store in centralized cache
        final_etag = etag_hex or expected_normalized
        if final_etag:
            cache.cache_image(final_etag, img_bytes)
        
        display_image_bytes(song_display_frame, img_bytes, max_size=(400, 400))
    elif status == 304 and cache.host_last_image_bytes:
        display_image_bytes(song_display_frame, cache.host_last_image_bytes, max_size=(400, 400))

# --- Host Functions ---
def get_host_token():
    cache = get_current_user_cache()
    if not FIREBASE_API_KEY:
        log("Host", "error", "FIREBASE_API_KEY is not set. Check .env file.")
        return
    
    # Check if we already have a valid token cached
    if cache.id_token:
        log("Host", "cache", f"Using cached token for {cache.user_email}")
        return
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": cache.user_email, "password": HOST_PASSWORD, "returnSecureToken": True}
    
    log("Host", "api_call", f"POST {url}", payload={"email": cache.user_email, "password": "..."})

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            content = resp.json()
            cache.id_token = content.get("idToken")
            log("Host", "api_resp", f"Status 200 OK - Authenticated host ({cache.user_email})", payload=content)
            log("Host", "cache", f"Cached authentication token for {cache.user_email}")
        else:
            log("Host", "error", f"Host auth failed: {resp.json().get('error', {}).get('message', 'Unknown error')}")
    except requests.RequestException as e:
        log("Host", "error", f"Error during host auth: {e}")

def create_host_room():
    cache = get_current_user_cache()
    if not cache.id_token: 
        log("Host", "warning", "Host not authenticated.")
        return
    
    resp = make_api_request('Host', 'POST', '/rooms/', token=cache.id_token)
    if resp and resp['status'] == 200:
        cache.room_id = resp['content']['room_id']
        log("Host", "success", f"Room '{cache.room_id}' created.")
        log("Host", "cache", f"Cached room ID {cache.room_id} for {cache.user_email}")
        connect_host_websocket()
    else:
        log("Host", "error", f"Failed to create room.", payload=resp.get('content') if resp else 'N/A')

def populate_song_list(dropdown):
    cache = get_current_user_cache()
    if not cache.id_token: log("Host", "warning", "Authenticate as host first."); return
    resp = make_api_request('Host', 'GET', '/songs/list', token=cache.id_token)
    if resp and resp['status'] == 200:
        raw = resp['content']
        try:
            decoded = json.loads(raw) if isinstance(raw, str) else raw
        except Exception as e:
            log("Host", "error", f"Failed to decode songs list JSON: {e}"); return

        songs_list = decoded if isinstance(decoded, list) else (decoded.get("songs") or [])
        
        normalized = [{'id': str(item.get('id')), 'title': item.get('title', 'Unknown')} for item in songs_list if item.get('id')]
        normalized.sort(key=lambda x: int(x['id']))
        
        song_titles = [f"{e['id']}: {e.get('title','Unknown')}" for e in normalized]
        dropdown.configure(values=song_titles)
        if song_titles: dropdown.set(song_titles[0])
        log("Host", "success", f"Loaded {len(normalized)} songs.")
    else:
        log("Host", "error", "Failed to load songs.")

def host_select_song():
    cache = get_current_user_cache()
    if not cache.room_id: log("Host", "warning", "Create a room first."); return
    selected_song = song_dropdown_var.get()
    song_id = selected_song.split(':')[0].strip()

    resp = make_api_request('Host', 'POST', f'/rooms/{cache.room_id}/song', json_payload={"song_id": song_id}, token=cache.id_token)
    if resp and resp['status'] < 400:
        log("Host", "success", f"Host selected Song ID: {song_id}")
        content = resp.get('content') or {}
        
        # Update state with lock to prevent race conditions with WebSocket updates
        with cache.host_state_lock:
            cache.host_current_song_id = song_id
            cache.host_current_page = content.get('current_page', 1)
            cache.host_total_pages = content.get('total_pages', 1)
            
            song_info_label.configure(text=f"Song: {content.get('title', song_id)}")
            page_indicator.configure(text=f"Page: {cache.host_current_page}/{cache.host_total_pages}")
            host_fetch_and_display_image(content.get('image_etag'))
    else:
        log("Host", "error", "Failed to set song.", payload=resp.get('content') if resp else 'N/A')

def host_change_page(direction):
    cache = get_current_user_cache()
    if not cache.host_current_song_id: log("Host", "warning", "Select a song first."); return

    # Check bounds with lock
    with cache.host_state_lock:
        new_page = cache.host_current_page + (1 if direction == "next" else -1)
        if not (1 <= new_page <= cache.host_total_pages):
            log("Host", "info", "Already at first/last page."); return
    
    cache = get_current_user_cache()
    resp = make_api_request('Host', 'POST', f'/rooms/{cache.room_id}/page', json_payload={'page': new_page}, token=cache.id_token)
    if resp and resp['status'] < 400:
        log("Host", "success", f"Host triggered page change to {new_page}")
        # Update state with lock to prevent race conditions with WebSocket updates
        with cache.host_state_lock:
            cache.host_current_page = new_page
            page_indicator.configure(text=f"Page: {cache.host_current_page}/{cache.host_total_pages}")
            host_fetch_and_display_image(None)
    else:
        log("Host", "error", "Failed to change page.", payload=resp.get('content') if resp else 'N/A')

def _normalize_websocket_url(base_url, token):
    url = str(base_url).strip()
    if url.startswith("http://"): url = "ws://" + url[7:]
    elif url.startswith("https://"): url = "wss://" + url[8:]
    elif not url.startswith(('ws://', 'wss://')): url = "ws://" + url
    return f"{url.rstrip('/')}?token={token}" if token else url.rstrip('/')

async def host_ws_client_loop():
    global host_ws_connection
    cache = get_current_user_cache()
    ws_url = _normalize_websocket_url(WEBSOCKET_URL, cache.id_token)
    log("Host", "info", "Host attempting WebSocket connection...")
    try:
        async with websockets.connect(ws_url) as websocket:
            host_ws_connection = websocket
            log("Host", "success", "WebSocket connected.")
            
            cache = get_current_user_cache()
            join_payload = {"type": "join_room", "room_id": cache.room_id}
            await websocket.send(json.dumps(join_payload))
            log("Host", "ws_send", "Sent join_room message.", payload=join_payload)

            async for message in websocket:
                cache = get_current_user_cache()
                if cache.host_is_disconnecting: break
                schedule_gui_update(handle_host_message, message)
    except Exception as e:
        log("Host", "error", f"Host WebSocket connection error: {e}")
    finally:
        host_ws_connection = None
        log("Host", "info", "Host WebSocket disconnected.")

def connect_host_websocket():
    cache = get_current_user_cache()
    if not cache.id_token or not cache.room_id:
        log("Host", "warning", "Host must authenticate and create room first.")
        return
    cache.host_is_disconnecting = False
    cache.host_ws_thread = threading.Thread(target=lambda: asyncio.run(host_ws_client_loop()), daemon=True)
    cache.host_ws_thread.start()

def schedule_gui_update(func, *args, **kwargs):
    if window: window.after(0, lambda: func(*args, **kwargs))

def handle_host_message(msg):
    cache = get_current_user_cache()
    data = json.loads(msg)
    log("Host", "ws_recv", f"Received message of type '{data.get('type')}'", payload=data)
    
    msg_type = data.get("type")
    msg_data = data.get("data", {})
    
    # Use lock to prevent race conditions between HTTP responses and WebSocket updates
    with cache.host_state_lock:
        if msg_type == "join_room_success":
            # Handle initial room state from WebSocket join
            room_state = data.get('room_state')
            if room_state and room_state.get('current_song'):
                cache.host_current_song_id = room_state.get('current_song')
                cache.host_current_page = room_state.get('current_page', 1)
                song_details = room_state.get('song_details', {})
                cache.host_total_pages = song_details.get('total_pages', 1)
                song_info_label.configure(text=f"Song: {song_details.get('title', cache.host_current_song_id)}")
                page_indicator.configure(text=f"Page: {cache.host_current_page}/{cache.host_total_pages}")
                host_fetch_and_display_image(room_state.get('image_etag'))
                log("Host", "info", "Received initial room state via WebSocket")
        elif msg_type == "song_updated":
            cache.host_current_song_id = msg_data.get("song_id", cache.host_current_song_id)
            cache.host_current_page = msg_data.get("current_page", cache.host_current_page)
            cache.host_total_pages = msg_data.get("total_pages", cache.host_total_pages)
            song_info_label.configure(text=f"Song: {msg_data.get('title', cache.host_current_song_id)}")
            page_indicator.configure(text=f"Page: {cache.host_current_page}/{cache.host_total_pages}")
            host_fetch_and_display_image(msg_data.get("image_etag"))
        elif msg_type == "page_updated":
            if "current_page" in msg_data:
                cache.host_current_page = msg_data.get("current_page")
                page_indicator.configure(text=f"Page: {cache.host_current_page}/{cache.host_total_pages}")
            host_fetch_and_display_image(msg_data.get("image_etag"))
    
    # Handle non-state messages outside the lock
    if msg_type == "participant_joined":
        log("Host", "info", f"Participant {msg_data.get('user_id')} joined the room")
    elif msg_type == "participant_left":
        log("Host", "info", f"Participant {msg_data.get('user_id')} left the room")
    elif msg_type == "error":
        log("Host", "error", f"WebSocket error: {data.get('message', 'Unknown error')}")
    elif msg_type not in ["join_room_success", "song_updated", "page_updated"]:
        log("Host", "warning", f"Unhandled message type: {msg_type}")

# --- Old authentication functions removed - using clean versions above ---

# --- Clean Songs Functions ---
def authenticate_songs_tab():
    cache = get_current_user_cache()
    if not FIREBASE_API_KEY:
        log("Songs", "error", "FIREBASE_API_KEY is not set. Check .env file.")
        return
    
    # Use existing token if available
    if cache.id_token:
        log("Songs", "cache", f"Using cached token for {cache.user_email}")
        update_songs_console(f"✓ Using cached authentication for {cache.user_email}")
        return
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": cache.user_email, "password": HOST_PASSWORD, "returnSecureToken": True}
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            cache.id_token = resp.json().get("idToken")
            log("Songs", "success", f"Authenticated as {cache.user_email}")
            update_songs_console(f"✓ Authenticated as {cache.user_email}")
        else:
            error_msg = f"Auth failed: {resp.json().get('error', {}).get('message', 'Unknown error')}"
            log("Songs", "error", error_msg)
            update_songs_console(f"✗ {error_msg}")
    except requests.RequestException as e:
        error_msg = f"Auth error: {e}"
        log("Songs", "error", error_msg)
        update_songs_console(f"✗ {error_msg}")

def load_all_songs_clean():
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Songs", "warning", "Please authenticate first")
        update_songs_console("⚠ Please authenticate first")
        return
    
    # Check cache first
    endpoint = '/songs/?limit=50'
    cached_resp = cache.get_cached_api_response(endpoint, max_age_seconds=300)  # 5 minute cache
    if cached_resp:
        cache.songs_current_list = cached_resp['content']
        display_songs_list(cache.songs_current_list)
        success_msg = f"✓ Loaded {len(cache.songs_current_list)} songs (cached)"
        log("Songs", "cache", f"Using cached songs list ({len(cache.songs_current_list)} songs)")
        update_songs_console(success_msg)
        return
    
    log("Songs", "info", "Loading all songs...")
    update_songs_console("Loading all songs...")
    resp = make_api_request('Songs', 'GET', endpoint, token=cache.id_token)
    
    if resp and resp['status'] == 200:
        cache.songs_current_list = resp['content']
        cache.cache_api_response(endpoint, resp)  # Cache the response
        display_songs_list(cache.songs_current_list)
        success_msg = f"✓ Loaded {len(cache.songs_current_list)} songs"
        log("Songs", "success", f"Loaded {len(cache.songs_current_list)} songs")
        update_songs_console(success_msg)
    else:
        error_msg = f"✗ Failed to load - {resp.get('content') if resp else 'N/A'}"
        log("Songs", "error", f"Failed to load - {resp.get('content') if resp else 'N/A'}")
        update_songs_console(error_msg)

def search_songs_clean():
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Songs", "warning", "Please authenticate first")
        update_songs_console("⚠ Please authenticate first")
        return
    
    query = songs_search_entry.get().strip()
    if not query:
        log("Songs", "warning", "Enter search term")
        update_songs_console("⚠ Enter search term")
        return
    
    log("Songs", "info", f"Searching for '{query}'...")
    update_songs_console(f"Searching for '{query}'...")
    resp = make_api_request('Songs', 'GET', f'/songs/?search={query}&limit=20', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        cache.songs_current_list = resp['content']
        display_songs_list(cache.songs_current_list)
        success_msg = f"✓ Found {len(cache.songs_current_list)} songs"
        log("Songs", "success", f"Found {len(cache.songs_current_list)} songs")
        update_songs_console(success_msg)
    else:
        error_msg = f"✗ Search failed - {resp.get('content') if resp else 'N/A'}"
        log("Songs", "error", f"Search failed - {resp.get('content') if resp else 'N/A'}")
        update_songs_console(error_msg)

def get_song_by_id_clean():
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Songs", "warning", "Please authenticate first")
        update_songs_console("⚠ Please authenticate first")
        return
    
    song_id = songs_id_entry.get().strip()
    if not song_id:
        log("Songs", "warning", "Enter song ID")
        update_songs_console("⚠ Enter song ID")
        return
    
    log("Songs", "info", f"Getting song {song_id}...")
    update_songs_console(f"Getting song {song_id}...")
    resp = make_api_request('Songs', 'GET', f'/songs/{song_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        song = resp['content']
        display_single_song(song)
        success_msg = f"✓ Retrieved '{song.get('title', 'Unknown')}'"
        log("Songs", "success", f"Retrieved '{song.get('title', 'Unknown')}'")
        update_songs_console(success_msg)
    else:
        error_msg = f"✗ Get song failed - {resp.get('content') if resp else 'N/A'}"
        log("Songs", "error", f"Get song failed - {resp.get('content') if resp else 'N/A'}")
        update_songs_console(error_msg)

def display_songs_list(songs):
    """Display songs in clean list format."""
    for widget in songs_scrollable_frame.winfo_children():
        widget.destroy()
    
    if not songs:
        ctk.CTkLabel(songs_scrollable_frame, text="No songs found").pack(pady=20)
        return
    
    for song in songs:
        song_frame = ctk.CTkFrame(songs_scrollable_frame)
        song_frame.pack(fill="x", padx=5, pady=2)
        song_frame.grid_columnconfigure(0, weight=1)
        
        # Song info
        title = song.get('title', 'Unknown')
        artist = song.get('artist', 'Unknown')
        song_id = song.get('id', 'N/A')
        
        info_text = f"{title} - {artist}\nID: {song_id}"
        ctk.CTkLabel(song_frame, text=info_text, justify="left").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Test buttons
        button_frame = ctk.CTkFrame(song_frame)
        button_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        
        ctk.CTkButton(button_frame, text="Details", width=60, 
                    command=lambda s=song: test_song_details(s)).pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="Image", width=60,
                    command=lambda s=song: test_song_image(s)).pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="PDF", width=60,
                    command=lambda s=song: test_song_pdf(s)).pack(side="left", padx=2)

def display_single_song(song):
    """Display single song details."""
    for widget in songs_display_frame.winfo_children():
        widget.destroy()
    
    title = song.get('title', 'Unknown')
    artist = song.get('artist', 'Unknown')
    song_id = song.get('id', 'N/A')
    page_count = song.get('page_count', 0)
    
    info_frame = ctk.CTkFrame(songs_display_frame)
    info_frame.pack(fill="x", padx=10, pady=10)
    
    ctk.CTkLabel(info_frame, text=f"{title}", font=ctk.CTkFont(size=14, weight="bold")).pack()
    ctk.CTkLabel(info_frame, text=f"by {artist}").pack()
    ctk.CTkLabel(info_frame, text=f"ID: {song_id} | Pages: {page_count}").pack()
    
    # Test buttons
    button_frame = ctk.CTkFrame(songs_display_frame)
    button_frame.pack(pady=10)
    
    ctk.CTkButton(button_frame, text="Test Image Endpoint", 
                command=lambda: test_song_image(song)).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Test PDF Endpoint", 
                command=lambda: test_song_pdf(song)).pack(side="left", padx=5)
    
    if page_count > 1:
        ctk.CTkButton(button_frame, text="Test Page Endpoint", 
                    command=lambda: test_song_page(song, 1)).pack(side="left", padx=5)

def test_song_details(song):
    """Test GET /songs/{id} endpoint."""
    cache = get_current_user_cache()
    song_id = song.get('id')
    log("Songs", "info", f"Testing GET /songs/{song_id}")
    resp = make_api_request('Songs', 'GET', f'/songs/{song_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        display_single_song(resp['content'])
        log("Songs", "success", f"GET /songs/{song_id} - Success")
    else:
        log("Songs", "error", f"GET /songs/{song_id} - Failed")

def test_song_image(song):
    """Test GET /songs/{id}/image endpoint."""
    song_id = song.get('id')
    log("Songs", "info", f"Testing GET /songs/{song_id}/image")
    
    try:
        resp = requests.get(f"{BASE_URL.rstrip('/')}/songs/{song_id}/image", timeout=10)
        if resp.status_code == 200:
            log("Songs", "success", f"GET /songs/{song_id}/image - Success ({len(resp.content)} bytes)")
            show_image_popup(song, resp.content)
        else:
            log("Songs", "error", f"GET /songs/{song_id}/image - Failed (Status {resp.status_code})")
    except Exception as e:
        log("Songs", "error", f"Image test error: {e}")

def test_song_pdf(song):
    """Test GET /songs/{id}/pdf endpoint."""
    song_id = song.get('id')
    log("Songs", "info", f"Testing GET /songs/{song_id}/pdf")
    
    try:
        import webbrowser
        pdf_url = f"{BASE_URL.rstrip('/')}/songs/{song_id}/pdf"
        webbrowser.open(pdf_url)
        log("Songs", "success", f"GET /songs/{song_id}/pdf - Opened in browser")
    except Exception as e:
        log("Songs", "error", f"PDF test error: {e}")

def test_song_page(song, page_num):
    """Test GET /songs/{id}/page/{page} endpoint."""
    song_id = song.get('id')
    log("Songs", "info", f"Testing GET /songs/{song_id}/page/{page_num}")
    
    try:
        resp = requests.get(f"{BASE_URL.rstrip('/')}/songs/{song_id}/page/{page_num}", timeout=10)
        if resp.status_code == 200:
            log("Songs", "success", f"GET /songs/{song_id}/page/{page_num} - Success ({len(resp.content)} bytes)")
            show_page_popup(song, page_num, resp.content)
        else:
            log("Songs", "error", f"GET /songs/{song_id}/page/{page_num} - Failed (Status {resp.status_code})")
    except Exception as e:
        log("Songs", "error", f"Page test error: {e}")

def show_image_popup(song, image_data):
    """Show song image in popup."""
    try:
        from PIL import Image, ImageTk
        import io
        
        popup = ctk.CTkToplevel()
        popup.title(f"Image - {song.get('title', 'Unknown')}")
        popup.geometry("600x700")
        
        ctk.CTkLabel(popup, text=f"{song.get('title', 'Unknown')} - Cover Image", 
                   font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail((500, 500), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        image_label = ctk.CTkLabel(popup, image=photo, text="")
        image_label.pack(padx=10, pady=10)
        image_label.image = photo
        
    except Exception as e:
        log("Songs", "error", f"Failed to display image: {e}")

def show_page_popup(song, page_num, image_data):
    """Show song page in popup."""
    try:
        from PIL import Image, ImageTk
        import io
        
        popup = ctk.CTkToplevel()
        popup.title(f"Page {page_num} - {song.get('title', 'Unknown')}")
        popup.geometry("600x700")
        
        ctk.CTkLabel(popup, text=f"{song.get('title', 'Unknown')} - Page {page_num}", 
                   font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail((500, 600), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        image_label = ctk.CTkLabel(popup, image=photo, text="")
        image_label.pack(padx=10, pady=10)
        image_label.image = photo
        
    except Exception as e:
        log("Songs", "error", f"Failed to display page: {e}")

def load_all_songs_proper():
    """Load all songs - tests GET /songs/ endpoint."""
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Songs", "warning", "Please authenticate first")
        return
    
    log("Songs", "info", "Loading all songs...")
    resp = make_api_request('Songs', 'GET', '/songs/?limit=50', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        cache.songs_current_list = resp['content']
        display_songs_list_proper(cache.songs_current_list)
        log("Songs", "success", f"Loaded {len(cache.songs_current_list)} songs")
    else:
        log("Songs", "error", "Failed to load songs", payload=resp.get('content') if resp else 'N/A')

def perform_song_search_proper(query, search_type_display, search_types):
    """Perform song search - tests GET /songs/?search=X and GET /songs/search/{type}?q=X endpoints."""
    if not query.strip():
        log("Songs", "warning", "Please enter a search query")
        return
    
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Songs", "warning", "Please authenticate first")
        return
    
    # Map display names to API endpoints
    type_mapping = {t[0]: t[1] for t in search_types}
    search_type = type_mapping.get(search_type_display, "basic")
    
    if search_type == "basic":
        endpoint = f"/songs/?search={query}&limit=20"
    else:
        endpoint = f"/songs/search/{search_type}?q={query}&limit=20"
    
    log("Songs", "info", f"Searching songs: '{query}' (type: {search_type})")
    resp = make_api_request('Songs', 'GET', endpoint, token=cache.id_token)
    
    if resp and resp['status'] == 200:
        cache.songs_current_list = resp['content']
        display_songs_list_proper(cache.songs_current_list)
        log("Songs", "success", f"Found {len(cache.songs_current_list)} songs")
    else:
        log("Songs", "error", "Failed to search songs", payload=resp.get('content') if resp else 'N/A')

def get_song_by_id_proper(song_id):
    """Get song by ID - tests GET /songs/{id} endpoint."""
    if not song_id.strip():
        log("Songs", "warning", "Please enter a song ID")
        return
    
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Songs", "warning", "Please authenticate first")
        return
    
    log("Songs", "info", f"Getting song by ID: {song_id}")
    resp = make_api_request('Songs', 'GET', f'/songs/{song_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        song_details = resp['content']
        display_single_song_details(song_details)
        log("Songs", "success", f"Retrieved song: {song_details.get('title', 'Unknown')}")
    else:
        log("Songs", "error", f"Failed to get song {song_id}", payload=resp.get('content') if resp else 'N/A')

def display_songs_list_proper(songs):
    """Display songs in the songs list frame with ALL endpoint actions."""
    # Find the songs tab and its scrollable frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            songs_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Songs":
                    songs_tab = widget._tab_dict[tab_name]
                    break
            
            if songs_tab and hasattr(songs_tab, 'songs_scrollable'):
                songs_frame = songs_tab.songs_scrollable
                
                # Clear previous songs
                for child in songs_frame.winfo_children():
                    child.destroy()
                
                if not songs:
                    ctk.CTkLabel(songs_frame, text="No songs found\nTry loading all songs or searching").pack(pady=20)
                    return
                
                # Display each song with ALL endpoint actions
                for i, song in enumerate(songs):
                    song_frame = ctk.CTkFrame(songs_frame)
                    song_frame.pack(fill="x", padx=5, pady=3)
                    song_frame.grid_columnconfigure(0, weight=1)
                    
                    # Song info
                    title = song.get('title', 'Unknown Title')
                    artist = song.get('artist', 'Unknown Artist')
                    song_id = song.get('id', 'N/A')
                    page_count = song.get('page_count', 0)
                    
                    info_text = f"🎵 {title} by {artist}\nID: {song_id} | Pages: {page_count}"
                    info_label = ctk.CTkLabel(song_frame, text=info_text, justify="left")
                    info_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
                    
                    # Action buttons frame - ALL ENDPOINTS
                    button_frame = ctk.CTkFrame(song_frame)
                    button_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")
                    
                    # Row 1: Basic actions
                    ctk.CTkButton(button_frame, text="Details", width=60, 
                                command=lambda s=song: test_song_details_endpoint(s)).grid(row=0, column=0, padx=2, pady=2)
                    ctk.CTkButton(button_frame, text="Image", width=60,
                                command=lambda s=song: test_song_image_endpoint(s)).grid(row=0, column=1, padx=2, pady=2)
                    ctk.CTkButton(button_frame, text="PDF", width=60,
                                command=lambda s=song: test_song_pdf_endpoint(s)).grid(row=0, column=2, padx=2, pady=2)
                    
                    # Row 2: Page actions (if multi-page)
                    if page_count > 1:
                        ctk.CTkButton(button_frame, text="Pages", width=60,
                                    command=lambda s=song: test_song_pages_endpoint(s)).grid(row=1, column=0, padx=2, pady=2)
                        ctk.CTkButton(button_frame, text="Page 1", width=60,
                                    command=lambda s=song: test_single_page_endpoint(s, 1)).grid(row=1, column=1, padx=2, pady=2)
                        if page_count > 2:
                            ctk.CTkButton(button_frame, text="Page 2", width=60,
                                        command=lambda s=song: test_single_page_endpoint(s, 2)).grid(row=1, column=2, padx=2, pady=2)
                break

def test_song_details_endpoint(song):
    """Test GET /songs/{id} endpoint and display comprehensive details."""
    cache = get_current_user_cache()
    song_id = song.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    log("Songs", "info", f"Testing GET /songs/{song_id} endpoint")
    resp = make_api_request('Songs', 'GET', f'/songs/{song_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        song_details = resp['content']
        display_single_song_details(song_details)
        log("Songs", "success", f"GET /songs/{song_id} - Retrieved detailed song info")
    else:
        log("Songs", "error", f"GET /songs/{song_id} failed", payload=resp.get('content') if resp else 'N/A')

def test_song_image_endpoint(song):
    """Test GET /songs/{id}/image endpoint."""
    song_id = song.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    log("Songs", "info", f"Testing GET /songs/{song_id}/image endpoint")
    
    # Make request without token for image
    try:
        import requests
        resp = requests.get(f"{BASE_URL}/songs/{song_id}/image", timeout=10)
        
        if resp.status_code == 200:
            log("Songs", "success", f"GET /songs/{song_id}/image - Image retrieved ({len(resp.content)} bytes)")
            # Show image in popup
            show_song_image_popup(song, resp.content)
        else:
            log("Songs", "error", f"GET /songs/{song_id}/image failed - Status {resp.status_code}")
    except Exception as e:
        log("Songs", "error", f"GET /songs/{song_id}/image error: {e}")

def test_song_pdf_endpoint(song):
    """Test GET /songs/{id}/pdf endpoint."""
    song_id = song.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    log("Songs", "info", f"Testing GET /songs/{song_id}/pdf endpoint")
    
    try:
        import webbrowser
        pdf_url = f"{BASE_URL}/songs/{song_id}/pdf"
        webbrowser.open(pdf_url)
        log("Songs", "success", f"GET /songs/{song_id}/pdf - PDF opened in browser")
    except Exception as e:
        log("Songs", "error", f"GET /songs/{song_id}/pdf error: {e}")

def test_song_pages_endpoint(song):
    """Test GET /songs/{id}/page/{page} endpoint for all pages."""
    song_id = song.get('id')
    page_count = song.get('page_count', 0)
    
    if not song_id or page_count <= 1:
        log("Songs", "warning", "Song has no multiple pages to test")
        return
    
    log("Songs", "info", f"Testing GET /songs/{song_id}/page/{{page}} endpoint for {page_count} pages")
    
    # Test first few pages
    pages_to_test = min(3, page_count)
    for page_num in range(1, pages_to_test + 1):
        test_single_page_endpoint(song, page_num)

def test_single_page_endpoint(song, page_num):
    """Test GET /songs/{id}/page/{page} endpoint for a specific page."""
    song_id = song.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    log("Songs", "info", f"Testing GET /songs/{song_id}/page/{page_num} endpoint")
    
    try:
        import requests
        resp = requests.get(f"{BASE_URL}/songs/{song_id}/page/{page_num}", timeout=10)
        
        if resp.status_code == 200:
            log("Songs", "success", f"GET /songs/{song_id}/page/{page_num} - Page image retrieved ({len(resp.content)} bytes)")
            # Show page image in popup
            show_song_page_popup(song, page_num, resp.content)
        else:
            log("Songs", "error", f"GET /songs/{song_id}/page/{page_num} failed - Status {resp.status_code}")
    except Exception as e:
        log("Songs", "error", f"GET /songs/{song_id}/page/{page_num} error: {e}")

def display_single_song_details(song_details):
    """Display comprehensive song details in the details frame."""
    # Find the songs tab and its details frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            songs_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Songs":
                    songs_tab = widget._tab_dict[tab_name]
                    break
            
            if songs_tab and hasattr(songs_tab, 'song_details_frame'):
                details_frame = songs_tab.song_details_frame
                
                # Clear previous details
                for child in details_frame.winfo_children():
                    child.destroy()
                
                # Display comprehensive song information
                title = song_details.get('title', 'Unknown Title')
                artist = song_details.get('artist', 'Unknown Artist')
                song_id = song_details.get('id', 'N/A')
                page_count = song_details.get('page_count', 0)
                
                # Header
                header_frame = ctk.CTkFrame(details_frame)
                header_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(header_frame, text=f"🎵 {title}", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
                ctk.CTkLabel(header_frame, text=f"by {artist}", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10)
                ctk.CTkLabel(header_frame, text=f"ID: {song_id}", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=10)
                ctk.CTkLabel(header_frame, text=f"Pages: {page_count}", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=10, pady=(0,5))
                
                # All endpoint actions
                actions_frame = ctk.CTkFrame(details_frame)
                actions_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(actions_frame, text="🔍 Test All Endpoints:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
                
                # Endpoint buttons
                button_frame = ctk.CTkFrame(actions_frame)
                button_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkButton(button_frame, text="GET /songs/{id}/image", 
                            command=lambda: test_song_image_endpoint(song_details)).pack(side="left", padx=5, pady=5)
                ctk.CTkButton(button_frame, text="GET /songs/{id}/pdf", 
                            command=lambda: test_song_pdf_endpoint(song_details)).pack(side="left", padx=5, pady=5)
                
                if page_count > 1:
                    ctk.CTkButton(button_frame, text="GET /songs/{id}/page/{page}", 
                                command=lambda: test_song_pages_endpoint(song_details)).pack(side="left", padx=5, pady=5)
                
                # Additional metadata if available
                if len(song_details) > 4:  # More than basic fields
                    metadata_frame = ctk.CTkFrame(details_frame)
                    metadata_frame.pack(fill="x", padx=10, pady=10)
                    
                    ctk.CTkLabel(metadata_frame, text="📋 Additional Metadata:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=5)
                    
                    for key, value in song_details.items():
                        if key not in ['id', 'title', 'artist', 'page_count']:
                            ctk.CTkLabel(metadata_frame, text=f"{key}: {value}").pack(anchor="w", padx=20, pady=2)
                break

def show_song_image_popup(song, image_data):
    """Show song cover image in a popup window."""
    try:
        from PIL import Image, ImageTk
        import io
        
        # Create popup window
        popup = ctk.CTkToplevel()
        popup.title(f"Song Cover - {song.get('title', 'Unknown')}")
        popup.geometry("600x700")
        
        # Song info header
        info_frame = ctk.CTkFrame(popup)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text=f"🎵 {song.get('title', 'Unknown')}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        ctk.CTkLabel(info_frame, text=f"by {song.get('artist', 'Unknown')}", font=ctk.CTkFont(size=12)).pack()
        ctk.CTkLabel(info_frame, text=f"Endpoint: GET /songs/{song.get('id')}/image", font=ctk.CTkFont(size=10)).pack(pady=5)
        
        # Image display
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail((500, 500), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        image_label = ctk.CTkLabel(popup, image=photo, text="")
        image_label.pack(padx=10, pady=10)
        image_label.image = photo  # Keep a reference
        
        popup.transient()
        popup.grab_set()
        
    except Exception as e:
        log("Songs", "error", f"Failed to display image: {e}")

def show_song_page_popup(song, page_num, image_data):
    """Show song page image in a popup window."""
    try:
        from PIL import Image, ImageTk
        import io
        
        # Create popup window
        popup = ctk.CTkToplevel()
        popup.title(f"Page {page_num} - {song.get('title', 'Unknown')}")
        popup.geometry("600x700")
        
        # Song info header
        info_frame = ctk.CTkFrame(popup)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text=f"📄 Page {page_num} of {song.get('title', 'Unknown')}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        ctk.CTkLabel(info_frame, text=f"by {song.get('artist', 'Unknown')}", font=ctk.CTkFont(size=12)).pack()
        ctk.CTkLabel(info_frame, text=f"Endpoint: GET /songs/{song.get('id')}/page/{page_num}", font=ctk.CTkFont(size=10)).pack(pady=5)
        
        # Image display
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail((500, 600), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        image_label = ctk.CTkLabel(popup, image=photo, text="")
        image_label.pack(padx=10, pady=10)
        image_label.image = photo  # Keep a reference
        
        popup.transient()
        popup.grab_set()
        
    except Exception as e:
        log("Songs", "error", f"Failed to display page image: {e}")

def load_all_songs():
    """Load all songs with pagination."""
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Songs", "warning", "Please authenticate first")
        return
    
    log("Songs", "info", "Loading all songs...")
    resp = make_api_request('Songs', 'GET', '/songs/?limit=100', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        cache.songs_current_list = resp['content']
        display_songs_list(cache.songs_current_list)
        log("Songs", "success", f"Loaded {len(cache.songs_current_list)} songs")
    else:
        log("Songs", "error", "Failed to load songs", payload=resp.get('content') if resp else 'N/A')

def perform_song_search(query, search_type_display, search_types):
    """Perform song search based on selected type."""
    if not query.strip():
        log("Songs", "warning", "Please enter a search query")
        return
    
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Songs", "warning", "Please authenticate first")
        return
    
    # Map display names to API endpoints
    type_mapping = {t[0]: t[1] for t in search_types}
    search_type = type_mapping.get(search_type_display, "basic")
    
    if search_type == "basic":
        endpoint = f"/songs/?search={query}&limit=20"
    else:
        endpoint = f"/songs/search/{search_type}?q={query}&limit=20"
    
    log("Songs", "info", f"Searching songs: '{query}' (type: {search_type})")
    resp = make_api_request('Songs', 'GET', endpoint, token=cache.id_token)
    
    if resp and resp['status'] == 200:
        cache.songs_current_list = resp['content']
        display_songs_list(cache.songs_current_list)
        log("Songs", "success", f"Found {len(cache.songs_current_list)} songs")
    else:
        log("Songs", "error", "Failed to search songs", payload=resp.get('content') if resp else 'N/A')

def display_songs_list(songs):
    """Display songs in the songs list frame with comprehensive actions."""
    # Find the songs tab and its scrollable frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            songs_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Songs":
                    songs_tab = widget._tab_dict[tab_name]
                    break
            
            if songs_tab and hasattr(songs_tab, 'songs_scrollable'):
                songs_frame = songs_tab.songs_scrollable
                
                # Clear previous songs
                for child in songs_frame.winfo_children():
                    child.destroy()
                
                if not songs:
                    ctk.CTkLabel(songs_frame, text="No songs found").pack(pady=20)
                    return
                
                # Display each song with comprehensive info and actions
                for i, song in enumerate(songs):
                    song_frame = ctk.CTkFrame(songs_frame)
                    song_frame.pack(fill="x", padx=5, pady=3)
                    song_frame.grid_columnconfigure(0, weight=1)
                    
                    # Song info
                    title = song.get('title', 'Unknown Title')
                    artist = song.get('artist', 'Unknown Artist')
                    song_id = song.get('id', 'N/A')
                    page_count = song.get('page_count', 0)
                    
                    info_text = f"ID: {song_id} | {title} by {artist} | Pages: {page_count}"
                    info_label = ctk.CTkLabel(song_frame, text=info_text, justify="left")
                    info_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
                    
                    # Action buttons frame
                    button_frame = ctk.CTkFrame(song_frame)
                    button_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")
                    
                    # Buttons for different actions
                    ctk.CTkButton(button_frame, text="Details", width=70, 
                                command=lambda s=song: show_song_details_enhanced(s)).pack(side="left", padx=2)
                    ctk.CTkButton(button_frame, text="Image", width=70,
                                command=lambda s=song: show_song_image_enhanced(s)).pack(side="left", padx=2)
                    ctk.CTkButton(button_frame, text="PDF", width=70,
                                command=lambda s=song: open_song_pdf_enhanced(s)).pack(side="left", padx=2)
                    
                    if page_count > 1:
                        ctk.CTkButton(button_frame, text="Pages", width=70,
                                    command=lambda s=song: show_song_pages_enhanced(s)).pack(side="left", padx=2)
                break

def display_song_results(songs):
    """Display search results in the results frame."""
    # Find the songs tab and its results frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            songs_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Songs":
                    songs_tab = widget._tab_dict[tab_name]
                    break
            
            if songs_tab and hasattr(songs_tab, 'results_scrollable'):
                results_frame = songs_tab.results_scrollable
                
                # Clear previous results
                for child in results_frame.winfo_children():
                    child.destroy()
                
                if not songs:
                    ctk.CTkLabel(results_frame, text="No songs found").pack(pady=20)
                    return
                
                # Display each song
                for i, song in enumerate(songs):
                    song_frame = ctk.CTkFrame(results_frame)
                    song_frame.pack(fill="x", padx=5, pady=2)
                    
                    # Song info
                    title = song.get('title', 'Unknown Title')
                    artist = song.get('artist', 'Unknown Artist')
                    song_id = song.get('id', 'N/A')
                    
                    info_text = f"ID: {song_id}\n{title}\nby {artist}"
                    ctk.CTkLabel(song_frame, text=info_text, justify="left").pack(side="left", padx=10, pady=5)
                    
                    # Action buttons
                    button_frame = ctk.CTkFrame(song_frame)
                    button_frame.pack(side="right", padx=10, pady=5)
                    
                    ctk.CTkButton(button_frame, text="Details", width=80, 
                                command=lambda s=song: show_song_details_enhanced(s)).pack(side="left", padx=2)
                    ctk.CTkButton(button_frame, text="Image", width=80,
                                command=lambda s=song: show_song_image_enhanced(s)).pack(side="left", padx=2)
                    ctk.CTkButton(button_frame, text="PDF", width=80,
                                command=lambda s=song: open_song_pdf(s)).pack(side="left", padx=2)
                break

def show_song_details_enhanced(song):
    """Show detailed information about a song with all available data."""
    cache = get_current_user_cache()
    song_id = song.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    log("Songs", "info", f"Fetching details for song {song_id}")
    resp = make_api_request('Songs', 'GET', f'/songs/{song_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        song_details = resp['content']
        display_song_details_enhanced(song_details)
        log("Songs", "success", f"Loaded details for song {song_id}")
    else:
        log("Songs", "error", f"Failed to load song details", payload=resp.get('content') if resp else 'N/A')

def display_song_details_enhanced(song_details):
    """Display comprehensive song information with all endpoints tested."""
    # Find the songs tab and its details frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            songs_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Songs":
                    songs_tab = widget._tab_dict[tab_name]
                    break
            
            if songs_tab and hasattr(songs_tab, 'song_details_frame'):
                details_frame = songs_tab.song_details_frame
                
                # Clear previous details
                for child in details_frame.winfo_children():
                    child.destroy()
                
                # Song header
                header_frame = ctk.CTkFrame(details_frame)
                header_frame.pack(fill="x", padx=10, pady=10)
                
                title = song_details.get('title', 'Unknown')
                artist = song_details.get('artist', 'Unknown')
                song_id = song_details.get('id', 'N/A')
                
                ctk.CTkLabel(header_frame, text=f"{title}", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
                ctk.CTkLabel(header_frame, text=f"by {artist}", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10)
                ctk.CTkLabel(header_frame, text=f"ID: {song_id}", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=10, pady=(0,5))
                
                # Detailed information
                info_frame = ctk.CTkFrame(details_frame)
                info_frame.pack(fill="x", padx=10, pady=10)
                
                info_text = f"""Total Pages: {song_details.get('total_pages', 0)}
Page Count: {song_details.get('page_count', 0)}
Filename: {song_details.get('filename', 'N/A')}

Endpoints Available:
• PDF URL: {song_details.get('pdf_url', 'N/A')}
• Image URL: {song_details.get('image_url', 'N/A')}"""
                
                ctk.CTkLabel(info_frame, text=info_text, justify="left").pack(anchor="w", padx=10, pady=10)
                
                # Action buttons
                actions_frame = ctk.CTkFrame(details_frame)
                actions_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(actions_frame, text="Actions:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=5)
                
                buttons_frame = ctk.CTkFrame(actions_frame)
                buttons_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkButton(buttons_frame, text="View Cover Image", 
                            command=lambda: show_song_image_enhanced(song_details)).pack(side="left", padx=5, pady=5)
                ctk.CTkButton(buttons_frame, text="Open PDF", 
                            command=lambda: open_song_pdf_enhanced(song_details)).pack(side="left", padx=5, pady=5)
                
                total_pages = song_details.get('total_pages', 0)
                if total_pages > 1:
                    ctk.CTkButton(buttons_frame, text="Browse Pages", 
                                command=lambda: show_song_pages_enhanced(song_details)).pack(side="left", padx=5, pady=5)
                
                # Page navigation for multi-page songs
                if total_pages > 1:
                    pages_frame = ctk.CTkFrame(details_frame)
                    pages_frame.pack(fill="x", padx=10, pady=10)
                    
                    ctk.CTkLabel(pages_frame, text="Quick Page Access:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=5)
                    
                    page_buttons_frame = ctk.CTkFrame(pages_frame)
                    page_buttons_frame.pack(fill="x", padx=10, pady=5)
                    
                    # Show page buttons (limit to first 15 for UI space)
                    for page in range(1, min(total_pages + 1, 16)):
                        ctk.CTkButton(page_buttons_frame, text=str(page), width=35,
                                    command=lambda p=page, s=song_details: show_song_page_enhanced(s, p)).pack(side="left", padx=1, pady=2)
                    
                    if total_pages > 15:
                        ctk.CTkLabel(page_buttons_frame, text=f"... ({total_pages} total pages)").pack(side="left", padx=5)
                break

def show_song_image_enhanced(song):
    """Show song cover image with enhanced display."""
    song_id = song.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    log("Songs", "info", f"Fetching image for song {song_id}")
    
    # Create a new window for the image
    image_window = ctk.CTkToplevel()
    image_window.title(f"Song Cover - {song.get('title', song_id)}")
    image_window.geometry("700x800")
    
    # Header with song info
    header_frame = ctk.CTkFrame(image_window)
    header_frame.pack(fill="x", padx=10, pady=10)
    
    title = song.get('title', 'Unknown Title')
    artist = song.get('artist', 'Unknown Artist')
    ctk.CTkLabel(header_frame, text=f"{title} by {artist}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
    ctk.CTkLabel(header_frame, text=f"Song ID: {song_id}").pack()
    
    # Fetch and display image
    try:
        cache = get_current_user_cache()
        headers = {"Authorization": f"Bearer {cache.id_token}"}
        resp = requests.get(f"{BASE_URL.rstrip('/')}/songs/{song_id}/image", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            image_frame = ctk.CTkFrame(image_window)
            image_frame.pack(fill="both", expand=True, padx=10, pady=10)
            display_image_bytes(image_frame, resp.content, max_size=(650, 700))
            log("Songs", "success", f"Loaded image for song {song_id}")
        else:
            ctk.CTkLabel(image_window, text=f"Failed to load image\nStatus: {resp.status_code}").pack(expand=True)
            log("Songs", "error", f"Failed to load image: {resp.status_code}")
    except Exception as e:
        ctk.CTkLabel(image_window, text=f"Error loading image:\n{e}").pack(expand=True)
        log("Songs", "error", f"Error loading image: {e}")

def show_song_pages_enhanced(song):
    """Show a page browser for multi-page songs."""
    song_id = song.get('id')
    total_pages = song.get('total_pages', 0)
    
    if not song_id or total_pages <= 1:
        log("Songs", "warning", "Song has no multiple pages to browse")
        return
    
    # Create page browser window
    browser_window = ctk.CTkToplevel()
    browser_window.title(f"Page Browser - {song.get('title', song_id)}")
    browser_window.geometry("800x900")
    
    # Header
    header_frame = ctk.CTkFrame(browser_window)
    header_frame.pack(fill="x", padx=10, pady=10)
    
    title = song.get('title', 'Unknown Title')
    ctk.CTkLabel(header_frame, text=f"{title} - Page Browser", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
    ctk.CTkLabel(header_frame, text=f"Total Pages: {total_pages}").pack()
    
    # Page selection
    page_select_frame = ctk.CTkFrame(browser_window)
    page_select_frame.pack(fill="x", padx=10, pady=10)
    
    ctk.CTkLabel(page_select_frame, text="Select Page:").pack(side="left", padx=5)
    
    # Create page buttons
    for page in range(1, min(total_pages + 1, 21)):  # Show first 20 pages
        ctk.CTkButton(page_select_frame, text=str(page), width=35,
                    command=lambda p=page: show_song_page_enhanced(song, p)).pack(side="left", padx=1)
    
    if total_pages > 20:
        ctk.CTkLabel(page_select_frame, text=f"... +{total_pages-20} more").pack(side="left", padx=5)

def show_song_page_enhanced(song, page_number):
    """Show a specific page of a song with enhanced display."""
    song_id = song.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    log("Songs", "info", f"Fetching page {page_number} for song {song_id}")
    
    # Create a new window for the page
    page_window = ctk.CTkToplevel()
    page_window.title(f"{song.get('title', song_id)} - Page {page_number}")
    page_window.geometry("700x800")
    
    # Header
    header_frame = ctk.CTkFrame(page_window)
    header_frame.pack(fill="x", padx=10, pady=10)
    
    title = song.get('title', 'Unknown Title')
    ctk.CTkLabel(header_frame, text=f"{title} - Page {page_number}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
    
    # Fetch and display page
    try:
        cache = get_current_user_cache()
        headers = {"Authorization": f"Bearer {cache.id_token}"}
        resp = requests.get(f"{BASE_URL.rstrip('/')}/songs/{song_id}/page/{page_number}", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            image_frame = ctk.CTkFrame(page_window)
            image_frame.pack(fill="both", expand=True, padx=10, pady=10)
            display_image_bytes(image_frame, resp.content, max_size=(650, 700))
            log("Songs", "success", f"Loaded page {page_number} for song {song_id}")
        else:
            ctk.CTkLabel(page_window, text=f"Failed to load page\nStatus: {resp.status_code}").pack(expand=True)
            log("Songs", "error", f"Failed to load page: {resp.status_code}")
    except Exception as e:
        ctk.CTkLabel(page_window, text=f"Error loading page:\n{e}").pack(expand=True)
        log("Songs", "error", f"Error loading page: {e}")

def open_song_pdf_enhanced(song):
    """Open song PDF with enhanced logging."""
    song_id = song.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    pdf_url = f"{BASE_URL}songs/{song_id}/pdf"
    log("Songs", "info", f"Opening PDF: {pdf_url}")
    
    # Try to open in default browser
    try:
        import webbrowser
        webbrowser.open(pdf_url)
        log("Songs", "success", f"Opened PDF for song {song_id} - {song.get('title', 'Unknown')}")
    except Exception as e:
        log("Songs", "error", f"Failed to open PDF: {e}")

def show_song_page(song_details, page_number):
    """Show a specific page of a song."""
    song_id = song_details.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    log("Songs", "info", f"Fetching page {page_number} for song {song_id}")
    
    # Create a new window for the page
    page_window = ctk.CTkToplevel()
    page_window.title(f"Song Page {page_number} - {song_details.get('title', song_id)}")
    page_window.geometry("600x700")
    
    # Fetch and display page
    try:
        cache = get_current_user_cache()
        headers = {"Authorization": f"Bearer {cache.id_token}"}
        resp = requests.get(f"{BASE_URL.rstrip('/')}/songs/{song_id}/page/{page_number}", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            image_frame = ctk.CTkFrame(page_window)
            image_frame.pack(fill="both", expand=True, padx=10, pady=10)
            display_image_bytes(image_frame, resp.content, max_size=(550, 650))
            log("Songs", "success", f"Loaded page {page_number} for song {song_id}")
        else:
            ctk.CTkLabel(page_window, text=f"Failed to load page\nStatus: {resp.status_code}").pack(expand=True)
            log("Songs", "error", f"Failed to load page: {resp.status_code}")
    except Exception as e:
        ctk.CTkLabel(page_window, text=f"Error loading page:\n{e}").pack(expand=True)
        log("Songs", "error", f"Error loading page: {e}")

def open_song_pdf(song):
    """Open song PDF in browser."""
    song_id = song.get('id')
    if not song_id:
        log("Songs", "error", "No song ID available")
        return
    
    pdf_url = f"{BASE_URL}songs/{song_id}/pdf"
    log("Songs", "info", f"Opening PDF: {pdf_url}")
    
    # Try to open in default browser
    try:
        import webbrowser
        webbrowser.open(pdf_url)
        log("Songs", "success", f"Opened PDF for song {song_id}")
    except Exception as e:
        log("Songs", "error", f"Failed to open PDF: {e}")

# --- Clean Playlists Functions ---
# Legacy global variables - now using cache
# playlists_id_token = None  # Now in cache.id_token
# current_playlists = []     # Now in cache.playlists_current_list
# selected_playlist = None   # Now in cache.playlists_selected_playlist

def authenticate_playlists_tab():
    cache = get_current_user_cache()
    if not FIREBASE_API_KEY:
        log("Playlists", "error", "FIREBASE_API_KEY is not set. Check .env file.")
        return
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": HOST_EMAIL, "password": HOST_PASSWORD, "returnSecureToken": True}
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            cache.id_token = resp.json().get("idToken")
            log("Playlists", "success", f"Authenticated as {HOST_EMAIL}")
            update_playlists_console(f"✓ Authenticated as {HOST_EMAIL}")
        else:
            error_msg = f"Auth failed: {resp.json().get('error', {}).get('message', 'Unknown error')}"
            log("Playlists", "error", error_msg)
            update_playlists_console(f"✗ {error_msg}")
    except requests.RequestException as e:
        error_msg = f"Auth error: {e}"
        log("Playlists", "error", error_msg)
        update_playlists_console(f"✗ {error_msg}")

def load_playlists_clean():
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        update_playlists_console("⚠ Please authenticate first")
        return
    
    log("Playlists", "info", "Loading playlists...")
    update_playlists_console("Loading playlists...")
    resp = make_api_request('Playlists', 'GET', '/playlists/', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        response_data = resp['content']
        if response_data.get('success'):
            cache.playlists_current_list = response_data.get('data', [])
            display_playlists_list(cache.playlists_current_list)
            success_msg = f"✓ Loaded {len(cache.playlists_current_list)} playlists"
            log("Playlists", "success", f"Loaded {len(cache.playlists_current_list)} playlists")
            update_playlists_console(success_msg)
        else:
            error_msg = f"✗ API returned error - {response_data.get('message', 'Unknown')}"
            log("Playlists", "error", f"API returned error - {response_data.get('message', 'Unknown')}")
            update_playlists_console(error_msg)
    else:
        error_msg = f"✗ Failed to load - {resp.get('content') if resp else 'N/A'}"
        log("Playlists", "error", f"Failed to load - {resp.get('content') if resp else 'N/A'}")
        update_playlists_console(error_msg)

def create_playlist_clean():
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        update_playlists_console("⚠ Please authenticate first")
        return
    
    name = playlists_name_entry.get().strip()
    if not name:
        log("Playlists", "warning", "Enter playlist name")
        update_playlists_console("⚠ Enter playlist name")
        return
    
    log("Playlists", "info", f"Creating '{name}'...")
    update_playlists_console(f"Creating '{name}'...")
    payload = {"name": name}
    resp = make_api_request('Playlists', 'POST', '/playlists/', json_payload=payload, token=cache.id_token)
    
    if resp and resp['status'] == 200:
        response_data = resp['content']
        if response_data.get('success'):
            success_msg = f"✓ Created '{name}'"
            log("Playlists", "success", f"Created '{name}'")
            update_playlists_console(success_msg)
            playlists_name_entry.delete(0, 'end')
            load_playlists_clean()
        else:
            error_msg = f"✗ Create failed - {response_data.get('message', 'Unknown')}"
            log("Playlists", "error", f"Create failed - {response_data.get('message', 'Unknown')}")
            update_playlists_console(error_msg)
    else:
        error_msg = f"✗ Create failed - {resp.get('content') if resp else 'N/A'}"
        log("Playlists", "error", f"Create failed - {resp.get('content') if resp else 'N/A'}")
        update_playlists_console(error_msg)

def add_song_to_playlist_clean():
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        return
    
    if not cache.playlists_selected_playlist:
        log("Playlists", "warning", "Please select a playlist first")
        return
        
    song_id = playlists_song_entry.get().strip()
    if not song_id:
        log("Playlists", "warning", "Enter song ID")
        return
    
    playlist_id = cache.playlists_selected_playlist.get('id')
    playlist_name = cache.playlists_selected_playlist.get('name', 'Unknown')
    
    log("Playlists", "info", f"Adding song {song_id} to '{playlist_name}'...")
    payload = {"song_id": song_id}
    resp = make_api_request('Playlists', 'POST', f'/playlists/{playlist_id}/songs', json_payload=payload, token=cache.id_token)
    
    if resp and resp['status'] == 200:
        response_data = resp['content']
        if response_data.get('success'):
            log("Playlists", "success", f"Added song to '{playlist_name}'")
            playlists_song_entry.delete(0, 'end')
            load_playlists_clean()
        else:
            log("Playlists", "error", f"Add song failed - {response_data.get('message', 'Unknown')}")
    else:
        log("Playlists", "error", f"Add song failed - {resp.get('content') if resp else 'N/A'}")

def display_playlists_list(playlists):
    """Display playlists in clean list format."""
    for widget in playlists_scrollable_frame.winfo_children():
        widget.destroy()
    
    if not playlists:
        ctk.CTkLabel(playlists_scrollable_frame, text="No playlists found\nCreate one to get started!").pack(pady=20)
        return
    
    for playlist in playlists:
        playlist_frame = ctk.CTkFrame(playlists_scrollable_frame)
        playlist_frame.pack(fill="x", padx=5, pady=2)
        playlist_frame.grid_columnconfigure(0, weight=1)
        
        # Playlist info
        name = playlist.get('name', 'Unknown')
        song_count = playlist.get('song_count', 0)
        playlist_id = playlist.get('id', 'N/A')
        
        # Highlight selected
        cache = get_current_user_cache()
        bg_color = "#404040" if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id else None
        if bg_color:
            playlist_frame.configure(fg_color=bg_color)
        
        info_text = f"{name}\n{song_count} songs"
        ctk.CTkLabel(playlist_frame, text=info_text, justify="left").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Action buttons
        button_frame = ctk.CTkFrame(playlist_frame)
        button_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        
        select_text = "✓ Selected" if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id else "Select"
        ctk.CTkButton(button_frame, text=select_text, width=60,
                    command=lambda p=playlist: select_playlist_clean(p)).pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="View", width=60,
                    command=lambda p=playlist: view_playlist_clean(p)).pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="Delete", width=60,
                    command=lambda p=playlist: delete_playlist_clean(p)).pack(side="left", padx=2)

def select_playlist_clean(playlist):
    """Select a playlist for operations."""
    cache = get_current_user_cache()
    cache.playlists_selected_playlist = playlist
    
    name = playlist.get('name', 'Unknown')
    song_count = playlist.get('song_count', 0)
    playlists_info_label.configure(text=f"Selected: {name} ({song_count} songs)")
    
    display_playlists_list(cache.playlists_current_list)  # Refresh to show selection
    log("Playlists", "info", f"Selected '{name}'")

def view_playlist_clean(playlist):
    """View playlist details."""
    cache = get_current_user_cache()
    playlist_id = playlist.get('id')
    log("Playlists", "info", f"Testing GET /playlists/{playlist_id}")
    
    resp = make_api_request('Playlists', 'GET', f'/playlists/{playlist_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        response_data = resp['content']
        if response_data.get('success'):
            playlist_data = response_data.get('data', {})
            display_playlist_details(playlist_data)
            log("Playlists", "success", f"GET /playlists/{playlist_id} - Success")
        else:
            log("Playlists", "error", f"View failed - {response_data.get('message', 'Unknown')}")
    else:
        log("Playlists", "error", f"GET /playlists/{playlist_id} - Failed")

def display_playlist_details(playlist):
    """Display playlist details in the display area."""
    for widget in playlists_display_frame.winfo_children():
        widget.destroy()
    
    name = playlist.get('name', 'Unknown')
    description = playlist.get('description', '')
    songs = playlist.get('songs', [])
    
    info_frame = ctk.CTkFrame(playlists_display_frame)
    info_frame.pack(fill="x", padx=10, pady=10)
    
    ctk.CTkLabel(info_frame, text=f"{name}", font=ctk.CTkFont(size=14, weight="bold")).pack()
    if description:
        ctk.CTkLabel(info_frame, text=f"{description}").pack()
    ctk.CTkLabel(info_frame, text=f"{len(songs)} songs").pack()
    
    if songs:
        songs_frame = ctk.CTkFrame(playlists_display_frame)
        songs_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(songs_frame, text="Songs:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=5)
        
        for i, song in enumerate(songs, 1):
            song_frame = ctk.CTkFrame(songs_frame)
            song_frame.pack(fill="x", padx=5, pady=2)
            song_frame.grid_columnconfigure(0, weight=1)
            
            title = song.get('title', 'Unknown')
            artist = song.get('artist', 'Unknown')
            song_id = song.get('id', 'N/A')
            
            info_text = f"{i}. {title} - {artist}"
            ctk.CTkLabel(song_frame, text=info_text, justify="left").grid(row=0, column=0, padx=10, pady=2, sticky="w")
            
            ctk.CTkButton(song_frame, text="Remove", width=60,
                        command=lambda s_id=song_id: remove_song_clean(s_id)).grid(row=0, column=1, padx=5, pady=2, sticky="e")

def remove_song_clean(song_id):
    """Remove song from selected playlist."""
    cache = get_current_user_cache()
    if not cache.playlists_selected_playlist:
        log("Playlists", "warning", "No playlist selected")
        return
    
    playlist_id = cache.playlists_selected_playlist.get('id')
    playlist_name = cache.playlists_selected_playlist.get('name', 'Unknown')
    
    log("Playlists", "info", f"Testing DELETE /playlists/{playlist_id}/songs/{song_id}")
    resp = make_api_request('Playlists', 'DELETE', f'/playlists/{playlist_id}/songs/{song_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        response_data = resp['content']
        if response_data.get('success'):
            log("Playlists", "success", f"DELETE /playlists/{playlist_id}/songs/{song_id} - Success")
            load_playlists_clean()
            view_playlist_clean(cache.playlists_selected_playlist)
        else:
            log("Playlists", "error", f"Remove failed - {response_data.get('message', 'Unknown')}")
    else:
        log("Playlists", "error", f"DELETE /playlists/{playlist_id}/songs/{song_id} - Failed")

def delete_playlist_clean(playlist):
    """Delete playlist with confirmation."""
    cache = get_current_user_cache()
    playlist_id = playlist.get('id')
    playlist_name = playlist.get('name', 'Unknown')
    
    # Simple confirmation
    import tkinter.messagebox as msgbox
    if not msgbox.askyesno("Confirm Delete", f"Delete playlist '{playlist_name}'?\n\nThis cannot be undone."):
        return
    
    log("Playlists", "info", f"Testing DELETE /playlists/{playlist_id}")
    resp = make_api_request('Playlists', 'DELETE', f'/playlists/{playlist_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        response_data = resp['content']
        if response_data.get('success'):
            log("Playlists", "success", f"DELETE /playlists/{playlist_id} - Success")
            if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id:
                cache.playlists_selected_playlist = None
                playlists_info_label.configure(text="No playlist selected")
            load_playlists_clean()
        else:
            log("Playlists", "error", f"Delete failed - {response_data.get('message', 'Unknown')}")
    else:
        log("Playlists", "error", f"DELETE /playlists/{playlist_id} - Failed")

# All old complex functions removed - using clean versions above

# All old complex functions removed - using clean versions above

# === SECTION 5: CLIENT MANAGEMENT & SIMULATION ===

class SimulatedClient:
    """Enhanced client class with separate terminal for API logging."""
    
    def __init__(self, client_id):
        self.client_id = client_id
        self.log_source = f"Client {self.client_id}"
        self.client_token = None
        self.ws_thread = None
        self.is_disconnecting = False
        self.last_image_etag = None
        self.last_image_bytes = None
        self.state_lock = threading.Lock()
        
        # Add to user cache
        cache = get_current_user_cache()
        cache.add_client(self)
        
        # Create client window with separate terminal
        self.create_client_window()
        
        log("System", "success", f"Created client {self.client_id}")
    
    def create_client_window(self):
        """Create client window with separate API terminal."""
        self.window = ctk.CTkToplevel()
        self.window.title(f"Client {self.client_id} - Room Simulator")
        self.window.geometry("1200x800")
        
        # Main container with two panels
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left panel - Client controls
        self.controls_frame = ctk.CTkFrame(main_container)
        self.controls_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        
        # Right panel - API Terminal
        self.terminal_frame = ctk.CTkFrame(main_container)
        self.terminal_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
        
        self.setup_client_controls()
        self.setup_client_terminal()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.disconnect)
    
    def setup_client_controls(self):
        """Setup client control panel."""
        # Header
        header_frame = ctk.CTkFrame(self.controls_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header_frame, text=f"Client {self.client_id}", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Authentication section
        auth_frame = ctk.CTkFrame(self.controls_frame)
        auth_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(auth_frame, text="Authentication", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        
        # User selection
        self.user_var = ctk.StringVar(value=TEST_USERS[0]["email"])
        user_dropdown = ctk.CTkComboBox(auth_frame, 
                                       values=[user["email"] for user in TEST_USERS],
                                       variable=self.user_var, state="readonly")
        user_dropdown.pack(pady=5)
        
        ctk.CTkButton(auth_frame, text="Authenticate", 
                     command=self.authenticate_client).pack(pady=5)
        
        self.auth_status = ctk.CTkLabel(auth_frame, text="Not authenticated", 
                                       text_color="red")
        self.auth_status.pack(pady=2)
        
        # Room controls
        room_frame = ctk.CTkFrame(self.controls_frame)
        room_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(room_frame, text="Room Controls", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        
        self.room_entry = ctk.CTkEntry(room_frame, placeholder_text="Room ID")
        self.room_entry.pack(pady=5)
        
        ctk.CTkButton(room_frame, text="Join Room", 
                     command=self.join_room).pack(pady=2)
        ctk.CTkButton(room_frame, text="Connect WebSocket", 
                     command=self.connect_websocket).pack(pady=2)
        ctk.CTkButton(room_frame, text="Disconnect", 
                     command=self.disconnect_websocket).pack(pady=2)
        
        # Status display
        status_frame = ctk.CTkFrame(self.controls_frame)
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(status_frame, text="Status", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        
        self.status_text = ctk.CTkTextbox(status_frame, height=100)
        self.status_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Image display
        self.image_frame = ctk.CTkFrame(self.controls_frame)
        self.image_frame.pack(fill="x", padx=10, pady=5, ipady=10)
        
        ctk.CTkLabel(self.image_frame, text="Current Song Image").pack(pady=5)
        
        self.image_display = ctk.CTkFrame(self.image_frame)
        self.image_display.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(self.image_display, text="No image", text_color="gray").pack(pady=20)
    
    def setup_client_terminal(self):
        """Setup separate API terminal for this client."""
        # Terminal header
        terminal_header = ctk.CTkFrame(self.terminal_frame)
        terminal_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(terminal_header, text=f"Client {self.client_id} - API Terminal", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", pady=5)
        
        ctk.CTkButton(terminal_header, text="Clear", width=60,
                     command=self.clear_terminal).pack(side="right", padx=5)
        
        # Terminal output
        self.terminal_output = scrolledtext.ScrolledText(
            self.terminal_frame, 
            wrap=tk.WORD, 
            height=35,
            bg="#1a1a1a", 
            fg="#ffffff", 
            insertbackground="white",
            font=("Consolas", 9)
        )
        self.terminal_output.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Configure terminal colors
        self.setup_terminal_colors()
        
        # Initial welcome message
        self.log_to_terminal("System", "info", f"Client {self.client_id} terminal initialized")
    
    def setup_terminal_colors(self):
        """Setup color tags for terminal output."""
        self.terminal_output.tag_config("api_call", foreground="#00ff00")
        self.terminal_output.tag_config("api_resp", foreground="#00ffff")
        self.terminal_output.tag_config("ws_send", foreground="#ffff00")
        self.terminal_output.tag_config("ws_recv", foreground="#ff8800")
        self.terminal_output.tag_config("success", foreground="#00ff00")
        self.terminal_output.tag_config("error", foreground="#ff0000")
        self.terminal_output.tag_config("warning", foreground="#ffaa00")
        self.terminal_output.tag_config("info", foreground="#ffffff")
        self.terminal_output.tag_config("cache", foreground="#aa88ff")
    
    def log_to_terminal(self, source, log_type, text, payload=None):
        """Log message to client's separate terminal."""
        if not hasattr(self, 'terminal_output') or not self.terminal_output.winfo_exists():
            return
        
        prefix_map = {
            "api_call": "[API CALL] >", "api_resp": "[API RESP] <",
            "ws_send": "[WS SEND]  >", "ws_recv": "[WS RECV]  <",
            "cache": "[CACHE] *", "info": "[INFO]",
            "success": "[SUCCESS]", "error": "[ERROR]", "warning": "[WARNING]"
        }
        
        prefix = prefix_map.get(log_type, "[INFO]")
        timestamp = time.strftime("%H:%M:%S")
        
        full_message = f"[{timestamp}] [{source}] {prefix} {text}\n"
        if payload:
            if isinstance(payload, dict):
                if 'idToken' in payload: 
                    payload['idToken'] = f"{payload['idToken'][:15]}..."
                if 'token' in payload: 
                    payload['token'] = f"{payload['token'][:15]}..."
            payload_str = json.dumps(payload, indent=2)
            full_message += f"  Payload: {payload_str}\n"
        
        self.terminal_output.configure(state='normal')
        self.terminal_output.insert(tk.END, full_message, log_type)
        self.terminal_output.configure(state='disabled')
        self.terminal_output.see(tk.END)
    
    def clear_terminal(self):
        """Clear the client terminal."""
        self.terminal_output.configure(state='normal')
        self.terminal_output.delete(1.0, tk.END)
        self.terminal_output.configure(state='disabled')
        self.log_to_terminal("System", "info", "Terminal cleared")
    
    def authenticate_client(self):
        """Authenticate this client with selected user credentials."""
        selected_email = self.user_var.get()
        user_data = next((u for u in TEST_USERS if u["email"] == selected_email), None)
        
        if not user_data:
            self.log_to_terminal("Auth", "error", f"User data not found for {selected_email}")
            return
        
        self.log_to_terminal("Auth", "info", f"Authenticating as {selected_email}")
        
        if not FIREBASE_API_KEY:
            self.log_to_terminal("Auth", "error", "Firebase API key not configured")
            return
        
        payload = {
            "email": user_data["email"],
            "password": user_data["password"],
            "returnSecureToken": True
        }
        
        firebase_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        
        try:
            self.log_to_terminal("Auth", "api_call", f"POST Firebase Auth for {selected_email}")
            resp = requests.post(firebase_url, json=payload, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                self.client_token = data.get('idToken')
                self.log_to_terminal("Auth", "success", f"Authentication successful for {selected_email}")
                self.auth_status.configure(text=f"✓ Authenticated as {selected_email}", text_color="green")
                self.update_status(f"Authenticated as {selected_email}")
            else:
                error_data = resp.json() if resp.content else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                self.log_to_terminal("Auth", "error", f"Authentication failed: {error_msg}")
                self.auth_status.configure(text="✗ Authentication failed", text_color="red")
                
        except requests.RequestException as e:
            self.log_to_terminal("Auth", "error", f"Authentication request failed: {e}")
            self.auth_status.configure(text="✗ Network error", text_color="red")
    
    def join_room(self):
        """Join a room using the room ID."""
        room_id = self.room_entry.get().strip()
        if not room_id:
            self.log_to_terminal("Room", "warning", "Please enter a room ID")
            return
        
        if not self.client_token:
            self.log_to_terminal("Room", "warning", "Please authenticate first")
            return
        
        self.log_to_terminal("Room", "info", f"Joining room {room_id}")
        
        # Make API request to join room
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        try:
            self.log_to_terminal("Room", "api_call", f"POST /rooms/{room_id}/join")
            resp = requests.post(f"{BASE_URL.rstrip('/')}/rooms/{room_id}/join", headers=headers, timeout=10)
            
            if resp.status_code == 200:
                self.log_to_terminal("Room", "success", f"Successfully joined room {room_id}")
                self.update_status(f"Joined room: {room_id}")
                self.current_room_id = room_id
            else:
                error_text = resp.text if resp.content else "Unknown error"
                self.log_to_terminal("Room", "error", f"Failed to join room: {resp.status_code} - {error_text}")
                
        except requests.RequestException as e:
            self.log_to_terminal("Room", "error", f"Room join request failed: {e}")
    
    def connect_websocket(self):
        """Connect to WebSocket for real-time updates."""
        if not hasattr(self, 'current_room_id'):
            self.log_to_terminal("WebSocket", "warning", "Please join a room first")
            return
        
        if not self.client_token:
            self.log_to_terminal("WebSocket", "warning", "Please authenticate first")
            return
        
        if self.ws_thread and self.ws_thread.is_alive():
            self.log_to_terminal("WebSocket", "warning", "WebSocket already connected")
            return
        
        self.is_disconnecting = False
        self.ws_thread = threading.Thread(target=self.websocket_loop, daemon=True)
        self.ws_thread.start()
        
        self.log_to_terminal("WebSocket", "info", "Starting WebSocket connection...")
    
    def websocket_loop(self):
        """WebSocket connection loop for this client."""
        ws_url = f"{WEBSOCKET_URL.rstrip('/')}/rooms/{self.current_room_id}?token={self.client_token}"
        
        try:
            self.log_to_terminal("WebSocket", "info", f"Connecting to {ws_url}")
            
            async def ws_handler():
                async with websockets.connect(ws_url) as websocket:
                    self.log_to_terminal("WebSocket", "success", "WebSocket connected")
                    
                    async for message in websocket:
                        if self.is_disconnecting:
                            break
                        
                        try:
                            data = json.loads(message)
                            self.handle_websocket_message(data)
                        except json.JSONDecodeError:
                            self.log_to_terminal("WebSocket", "error", f"Invalid JSON received: {message}")
            
            # Run the async WebSocket handler
            asyncio.run(ws_handler())
            
        except Exception as e:
            if not self.is_disconnecting:
                self.log_to_terminal("WebSocket", "error", f"WebSocket error: {e}")
    
    def handle_websocket_message(self, data):
        """Handle incoming WebSocket messages."""
        msg_type = data.get('type', 'unknown')
        self.log_to_terminal("WebSocket", "ws_recv", f"Received {msg_type}", payload=data)
        
        if msg_type == 'song_change':
            song_data = data.get('song', {})
            self.update_status(f"Song changed: {song_data.get('title', 'Unknown')}")
            
            # Fetch and display new song image
            expected_etag = data.get('image_etag')
            if expected_etag:
                self.fetch_and_display_image(expected_etag)
        
        elif msg_type == 'room_state':
            # Initial room state
            current_song = data.get('current_song', {})
            if current_song:
                self.update_status(f"Current song: {current_song.get('title', 'Unknown')}")
                expected_etag = data.get('image_etag')
                if expected_etag:
                    self.fetch_and_display_image(expected_etag)
    
    def fetch_and_display_image(self, expected_etag):
        """Fetch and display room image with ETag caching."""
        if not hasattr(self, 'current_room_id') or not self.client_token:
            return
        
        # Check cache first
        cache = get_current_user_cache()
        cached_image = cache.get_cached_image(expected_etag)
        
        if cached_image:
            self.log_to_terminal("Cache", "info", f"Using cached image for ETag {expected_etag[:10]}...")
            self.display_image_bytes(cached_image)
            return
        
        # Fetch from server using client's own logging
        headers = {"Authorization": f"Bearer {self.client_token}"}
        if self.last_image_etag:
            normalized_etag = self.last_image_etag.strip()
            if not normalized_etag.startswith('"'):
                normalized_etag = f'"{normalized_etag}"'
            headers["If-None-Match"] = normalized_etag
            self.log_to_terminal("Cache", "info", f"Requesting image with If-None-Match header for ETag: {normalized_etag[:15]}...")
        else:
            self.log_to_terminal("Cache", "info", "No previous ETag. Requesting full image.")

        self.log_to_terminal("Image", "api_call", f"GET /rooms/{self.current_room_id}/image")

        try:
            resp = requests.get(f"{BASE_URL.rstrip('/')}/rooms/{self.current_room_id}/image", headers=headers, timeout=10)
            if resp.status_code == 200:
                etag_raw = resp.headers.get('ETag', '')
                etag_hex = ImageHelper.normalize_etag(etag_raw)
                self.log_to_terminal("Image", "api_resp", f"Status 200 OK. Received new image ({len(resp.content)} bytes). New ETag: {etag_hex}")
                img_bytes = resp.content
                status = 200
            elif resp.status_code == 304:
                self.log_to_terminal("Image", "api_resp", "Status 304 Not Modified. Server confirms cached image is still valid.")
                img_bytes = None
                etag_hex = self.last_image_etag
                status = 304
            else:
                self.log_to_terminal("Image", "error", f"Image fetch failed: {resp.status_code} - {resp.text}")
                return
        except requests.RequestException as e:
            self.log_to_terminal("Image", "error", f"Image fetch error: {e}")
            return
        
        if status == 200 and img_bytes:
            self.last_image_bytes = img_bytes
            self.last_image_etag = etag_hex
            cache.cache_image(etag_hex, img_bytes)
            self.display_image_bytes(img_bytes)
        elif status == 304 and self.last_image_bytes:
            self.display_image_bytes(self.last_image_bytes)
    
    def display_image_bytes(self, image_bytes):
        """Display image in client window."""
        try:
            for widget in self.image_display.winfo_children():
                widget.destroy()
            
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            img_label = ctk.CTkLabel(self.image_display, image=ctk_img, text="")
            img_label.image = ctk_img
            img_label.pack(expand=True)
            
        except Exception as e:
            self.log_to_terminal("Image", "error", f"Error displaying image: {e}")
            ctk.CTkLabel(self.image_display, text="Error loading image", text_color="red").pack(pady=10)
    
    def update_status(self, message):
        """Update client status display."""
        timestamp = time.strftime("%H:%M:%S")
        status_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, status_message)
        self.status_text.see(tk.END)
    
    def disconnect_websocket(self):
        """Disconnect WebSocket connection."""
        self.is_disconnecting = True
        if self.ws_thread and self.ws_thread.is_alive():
            self.log_to_terminal("WebSocket", "info", "Disconnecting WebSocket...")
            # Thread will terminate naturally
        self.update_status("WebSocket disconnected")
    
    def disconnect(self):
        """Disconnect and close client window."""
        self.is_disconnecting = True
        
        # Disconnect WebSocket
        if self.ws_thread and self.ws_thread.is_alive():
            self.log_to_terminal("System", "info", "Disconnecting...")
        
        # Remove from cache
        cache = get_current_user_cache()
        cache.remove_client(self)
        
        # Close window
        if hasattr(self, 'window') and self.window.winfo_exists():
            self.window.destroy()
        
        log("System", "info", f"Client {self.client_id} disconnected")

def add_client_user():
    """Add a new simulated client user."""
    cache = get_current_user_cache()
    client_id = len(cache.simulated_clients) + 1
    
    # Create new client with separate terminal
    client = SimulatedClient(client_id)
    
    log("System", "success", f"Added client {client_id} with separate API terminal")

# === SECTION 6: PLAYLIST MANAGEMENT FUNCTIONS ===

def load_all_songs_for_playlist():
    """Load all available songs for playlist management."""
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        return
    
    log("Playlists", "info", "Loading all songs...")
    resp = make_api_request('Playlists', 'GET', '/songs/?limit=100', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        global available_songs_for_playlist
        available_songs_for_playlist = resp['content']
        display_songs_with_checkboxes(available_songs_for_playlist)
        log("Playlists", "success", f"Loaded {len(available_songs_for_playlist)} songs")
    else:
        log("Playlists", "error", "Failed to load songs", payload=resp.get('content') if resp else 'N/A')

def search_songs_for_playlist(query):
    """Search songs for playlist management."""
    if not query.strip():
        log("Playlists", "warning", "Please enter a search query")
        return
    
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        return
    
    log("Playlists", "info", f"Searching songs: '{query}'")
    resp = make_api_request('Playlists', 'GET', f'/songs/?search={query}&limit=50', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        global available_songs_for_playlist
        available_songs_for_playlist = resp['content']
        display_songs_with_checkboxes(available_songs_for_playlist)
        log("Playlists", "success", f"Found {len(available_songs_for_playlist)} songs")
    else:
        log("Playlists", "error", "Failed to search songs", payload=resp.get('content') if resp else 'N/A')

def display_playlists_modern(playlists):
    """Display playlists in modern layout."""
    # Find the playlists tab and its scrollable frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            playlists_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Playlists":
                    playlists_tab = widget._tab_dict[tab_name]
                    break
            
            if playlists_tab and hasattr(playlists_tab, 'playlists_scrollable'):
                playlists_frame = playlists_tab.playlists_scrollable
                
                # Clear previous playlists
                for child in playlists_frame.winfo_children():
                    child.destroy()
                
                if not playlists:
                    ctk.CTkLabel(playlists_frame, text="No playlists found\nCreate your first playlist!").pack(pady=20)
                    return
                
                # Display each playlist
                for playlist in playlists:
                    playlist_frame = ctk.CTkFrame(playlists_frame)
                    playlist_frame.pack(fill="x", padx=5, pady=3)
                    playlist_frame.grid_columnconfigure(0, weight=1)
                    
                    # Playlist info
                    name = playlist.get('name', 'Unknown Playlist')
                    description = playlist.get('description', '')
                    song_count = playlist.get('song_count', 0)
                    playlist_id = playlist.get('id', 'N/A')
                    
                    # Highlight selected playlist
                    cache = get_current_user_cache()
                    bg_color = "#404040" if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id else None
                    if bg_color:
                        playlist_frame.configure(fg_color=bg_color)
                    
                    # Info display
                    info_text = f"📁 {name}"
                    if description:
                        info_text += f"\n💬 {description}"
                    info_text += f"\n🎵 {song_count} songs"
                    
                    info_label = ctk.CTkLabel(playlist_frame, text=info_text, justify="left")
                    info_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
                    
                    # Action buttons
                    button_frame = ctk.CTkFrame(playlist_frame)
                    button_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")
                    
                    select_text = "✅ Selected" if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id else "Select"
                    ctk.CTkButton(button_frame, text=select_text, width=70,
                                command=lambda p=playlist: select_playlist_modern(p)).pack(side="left", padx=2)
                    ctk.CTkButton(button_frame, text="🗑️ Delete", width=70,
                                command=lambda p=playlist: delete_playlist_modern(p)).pack(side="left", padx=2)
                break

def display_songs_with_checkboxes(songs):
    """Display songs with multi-select checkboxes."""
    # Find the playlists tab and its songs frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            playlists_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Playlists":
                    playlists_tab = widget._tab_dict[tab_name]
                    break
            
            if playlists_tab and hasattr(playlists_tab, 'songs_scrollable'):
                songs_frame = playlists_tab.songs_scrollable
                
                # Clear previous songs
                for child in songs_frame.winfo_children():
                    child.destroy()
                
                if not songs:
                    ctk.CTkLabel(songs_frame, text="No songs found\nTry loading all songs or searching").pack(pady=20)
                    return
                
                # Display each song with checkbox
                for song in songs:
                    song_frame = ctk.CTkFrame(songs_frame)
                    song_frame.pack(fill="x", padx=5, pady=2)
                    song_frame.grid_columnconfigure(1, weight=1)
                    
                    # Song info
                    title = song.get('title', 'Unknown Title')
                    artist = song.get('artist', 'Unknown Artist')
                    song_id = song.get('id', 'N/A')
                    
                    # Checkbox
                    checkbox_var = ctk.BooleanVar(value=song_id in selected_song_ids)
                    checkbox = ctk.CTkCheckBox(song_frame, text="", variable=checkbox_var, width=20,
                                             command=lambda s_id=song_id, var=checkbox_var: toggle_song_selection(s_id, var))
                    checkbox.grid(row=0, column=0, padx=5, pady=5)
                    
                    # Song info
                    info_text = f"🎵 {title}\nby {artist} | ID: {song_id[:8]}..."
                    info_label = ctk.CTkLabel(song_frame, text=info_text, justify="left")
                    info_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
                break

def select_playlist_modern(playlist):
    """Select a playlist for song management."""
    cache = get_current_user_cache()
    cache.playlists_selected_playlist = playlist
    
    # Update the playlist title
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            playlists_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Playlists":
                    playlists_tab = widget._tab_dict[tab_name]
                    break
            
            if playlists_tab and hasattr(playlists_tab, 'playlist_title_label'):
                name = playlist.get('name', 'Unknown Playlist')
                song_count = playlist.get('song_count', 0)
                playlists_tab.playlist_title_label.configure(text=f"🎯 {name} ({song_count} songs)")
                break
    
    # Refresh displays to show selection
    display_playlists_modern(playlists_current_list)
    display_playlist_contents(playlist)
    
    log("Playlists", "success", f"Selected playlist: {playlist.get('name', 'Unknown')}")

def display_playlist_contents(playlist):
    """Display the contents of the selected playlist."""
    # Find the playlists tab and its content frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            playlists_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Playlists":
                    playlists_tab = widget._tab_dict[tab_name]
                    break
            
            if playlists_tab and hasattr(playlists_tab, 'playlist_content_scrollable'):
                content_frame = playlists_tab.playlist_content_scrollable
                
                # Clear previous content
                for child in content_frame.winfo_children():
                    child.destroy()
                
                songs = playlist.get('songs', [])
                
                if not songs:
                    instructions_text = "🎯 This playlist is empty\n\nTo add songs:\n1. Search or load songs on the right\n2. Select songs with checkboxes\n3. Click 'Add Selected to Playlist'"
                    ctk.CTkLabel(content_frame, text=instructions_text, justify="left").pack(padx=10, pady=20)
                else:
                    # Display songs in playlist
                    for i, song in enumerate(songs, 1):
                        song_frame = ctk.CTkFrame(content_frame)
                        song_frame.pack(fill="x", padx=5, pady=2)
                        song_frame.grid_columnconfigure(0, weight=1)
                        
                        # Song info
                        title = song.get('title', 'Unknown Song')
                        artist = song.get('artist', 'Unknown Artist')
                        song_id = song.get('id', 'N/A')
                        
                        info_text = f"{i}. 🎵 {title}\nby {artist}"
                        ctk.CTkLabel(song_frame, text=info_text, justify="left").grid(row=0, column=0, padx=10, pady=5, sticky="w")
                        
                        # Remove button
                        ctk.CTkButton(song_frame, text="❌", width=30,
                                    command=lambda s_id=song_id: remove_song_from_playlist_modern(s_id)).grid(row=0, column=1, padx=5, pady=5, sticky="e")
                break

def toggle_song_selection(song_id, checkbox_var):
    """Toggle song selection for multi-select."""
    global selected_song_ids
    if checkbox_var.get():
        selected_song_ids.add(song_id)
    else:
        selected_song_ids.discard(song_id)
    
    log("Playlists", "info", f"Selected {len(selected_song_ids)} songs")

def select_all_songs():
    """Select all visible songs."""
    global selected_song_ids
    selected_song_ids = {song.get('id') for song in available_songs_for_playlist if song.get('id')}
    display_songs_with_checkboxes(available_songs_for_playlist)
    log("Playlists", "info", f"Selected all {len(selected_song_ids)} songs")

def clear_song_selection():
    """Clear all song selections."""
    global selected_song_ids
    selected_song_ids.clear()
    display_songs_with_checkboxes(available_songs_for_playlist)
    log("Playlists", "info", "Cleared song selection")

def add_selected_songs_to_playlist():
    """Add selected songs to the current playlist - tests POST /playlists/{id}/songs/bulk endpoint."""
    cache = get_current_user_cache()
    if not cache.playlists_selected_playlist:
        log("Playlists", "warning", "Please select a playlist first")
        return
    
    if not selected_song_ids:
        log("Playlists", "warning", "Please select some songs first")
        return
    
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        return
    
    playlist_id = cache.playlists_selected_playlist.get('id')
    playlist_name = cache.playlists_selected_playlist.get('name', 'Unknown')
    
    log("Playlists", "info", f"Adding {len(selected_song_ids)} songs to playlist '{playlist_name}'")
    
    payload = {"song_ids": list(selected_song_ids)}
    resp = make_api_request('Playlists', 'POST', f'/playlists/{playlist_id}/songs/bulk', json_payload=payload, token=cache.id_token)
    
    if resp and resp['status'] == 200:
        response_data = resp['content']
        if response_data.get('success'):
            added_count = len(response_data.get('data', {}).get('added_songs', []))
            skipped_count = len(response_data.get('data', {}).get('skipped_songs', []))
            log("Playlists", "success", f"Added {added_count} songs, skipped {skipped_count} (duplicates/errors)")
            
            # Clear selection and refresh
            clear_song_selection()
            load_playlists_clean()
        else:
            log("Playlists", "error", "Failed to add songs", payload=response_data)
    else:
        log("Playlists", "error", "Failed to add songs to playlist", payload=resp.get('content') if resp else 'N/A')

def remove_song_from_playlist_modern(song_id):
    """Remove a song from the current playlist."""
    cache = get_current_user_cache()
    if not cache.playlists_selected_playlist:
        log("Playlists", "warning", "No playlist selected")
        return
    
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        return
    
    playlist_id = cache.playlists_selected_playlist.get('id')
    playlist_name = cache.playlists_selected_playlist.get('name', 'Unknown')
    
    log("Playlists", "info", f"Removing song from playlist '{playlist_name}'")
    resp = make_api_request('Playlists', 'DELETE', f'/playlists/{playlist_id}/songs/{song_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        response_data = resp['content']
        if response_data.get('success'):
            log("Playlists", "success", f"Removed song from playlist")
            # Refresh playlist
            load_playlists_clean()
        else:
            log("Playlists", "error", "Failed to remove song", payload=response_data)
    else:
        log("Playlists", "error", "Failed to remove song from playlist", payload=resp.get('content') if resp else 'N/A')

def delete_playlist_modern(playlist):
    """Delete a playlist with confirmation."""
    playlist_id = playlist.get('id')
    playlist_name = playlist.get('name', 'Unknown')
    
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        return
    
    # Create confirmation dialog
    confirm_window = ctk.CTkToplevel()
    confirm_window.title("Confirm Deletion")
    confirm_window.geometry("400x200")
    confirm_window.transient()
    confirm_window.grab_set()
    
    # Center the window
    confirm_window.update_idletasks()
    x = (confirm_window.winfo_screenwidth() // 2) - (400 // 2)
    y = (confirm_window.winfo_screenheight() // 2) - (200 // 2)
    confirm_window.geometry(f"400x200+{x}+{y}")
    
    # Confirmation message
    ctk.CTkLabel(confirm_window, text="Delete Playlist?", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
    ctk.CTkLabel(confirm_window, text=f"Are you sure you want to delete:\n'{playlist_name}'?\n\nThis action cannot be undone.").pack(pady=10)
    
    # Buttons
    button_frame = ctk.CTkFrame(confirm_window)
    button_frame.pack(pady=20)
    
    def confirm_delete():
        confirm_window.destroy()
        log("Playlists", "info", f"Deleting playlist '{playlist_name}'")
        resp = make_api_request('Playlists', 'DELETE', f'/playlists/{playlist_id}', token=cache.id_token)
        
        if resp and resp['status'] == 200:
            response_data = resp['content']
            if response_data.get('success'):
                log("Playlists", "success", f"Deleted playlist '{playlist_name}'")
                cache = get_current_user_cache()
                if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id:
                    cache.playlists_selected_playlist = None
                load_playlists_clean()
            else:
                log("Playlists", "error", "Failed to delete playlist", payload=response_data)
        else:
            log("Playlists", "error", "Failed to delete playlist", payload=resp.get('content') if resp else 'N/A')
    
    def cancel_delete():
        confirm_window.destroy()
        log("Playlists", "info", "Playlist deletion cancelled")
    
    ctk.CTkButton(button_frame, text="Delete", command=confirm_delete, fg_color="red", hover_color="darkred").pack(side="left", padx=10)
    ctk.CTkButton(button_frame, text="Cancel", command=cancel_delete).pack(side="left", padx=10)

def clear_playlist_inputs():
    """Clear playlist creation input fields."""
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            playlists_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Playlists":
                    playlists_tab = widget._tab_dict[tab_name]
                    break
            if playlists_tab:
                if hasattr(playlists_tab, 'playlist_name_entry'):
                    playlists_tab.playlist_name_entry.delete(0, 'end')
                if hasattr(playlists_tab, 'playlist_desc_entry'):
                    playlists_tab.playlist_desc_entry.delete(0, 'end')
                break

def display_draggable_songs(songs):
    """Display available songs as draggable items for adding to playlists."""
    # Find the playlists tab and its available songs frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            playlists_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Playlists":
                    playlists_tab = widget._tab_dict[tab_name]
                    break
            
            if playlists_tab and hasattr(playlists_tab, 'available_songs_scrollable'):
                songs_frame = playlists_tab.available_songs_scrollable
                
                # Clear previous songs
                for child in songs_frame.winfo_children():
                    child.destroy()
                
                if not songs:
                    ctk.CTkLabel(songs_frame, text="No songs available\nClick '1. Load Available Songs' first").pack(pady=20)
                    return
                
                # Display each song as draggable
                for song in songs:
                    song_frame = ctk.CTkFrame(songs_frame)
                    song_frame.pack(fill="x", padx=5, pady=2)
                    song_frame.grid_columnconfigure(0, weight=1)
                    
                    # Song info
                    title = song.get('title', 'Unknown Title')
                    artist = song.get('artist', 'Unknown Artist')
                    song_id = song.get('id', 'N/A')
                    
                    info_text = f"🎵 {title}\nby {artist} | ID: {song_id}"
                    info_label = ctk.CTkLabel(song_frame, text=info_text, justify="left")
                    info_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
                    
                    # Drag button (simulated - will add to selected playlist)
                    drag_button = ctk.CTkButton(song_frame, text="➕ Add to Selected", width=120,
                                              command=lambda s=song: add_song_to_selected_playlist_proper(s))
                    drag_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")
                    
                    # Disable if no playlist selected
                    cache = get_current_user_cache()
                    if not cache.playlists_selected_playlist:
                        drag_button.configure(state="disabled")
                break

def display_selectable_playlists(playlists):
    """Display playlists as selectable items."""
    # Find the playlists tab and its playlists frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            playlists_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Playlists":
                    playlists_tab = widget._tab_dict[tab_name]
                    break
            
            if playlists_tab and hasattr(playlists_tab, 'playlists_scrollable'):
                playlists_frame = playlists_tab.playlists_scrollable
                
                # Clear previous playlists
                for child in playlists_frame.winfo_children():
                    child.destroy()
                
                if not playlists:
                    ctk.CTkLabel(playlists_frame, text="No playlists found\nCreate one first!").pack(pady=20)
                    return
                
                # Display each playlist as selectable
                for playlist in playlists:
                    playlist_frame = ctk.CTkFrame(playlists_frame)
                    playlist_frame.pack(fill="x", padx=5, pady=3)
                    playlist_frame.grid_columnconfigure(0, weight=1)
                    
                    # Playlist info
                    name = playlist.get('name', 'Unknown Playlist')
                    playlist_id = playlist.get('id', 'N/A')
                    song_count = len(playlist.get('songs', []))
                    
                    # Highlight selected playlist
                    cache = get_current_user_cache()
                    bg_color = "#404040" if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id else None
                    if bg_color:
                        playlist_frame.configure(fg_color=bg_color)
                    
                    info_text = f"📁 {name}\n{song_count} songs | ID: {playlist_id[:8]}..."
                    info_label = ctk.CTkLabel(playlist_frame, text=info_text, justify="left")
                    info_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
                    
                    # Action buttons
                    button_frame = ctk.CTkFrame(playlist_frame)
                    button_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")
                    
                    select_text = "✅ Selected" if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id else "Select"
                    ctk.CTkButton(button_frame, text=select_text, width=70,
                                command=lambda p=playlist: select_playlist_proper(p)).pack(side="left", padx=2)
                    ctk.CTkButton(button_frame, text="View", width=60,
                                command=lambda p=playlist: show_playlist_details_proper(p)).pack(side="left", padx=2)
                    ctk.CTkButton(button_frame, text="Delete", width=60,
                                command=lambda p=playlist: delete_playlist_proper(p)).pack(side="left", padx=2)
                break

def select_playlist_proper(playlist):
    """Select a playlist as the target for adding songs."""
    cache = get_current_user_cache()
    cache.playlists_selected_playlist = playlist
    
    # Update the playlist title
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            playlists_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Playlists":
                    playlists_tab = widget._tab_dict[tab_name]
                    break
            
            if playlists_tab and hasattr(playlists_tab, 'playlist_title_label'):
                name = playlist.get('name', 'Unknown Playlist')
                playlists_tab.playlist_title_label.configure(text=f"🎯 Selected: {name}")
                break
    
    # Refresh displays to show selection and enable add buttons
    display_selectable_playlists(playlists_current_list)
    display_draggable_songs(available_songs_for_playlist)
    show_playlist_details_proper(playlist)
    
    log("Playlists", "success", f"Selected playlist: {playlist.get('name', 'Unknown')} - You can now add songs!")

def add_song_to_selected_playlist_proper(song):
    """Step 3: Add a song to the selected playlist - tests POST /playlists/{id}/songs?song_id=X endpoint."""
    cache = get_current_user_cache()
    if not cache.playlists_selected_playlist:
        log("Playlists", "warning", "Please select a playlist first")
        return
    
    playlist_id = cache.playlists_selected_playlist.get('id')
    song_id = song.get('id')
    
    if not playlist_id or not song_id:
        log("Playlists", "error", "Invalid playlist or song ID")
        return
    
    song_title = song.get('title', 'Unknown')
    playlist_name = cache.playlists_selected_playlist.get('name', 'Unknown')
    
    log("Playlists", "info", f"Adding '{song_title}' to playlist '{playlist_name}'")
    
    resp = make_api_request('Playlists', 'POST', f'/playlists/{playlist_id}/songs?song_id={song_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        log("Playlists", "success", f"Added '{song_title}' to playlist '{playlist_name}'")
        # Refresh the playlist details and list
        load_playlists_clean()
        show_playlist_details_proper(cache.playlists_selected_playlist)
    else:
        log("Playlists", "error", f"Failed to add song to playlist", payload=resp.get('content') if resp else 'N/A')

def show_playlist_details_proper(playlist):
    """Show detailed playlist contents in the drop zone."""
    # Find the playlists tab and its content frame
    for widget in main_frame.winfo_children():
        if hasattr(widget, '_name') and 'tabview' in str(type(widget)).lower():
            playlists_tab = None
            for tab_name in widget._tab_dict:
                if tab_name == "Playlists":
                    playlists_tab = widget._tab_dict[tab_name]
                    break
            
            if playlists_tab and hasattr(playlists_tab, 'playlist_content_scrollable'):
                content_frame = playlists_tab.playlist_content_scrollable
                
                # Clear previous content
                for child in content_frame.winfo_children():
                    child.destroy()
                
                # Display playlist information
                name = playlist.get('name', 'Unknown Playlist')
                playlist_id = playlist.get('id', 'N/A')
                songs = playlist.get('songs', [])
                
                # Header
                header_frame = ctk.CTkFrame(content_frame)
                header_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(header_frame, text=f"📁 {name}", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
                ctk.CTkLabel(header_frame, text=f"ID: {playlist_id}", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=10)
                ctk.CTkLabel(header_frame, text=f"Total Songs: {len(songs)}", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(0,5))
                
                # Instructions or songs list
                if not songs:
                    instructions_frame = ctk.CTkFrame(content_frame)
                    instructions_frame.pack(fill="x", padx=10, pady=10)
                    
                    instructions_text = "🎯 DROP ZONE - This playlist is empty\n\nTo add songs:\n1. Load Available Songs\n2. Select this playlist\n3. Click '➕ Add to Selected' on any song"
                    ctk.CTkLabel(instructions_frame, text=instructions_text, justify="left").pack(padx=10, pady=10)
                else:
                    ctk.CTkLabel(content_frame, text="🎵 Songs in Playlist:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(20,10))
                    
                    for i, song in enumerate(songs, 1):
                        song_frame = ctk.CTkFrame(content_frame)
                        song_frame.pack(fill="x", padx=10, pady=2)
                        song_frame.grid_columnconfigure(0, weight=1)
                        
                        # Song info
                        song_name = song.get('name', song.get('title', 'Unknown Song'))
                        song_id = song.get('id', 'N/A')
                        
                        info_text = f"{i}. {song_name}\nID: {song_id}"
                        ctk.CTkLabel(song_frame, text=info_text, justify="left").grid(row=0, column=0, padx=10, pady=5, sticky="w")
                        
                        # Remove button - tests DELETE /playlists/{id}/songs/{song_id}
                        ctk.CTkButton(song_frame, text="❌ Remove", width=80,
                                    command=lambda s_id=song_id, p_id=playlist_id: remove_song_from_playlist_proper(p_id, s_id)).grid(row=0, column=1, padx=10, pady=5, sticky="e")
                break

def remove_song_from_playlist_proper(playlist_id, song_id):
    """Remove a song from playlist - tests DELETE /playlists/{id}/songs/{song_id} endpoint."""
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        return
    
    log("Playlists", "info", f"Removing song {song_id} from playlist {playlist_id}")
    resp = make_api_request('Playlists', 'DELETE', f'/playlists/{playlist_id}/songs/{song_id}', token=cache.id_token)
    
    if resp and resp['status'] == 200:
        log("Playlists", "success", f"Removed song from playlist")
        # Refresh displays
        load_playlists_clean()
        cache = get_current_user_cache()
        if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id:
            show_playlist_details_proper(cache.playlists_selected_playlist)
    else:
        log("Playlists", "error", "Failed to remove song from playlist", payload=resp.get('content') if resp else 'N/A')

def delete_playlist_proper(playlist):
    """Delete a playlist with confirmation - tests DELETE /playlists/{id} endpoint."""
    playlist_id = playlist.get('id')
    playlist_name = playlist.get('name', 'Unknown')
    
    cache = get_current_user_cache()
    if not cache.id_token:
        log("Playlists", "warning", "Please authenticate first")
        return
    
    # Create confirmation dialog
    confirm_window = ctk.CTkToplevel()
    confirm_window.title("Confirm Deletion")
    confirm_window.geometry("400x200")
    confirm_window.transient()
    confirm_window.grab_set()
    
    # Center the window
    confirm_window.update_idletasks()
    x = (confirm_window.winfo_screenwidth() // 2) - (400 // 2)
    y = (confirm_window.winfo_screenheight() // 2) - (200 // 2)
    confirm_window.geometry(f"400x200+{x}+{y}")
    
    # Confirmation message
    ctk.CTkLabel(confirm_window, text="Delete Playlist?", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
    ctk.CTkLabel(confirm_window, text=f"Are you sure you want to delete:\n'{playlist_name}'?\n\nThis action cannot be undone.").pack(pady=10)
    
    # Buttons
    button_frame = ctk.CTkFrame(confirm_window)
    button_frame.pack(pady=20)
    
    def confirm_delete():
        confirm_window.destroy()
        log("Playlists", "info", f"Deleting playlist {playlist_name} ({playlist_id})")
        resp = make_api_request('Playlists', 'DELETE', f'/playlists/{playlist_id}', token=cache.id_token)
        
        if resp and resp['status'] == 200:
            log("Playlists", "success", f"Deleted playlist {playlist_name}")
            cache = get_current_user_cache()
            if cache.playlists_selected_playlist and cache.playlists_selected_playlist.get('id') == playlist_id:
                cache.playlists_selected_playlist = None
            load_playlists_clean()
        else:
            log("Playlists", "error", "Failed to delete playlist", payload=resp.get('content') if resp else 'N/A')
    
    def cancel_delete():
        confirm_window.destroy()
        log("Playlists", "info", "Playlist deletion cancelled")
    
    ctk.CTkButton(button_frame, text="Delete", command=confirm_delete, fg_color="red", hover_color="darkred").pack(side="left", padx=10)
    ctk.CTkButton(button_frame, text="Cancel", command=cancel_delete).pack(side="left", padx=10)

# Old function removed - replaced with clear_playlist_inputs()

# --- Client Class ---
def add_client_user():
    cache = get_current_user_cache()
    client_id = cache.client_user_index + 1
    SimulatedClient(client_id)
    cache.client_user_index += 1

class SimulatedClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.log_source = f"Client {self.client_id}"
        self.client_token = None
        self.ws_thread = None
        self.is_disconnecting = False
        self.last_image_etag = None
        self.last_image_bytes = None
        self.state_lock = threading.Lock()  # Prevent race conditions
        simulated_clients.append(self)
        
        self.client_window = ctk.CTkToplevel()
        self.client_window.title(f"Client {self.client_id}")
        self.client_window.geometry("500x700")
        self.client_window.protocol("WM_DELETE_WINDOW", self.disconnect)

        main_frame = ctk.CTkFrame(self.client_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        controls = ctk.CTkFrame(main_frame)
        controls.pack(fill="x", pady=5)
        ctk.CTkLabel(controls, text=f"Client {self.client_id}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        self.signin_button = ctk.CTkButton(controls, text="1. Sign In", command=self.get_client_token)
        self.signin_button.pack(pady=5, padx=10, fill="x")
        self.join_button = ctk.CTkButton(controls, text="2. Join Room (REST)", command=self.join_room_api, state="disabled")
        self.join_button.pack(pady=5, padx=10, fill="x")
        self.connect_button = ctk.CTkButton(controls, text="3. Connect (WebSocket)", command=self.connect, state="disabled")
        self.connect_button.pack(pady=5, padx=10, fill="x")
        
        self.song_display_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a")
        self.song_display_frame.pack(fill="both", expand=True, pady=10)
        ctk.CTkLabel(self.song_display_frame, text="Awaiting connection...").pack(expand=True)

        self.console_text = scrolledtext.ScrolledText(main_frame, height=10, bg="#2b2b2b", fg="white", state="disabled", font=("Courier", 10))
        self.console_text.pack(fill="x", pady=10, padx=5)
    
    def log(self, log_type, text, payload=None):
        def do_log():
            prefix_map = {"api_call": ">", "api_resp": "<", "ws_send": ">", "ws_recv": "<", "cache": "*", "info": "i", "success": "✓", "error": "✗"}
            prefix = prefix_map.get(log_type, "i")
            message = f"[{prefix}] {text}"
            if payload:
                payload_str = json.dumps(payload, indent=2) if isinstance(payload, dict) else str(payload)
                if len(payload_str) > 200: payload_str = payload_str[:200] + "..."
                message += f"\n  {payload_str}"

            self.console_text.config(state="normal")
            self.console_text.insert(tk.END, message + "\n")
            self.console_text.see(tk.END)
            self.console_text.config(state="disabled")
        if self.client_window.winfo_exists(): self.client_window.after(0, do_log)
    
    def get_client_token(self):
        user = TEST_USERS[self.client_id - 1]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {"email": user["email"], "password": user["password"], "returnSecureToken": True}
        
        self.log("api_call", f"Signing in as {user['email']}...")
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            self.client_token = resp.json().get("idToken")
            self.signin_button.configure(state="disabled", text=f"Signed in")
            self.join_button.configure(state="normal")
            self.log("success", "Authentication successful.")
        else:
            self.log("error", f"Auth failed: {resp.json().get('error', {}).get('message')}")

    def join_room_api(self):
        cache = get_current_user_cache()
        if not cache.room_id: self.log("error", "Host has not created a room."); return
        resp = make_api_request(self.log_source, 'POST', f'/rooms/{cache.room_id}/join', token=self.client_token)
        if resp and resp['status'] < 400:
            self.log("success", f"Joined room {cache.room_id} via REST.")
            self.join_button.configure(state="disabled")
            self.connect_button.configure(state="normal")
            # No longer need to call /sync - WebSocket will provide initial state
            self.log("info", "Room joined. Connect via WebSocket to receive real-time updates.")
        else:
            self.log("error", "Failed to join room.", payload=resp.get('content') if resp else 'N/A')

    def display_song(self, data):
        with self.state_lock:  # Prevent race conditions during UI updates
            for widget in self.song_display_frame.winfo_children(): widget.destroy()
            
            title = data.get('title', 'Unknown')
            page = data.get('current_page', 1)
            total_pages = data.get('total_pages', 1)
            image_etag = data.get('image_etag')
     
            ctk.CTkLabel(self.song_display_frame, text=f"{title} - Page {page}/{total_pages}").pack(pady=5)
            image_frame = ctk.CTkFrame(self.song_display_frame, fg_color="#333333")
            image_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Normalize both ETags for consistent comparison
            expected_normalized = _normalize_etag(image_etag) if image_etag else None
            cached_normalized = _normalize_etag(self.last_image_etag) if self.last_image_etag else None
            
            if expected_normalized and cached_normalized == expected_normalized and self.last_image_bytes:
                self.log("cache", f"ETag {expected_normalized[:10]}... matches cache. Using stored image.")
                display_image_bytes(image_frame, self.last_image_bytes, max_size=(450, 550))
            else:
                cache = get_current_user_cache()
                status, img_bytes, etag_hex = fetch_room_image(self.log_source, self.client_token, cache.room_id, self.last_image_etag)
                if status == 200 and img_bytes:
                    self.last_image_bytes = img_bytes
                    self.last_image_etag = etag_hex or expected_normalized
                    display_image_bytes(image_frame, img_bytes, max_size=(450, 550))
                elif status == 304 and self.last_image_bytes:
                    display_image_bytes(image_frame, self.last_image_bytes, max_size=(450, 550))
                else:
                    ctk.CTkLabel(image_frame, text="Image not available yet.").pack(expand=True)

    def handle_message(self, msg):
        try:
            data = json.loads(msg)
            self.log("ws_recv", f"Received message type '{data.get('type')}'", payload=data)
            # Also log to main console for debugging
            log(self.log_source, "ws_recv", f"Received message type '{data.get('type')}'", payload=data)
            
            msg_type = data.get("type")
            msg_data = data.get('data', {})
            
            if msg_type == "join_room_success":
                # Handle initial room state from WebSocket join
                room_state = data.get('room_state')
                if room_state and room_state.get('current_song'):
                    # Display initial room state
                    display_data = {
                        'title': room_state.get('song_details', {}).get('title', 'Unknown'),
                        'current_page': room_state.get('current_page', 1),
                        'total_pages': room_state.get('song_details', {}).get('total_pages', 1),
                        'image_etag': room_state.get('image_etag')
                    }
                    self.display_song(display_data)
                    self.log("info", "Received initial room state via WebSocket")
            elif msg_type in ["song_updated", "page_updated"]:
                self.display_song(msg_data)
            elif msg_type == "participant_joined":
                self.log("info", f"Participant {msg_data.get('user_id')} joined the room")
            elif msg_type == "participant_left":
                self.log("info", f"Participant {msg_data.get('user_id')} left the room")
            elif msg_type == "room_closed":
                self.log("warning", f"Room {msg_data.get('room_id', 'unknown')} was closed: {msg_data.get('reason', 'Unknown reason')}")
                # Clear display safely
                with self.state_lock:
                    for widget in self.song_display_frame.winfo_children(): 
                        widget.destroy()
                    ctk.CTkLabel(self.song_display_frame, text="Room closed by host").pack(expand=True)
            elif msg_type == "error":
                self.log("error", f"WebSocket error: {data.get('message', 'Unknown error')}")
            else:
                self.log("warning", f"Unhandled message type: {msg_type}")
        except json.JSONDecodeError as e:
            self.log("error", f"Failed to parse WebSocket message: {e}")
        except Exception as e:
            self.log("error", f"Error handling WebSocket message: {e}")

    async def _ws_client_loop(self):
        ws_url = _normalize_websocket_url(WEBSOCKET_URL, self.client_token)
        self.log("info", f"Connecting to WebSocket...")
        try:
            async with websockets.connect(ws_url) as websocket:
                if self.client_window.winfo_exists():
                    self.client_window.after(0, lambda: self.connect_button.configure(state="disabled"))
                self.log("success", "WebSocket connected.")
                cache = get_current_user_cache()
                join_payload = {"type": "join_room", "room_id": cache.room_id}
                await websocket.send(json.dumps(join_payload))
                self.log("ws_send", "Sent join_room message.", payload=join_payload)

                async for message in websocket:
                    if self.is_disconnecting: break
                    if self.client_window.winfo_exists():
                        self.client_window.after(0, self.handle_message, message)
        except Exception as e:
            self.log("error", f"WebSocket connection failed: {e}")
        finally:
            if self.client_window.winfo_exists():
                self.client_window.after(0, lambda: self.connect_button.configure(state="normal"))
            self.log("info", "WebSocket disconnected.")

    def connect(self):
        self.is_disconnecting = False
        self.ws_thread = threading.Thread(target=lambda: asyncio.run(self._ws_client_loop()), daemon=True)
        self.ws_thread.start()

    def disconnect(self):
        self.is_disconnecting = True
        if self.client_window.winfo_exists(): self.client_window.destroy()

# --- UI Setup ---
def clear_main_frame():
    for widget in main_frame.winfo_children(): widget.destroy()

def update_songs_console(message):
    """Update the songs tab console with a message."""
    try:
        for widget in songs_display_frame.winfo_children():
            widget.destroy()
        
        console_frame = ctk.CTkFrame(songs_display_frame)
        console_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(console_frame, text="Songs Console", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        console_text = ctk.CTkTextbox(console_frame, height=200)
        console_text.pack(fill="both", expand=True, padx=10, pady=10)
        console_text.insert("1.0", message)
        console_text.configure(state="disabled")
    except:
        pass  # Ignore if frame doesn't exist yet

def update_playlists_console(message):
    """Update the playlists tab console with a message."""
    try:
        for widget in playlists_display_frame.winfo_children():
            widget.destroy()
        
        console_frame = ctk.CTkFrame(playlists_display_frame)
        console_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(console_frame, text="Playlists Console", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        console_text = ctk.CTkTextbox(console_frame, height=200)
        console_text.pack(fill="both", expand=True, padx=10, pady=10)
        console_text.insert("1.0", message)
        console_text.configure(state="disabled")
    except:
        pass  # Ignore if frame doesn't exist yet

def show_educational_guide():
    guide_window = ctk.CTkToplevel(window)
    guide_window.title("Instructional Guide")
    guide_window.geometry("700x750")

    textbox = ctk.CTkTextbox(guide_window, wrap="word", font=("Arial", 14))
    textbox.pack(expand=True, fill="both", padx=15, pady=15)

    guide_text = """
### Core Workflow ###
This tool simulates the entire API flow:
1.  **Host Authenticates:** Clicks "Sign In" to get a JSON Web Token (JWT) from Firebase.
2.  **Host Creates Room:** Clicks "Create Room" (`POST /rooms/`) to establish a session.
3.  **Client Authenticates:** A client window clicks "Sign In" to get its own JWT.
4.  **Client Joins Room:** The client clicks "Join Room" (`POST /rooms/{id}/join`) to register with the room.
5.  **WebSocket Connection:** Both host and clients connect to the WebSocket server, passing their JWT for authentication. Upon joining, they immediately receive the current room state (song, page, etc.) via the `join_room_success` message.
6.  **Host Action:** The host selects a song (`POST /rooms/{id}/song`).
7.  **Server Push:** The server broadcasts a `song_updated` message to all clients in the room via WebSocket.
8.  **Client Reaction:** Clients receive the message, see it has a new `image_etag`, and make an API call (`GET /rooms/{id}/image`) to fetch the new image.

---
### Authentication: JWT ###
Every protected API call requires an `Authorization` header with a Bearer Token (JWT).
`Authorization: Bearer <your_jwt_token>`
This token proves the user's identity to the backend. This tool handles this automatically after you sign in.

---
### REST API vs. WebSocket ###
The two work together seamlessly:
*   **REST API (HTTP):** Used for **user-initiated actions**. These are one-time requests like creating a room, joining a room, or selecting a song. The user *does something*, and the app makes a request.
*   **WebSocket:** Used for **server-pushed updates** and **initial state delivery**. After joining a room via REST, the WebSocket connection provides the current room state immediately, then pushes real-time updates when the host makes changes. No separate sync call is needed!

---
### Songs & Playlists ###
The Songs tab provides comprehensive song management:
*   **Search:** Multiple search types including basic, substring, similarity, and full-text search
*   **Details:** View song metadata, page count, and individual pages
*   **Assets:** View song images and open PDFs in browser

The Playlists tab allows playlist management:
*   **Create:** Create new playlists with custom names
*   **Manage:** Add/remove songs, view playlist contents
*   **Delete:** Remove entire playlists

---
### Caching with ETags ###
To save bandwidth, the API uses ETag caching for images with improved normalization:
1.  When an image is first downloaded, the server includes an `ETag` header (e.g., `W/"abc123def"`). This is a unique identifier for that specific image version. The client stores this ETag.
2.  The next time the client needs the image, it sends a `If-None-Match: "abc123def"` header with its request.
3.  The server checks this ETag (handling both weak W/ and strong formats):
    *   If the image **has not changed**, the server replies with **`304 Not Modified`** and an empty body. The client knows it can safely use its cached version.
    *   If the image **has changed**, the server replies with **`200 OK`**, the new image data, and a new ETag.

Watch the `[CACHE LOGIC]` and `[API RESP]` logs in the consoles to see this in action!

---
### .env Configuration ###
For this tool to work, create a `.env` file in the same directory with your Firebase Web API Key:
`FIREBASE_API_KEY="AIzaSy...your...key"`
You can also add custom environment URLs:
`VM1_BASE_URL="http://your.vm.ip:8000/"`
`VM1_WS_URL="ws://your.vm.ip:8000/ws"`
    """
    textbox.insert("1.0", guide_text)
    textbox.configure(state="disabled")

# --- Main Application ---
def main():
    global window, main_frame, output, song_dropdown_var
    
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    window = ctk.CTk()
    window.title("Music Room API Testing GUI")
    window.geometry("1200x800")
    
    # Create main layout
    main_container = ctk.CTkFrame(window)
    main_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create paned window for main content and console
    main_container.grid_rowconfigure(0, weight=3)  # Main content gets more space
    main_container.grid_rowconfigure(1, weight=1)  # Console gets less space
    main_container.grid_columnconfigure(0, weight=1)
    
    # Main content area
    main_frame = ctk.CTkFrame(main_container)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    
    # Console area
    console_frame = ctk.CTkFrame(main_container)
    console_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    
    # Console setup
    ctk.CTkLabel(console_frame, text="Console Output", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
    output = scrolledtext.ScrolledText(console_frame, height=15, bg="#2b2b2b", fg="white", state="disabled", font=("Courier", 10))
    output.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Configure text tags for colored output
    output.tag_configure("api_call", foreground="#4CAF50")
    output.tag_configure("api_resp", foreground="#2196F3")
    output.tag_configure("ws_send", foreground="#FF9800")
    output.tag_configure("ws_recv", foreground="#9C27B0")
    output.tag_configure("cache", foreground="#00BCD4")
    output.tag_configure("info", foreground="#FFFFFF")
    output.tag_configure("success", foreground="#4CAF50")
    output.tag_configure("error", foreground="#F44336")
    output.tag_configure("warning", foreground="#FF5722")
    
    # Initialize song dropdown variable
    song_dropdown_var = ctk.StringVar()
    
    # Start with mode selection
    setup_mode_selection_ui()
    
    # Start the GUI
    window.mainloop()

if __name__ == "__main__":
    main()