import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import json
import sys
import time
import os
import math
import pygame
import socket
import queue

# --- Global Variables (for Pygame Mixer and Sound) ---
# Initialize Pygame mixer once globally if all sounds are loaded upfront.
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

script_dir = os.path.dirname(__file__)
sfx_dir = os.path.join(script_dir, "Sfx")
tada_sound = None
try:
    tada_sound_path = os.path.join(sfx_dir, "Tada.mp3")
    if os.path.exists(tada_sound_path):
        tada_sound = pygame.mixer.Sound(tada_sound_path)
        tada_sound.set_volume(0.6)
    else:
        print(f"[{time.strftime('%H:%M:%S')}] Peringatan: File suara 'Tada!.mp3' tidak ditemukan di '{tada_sound_path}'.")
except pygame.error as e:
    print(f"[{time.strftime('%H:%M:%S')}] Error memuat suara 'Tada!.mp3': {e}")
    tada_sound = None

# --- Game Constants (Defined here for server-side logic) ---
GAME_WIDTH = 900 # Corresponds to client's WIDTH
GAME_HEIGHT = 600 # Corresponds to client's HEIGHT
PLAYER_SIZE = 30 # Corresponds to client's player size for collision
BULLET_SPEED = 15
BULLET_SIZE = 5

# --- Language Dictionaries (Tetap global untuk akses mudah) ---
LANG_EN = {
    "server_name_prompt": "Enter a name for this server (e.g., qwertino): ",
    "server_password_prompt": "Enter a password for the server (leave blank for no password): ",
    "server_started": "Server '{server_name}' started. Player Limit: {limit}.",
    "share_address": "IP: {host}:{port}",
    "unknown_command": "Unknown command. Use: kick [username], op [username], unop [username], check [username], list, sertask, or playerlimit [number]",
    "kicking_player": "Kicking {name}",
    "player_not_found": "Player {name} not found.",
    "player_op_success": "{name} is now an operator.",
    "player_op_fail_offline": "Player {name} not found or not online.",
    "player_unop_success": "{name} is no longer an operator.",
    "player_unop_fail_not_op": "{name} is not an operator.",
    "shutting_down_server": "Shutting down server",
    "server_stopped": "Server stopped.",
    "connection_refused_server_bind_error": "Failed to bind server on {host}:{port}. Error: {error}",
    "eof_received_command_listener": "EOF received, shutting down command listener.",
    "unexpected_command_error": "Error in command listener: {error}",
    "client_connected": "{username} connected from {addr}",
    "client_disconnected": "{username} disconnected",
    "invalid_json_received": "Invalid JSON received from {addr}. Disconnecting.",
    "client_forcibly_disconnected": "Client {username_or_addr} forcibly disconnected.",
    "client_handling_error": "Error while handling client {username_or_addr}: {error}",
    "operator_kill_attempt": "{username} tried to kill operator {target} (failed).",
    "player_killed_server_log": "{killer} killed {target}",
    "player_respawned_server_log": "{username} respawned.",
    "operator_respawn_attempt": "Operator {username} tried to respawn (already alive).",
    "operator_removed_on_disconnect": "{username} removed from operator list.",
    "op_message_client": "You are now an operator!",
    "unop_message_client": "You are no longer an operator.",
    "restarting_server": "Restarting server...",
    "language_selection": "Select language (Pilih bahasa):",
    "type_eng": "  Type ENG for English",
    "type_id": "  Ketik ID untuk Indonesia",
    "your_choice": "Your choice (Pilihan Anda): ",
    "player_status_title": "--- Player Status for {username} ---",
    "player_status_online_alive": "{username} is ONLINE and ALIVE.",
    "player_status_online_dead": "{username} is ONLINE and DEAD.",
    "player_status_offline": "{username} is OFFLINE.",
    "player_status_op": "({username} is an Operator)",
    "player_list_title": "--- Currently Online Players ({count}) ---",
    "player_list_empty": "No players currently online.",
    "player_list_item": "{index}. {username} (Status: {status}{operator_suffix})",
    "status_alive": "ALIVE",
    "status_dead": "DEAD",
    "is_operator": " (OP)",
    "password_incorrect": "Incorrect password. Disconnecting.",
    "password_required": "Password required for this server.",
    "server_tasks_prompt": "What do you want to do with this server?",
    "task_shutdown": "Shutdown (1)",
    "task_restart": "Restart (2)",
    "task_kick_all": "Kick all (3)",
    "task_set_limit": "Set Player Limit (4)",
    "type_choice": "Type: ",
    "invalid_task_choice": "Invalid choice. Please type 1, 2, 3, or 4.",
    "kicking_all_players": "Kicking all players...",
    "commands_for_server_title": "Commands For Server !",
    "player_limit_prompt": "Enter max players (0 for no limit): ",
    "player_limit_set": "Player limit set to {limit}.",
    "limit_invalid_number": "Invalid number for limit. Please enter a whole number.",
    "limit_invalid_negative": "Player limit cannot be negative.",
    "server_full_kick_reason": "Server is full! Players: {current}/{max}",
    "connection_rejected_full": "Connection from {addr} rejected. Server is full.",
    "username_already_in_use": "Username '{username}' is already in use.",
    "edit_server_settings_title": "Edit Server Settings",
    "edit_server_name_label": "Server Name:",
    "edit_server_password_label": "Server Password:",
    "confirm_save_title": "Confirm Save",
    "confirm_save_message": "Are you sure you want to save these changes?",
    "changes_saved_message": "Server settings saved. Restart server to apply changes to existing connections.",
    "changes_discarded_message": "Changes discarded."
}

LANG_ID = {
    "server_name_prompt": "Masukkan nama untuk server ini (contoh: qwertino): ",
    "server_password_prompt": "Masukkan password untuk server (kosongkan jika tanpa password): ",
    "server_started": "Server '{server_name}' dimulai. Batas Pemain: {limit}.",
    "share_address": "IP: {host}:{port}",
    "unknown_command": "Perintah tidak dikenal. Gunakan: kick [username], op [username], unop [username], check [username], list, sertask, atau playerlimit [angka]",
    "kicking_player": "Mengeluarkan {name}",
    "player_not_found": "Pemain {name} tidak ditemukan.",
    "player_op_success": "{name} sekarang adalah operator.",
    "player_op_fail_offline": "Pemain {name} tidak ditemukan atau tidak online.",
    "player_unop_success": "{name} bukan lagi operator.",
    "player_unop_fail_not_op": "{name} bukan operator.",
    "shutting_down_server": "Mematikan server",
    "server_stopped": "Server dihentikan.",
    "connection_refused_server_bind_error": "Gagal mengikat server pada {host}:{port}. Error: {error}",
    "eof_received_command_listener": "EOF diterima, mematikan pendengar perintah.",
    "unexpected_command_error": "Error dalam pendengar perintah: {error}",
    "client_connected": "{username} terhubung dari {addr}",
    "client_disconnected": "{username} terputus",
    "invalid_json_received": "JSON tidak valid diterima dari {addr}. Memutus koneksi.",
    "client_forcibly_disconnected": "Klien {username_or_addr} terputus secara paksa.",
    "client_handling_error": "Error saat menangani klien {username_or_addr}: {error}",
    "operator_kill_attempt": "{username} mencoba membunuh operator {target} (gagal).",
    "player_killed_server_log": "{killer} membunuh {target}",
    "player_respawned_server_log": "{username} hidup kembali.",
    "operator_respawn_attempt": "Operator {username} mencoba respawn (sudah hidup).",
    "operator_removed_on_disconnect": "{username} dihapus dari daftar operator.",
    "op_message_client": "Anda sekarang adalah operator!",
    "unop_message_client": "Anda bukan lagi operator.",
    "restarting_server": "Memulai ulang server...",
    "language_selection": "Pilih bahasa (Select language):",
    "type_eng": "  Ketik ENG untuk English",
    "type_id": "  Ketik ID untuk Indonesia",
    "your_choice": "Pilihan Anda (Your choice): ",
    "player_status_title": "--- Status Pemain untuk {username} ---",
    "player_status_online_alive": "{username} ONLINE dan HIDUP.",
    "player_status_online_dead": "{username} ONLINE dan MATI.",
    "player_status_offline": "{username} OFFLINE.",
    "player_status_op": "({username} adalah Operator)",
    "player_list_title": "--- Pemain Online Saat Ini ({count}) ---",
    "player_list_empty": "Tidak ada pemain online saat ini.",
    "player_list_item": "{index}. {username} (Status: {status}{operator_suffix})",
    "status_alive": "HIDUP",
    "status_dead": "MATI",
    "is_operator": " (OP)",
    "password_incorrect": "Password salah. Memutus koneksi.",
    "password_required": "Password dibutuhkan untuk server ini.",
    "server_tasks_prompt": "Apa yang Anda lakukan ke server ini?",
    "task_shutdown": "ShutDown (1)",
    "task_restart": "Restart (2)",
    "task_kick_all": "Kick all (3)",
    "task_set_limit": "Atur Batas Pemain (4)",
    "type_choice": "Ketik: ",
    "invalid_task_choice": "Pilihan tidak valid. Silakan ketik 1, 2, 3, atau 4.",
    "kicking_all_players": "Mengeluarkan semua pemain...",
    "commands_for_server_title": "Perintah Untuk Server !",
    "player_limit_prompt": "Masukkan batas pemain maksimal (0 untuk tanpa batas): ",
    "player_limit_set": "Batas pemain diatur ke {limit}.",
    "limit_invalid_number": "Angka tidak valid untuk batas. Harap masukkan angka bulat.",
    "limit_invalid_negative": "Batas pemain tidak bisa negatif.",
    "server_full_kick_reason": "Server penuh! Pemain: {current}/{max}",
    "connection_rejected_full": "Koneksi dari {addr} ditolak. Server penuh.",
    "username_already_in_use": "Username '{username}' sudah digunakan.",
    "edit_server_settings_title": "Edit Pengaturan Server",
    "edit_server_name_label": "Nama Server:",
    "edit_server_password_label": "Password Server:",
    "confirm_save_title": "Konfirmasi Simpan",
    "confirm_save_message": "Anda yakin ingin menyimpan perubahan ini?",
    "changes_saved_message": "Pengaturan server disimpan. Restart server untuk menerapkan perubahan pada koneksi yang sudah ada.",
    "changes_discarded_message": "Perubahan dibatalkan."
}

current_language = LANG_EN # Default language

def set_language(lang_code):
    """Sets the global language dictionary."""
    global current_language
    if lang_code.upper() == "ENG":
        current_language = LANG_EN
    elif lang_code.upper() == "ID":
        current_language = LANG_ID
    else:
        current_language = LANG_EN # Default to English if invalid input

def get_text(key, **kwargs):
    """Retrieves localized text."""
    if not current_language:
        set_language("ENG") # Ensure a language is set
    return current_language.get(key, f"MISSING_TEXT_KEY[{key}]").format(**kwargs)

class ConterbitServerApp:
    def __init__(self, master):
        self.master = master
        master.title("Conterbit Server Manager")
        master.geometry("1000x650")

        # --- Server State Variables ---
        self.clients = {} # Stores {username: socket_object}
        self.players = {} # Stores {username: {"x": X, "y": Y, "shoot": False, "angle": A}}
        self.alive_status = {} # Stores {username: True/False}
        self.operators = set() # Stores {username, ...}
        self.player_kills = {} # Stores {username: kill_count}

        self.server_running = False
        self.lock = threading.Lock() # For thread-safe access to shared data
        self.server_name = "DefaultServer"
        self.server_password = None
        self.max_players = 0 # 0 means no player limit
        
        self.bullet_data = {
            "active": False,
            "x": 0,
            "y": 0,
            "angle": 0,
            "owner": "",
            "speed": BULLET_SPEED,
            "size": BULLET_SIZE
        }
        self.server_socket = None
        self.server_accept_thread = None
        self.server_port = 5555
        self.server_host = self._get_local_ip()

        self.log_queue = queue.Queue() # Queue for logging messages from server threads to GUI

        # --- UI Setup ---
        self._setup_ui()

        # Start periodic UI updates
        self.master.after(100, self._update_ui)
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self):
        # Top Bar for Server Control
        self.top_bar_frame = tk.Frame(self.master, bd=2, relief="groove")
        self.top_bar_frame.pack(fill=tk.X, pady=(0, 5), padx=10)

        self.start_button = tk.Button(self.top_bar_frame, text="Start Server", command=self.start_server, bg="green", fg="white", font=("Arial", 10, "bold"))
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.top_bar_frame, text="Stop Server", command=self.stop_server, bg="red", fg="white", font=("Arial", 10, "bold"), state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.restart_button = tk.Button(self.top_bar_frame, text="Restart Server", command=self.restart_server, bg="orange", fg="white", font=("Arial", 10, "bold"), state=tk.DISABLED)
        self.restart_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_button = tk.Button(self.top_bar_frame, text="Edit", command=self._edit_server_settings, bg="blue", fg="white", font=("Arial", 10, "bold"), state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        # --- Main content frames (Left and Right) ---
        self.main_content_frame = tk.Frame(self.master)
        self.main_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left Panel (Stats and Players)
        self.left_panel = tk.Frame(self.main_content_frame, width=280, bg="#f0f0f0", bd=2, relief="groove")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        self.left_panel.pack_propagate(False)

        # Stats Section
        self.stats_label = tk.Label(self.left_panel, text="Server Stats", font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.stats_label.pack(pady=(5, 2))

        self.stats_text = scrolledtext.ScrolledText(self.left_panel, wrap=tk.WORD, width=35, height=8, font=("Consolas", 9), bg="#e0e0e0")
        self.stats_text.pack(padx=5, pady=5, fill=tk.X)
        self.stats_text.config(state=tk.DISABLED)

        # Player List Section
        self.players_label = tk.Label(self.left_panel, text="Online Players", font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.players_label.pack(pady=(10, 2))

        self.player_list_text = scrolledtext.ScrolledText(self.left_panel, wrap=tk.WORD, width=35, height=20, font=("Arial", 10), bg="white")
        self.player_list_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.player_list_text.config(state=tk.DISABLED)

        # Right Panel (Log and Chat, Command Bar)
        self.right_panel = tk.Frame(self.main_content_frame, bg="#e0e0e0", bd=2, relief="groove")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Log and Chat Section
        self.log_label = tk.Label(self.right_panel, text="Server Log & Chat", font=("Arial", 12, "bold"), bg="#e0e0e0")
        self.log_label.pack(pady=(5, 2))

        self.log_text = scrolledtext.ScrolledText(self.right_panel, wrap=tk.WORD, font=("Consolas", 9), bg="black", fg="lightgray", insertbackground="white")
        self.log_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

        # Command Bar Section
        self.command_frame = tk.Frame(self.right_panel, bg="#e0e0e0")
        self.command_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.command_label = tk.Label(self.command_frame, text="Server Command:", font=("Arial", 10), bg="#e0e0e0")
        self.command_label.pack(side=tk.LEFT, padx=(0, 5))

        self.command_entry = tk.Entry(self.command_frame, font=("Arial", 10), width=50, bg="white", fg="black")
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self._handle_command_input)

        self.send_button = tk.Button(self.command_frame, text="Send", command=self._handle_command_input, font=("Arial", 10), bg="#d0d0d0")
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

    def _log_to_ui(self, message):
        """Puts a message into the queue to be displayed in the UI log."""
        self.log_queue.put(f"[{time.strftime('%H:%M:%S')}] {message}")

    def _update_ui(self):
        """Periodically pulls messages from the log queue and updates UI elements."""
        # Update log
        while not self.log_queue.empty():
            message = self.log_queue.get_nowait()
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        # Update stats and player list
        self._update_stats_and_players()

        # Reschedule next update
        self.master.after(100, self._update_ui)

    def _update_stats_and_players(self):
        with self.lock:
            # Update Stats
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"Server Name: {self.server_name}\n")
            self.stats_text.insert(tk.END, f"IP Address: {self.server_host}:{self.server_port}\n")
            self.stats_text.insert(tk.END, f"Players: {len(self.players)} / {('Unlimited' if self.max_players == 0 else self.max_players)}\n")
            
            # Bullet info
            self.stats_text.insert(tk.END, f"Bullet Active: {self.bullet_data['active']}\n")
            if self.bullet_data["active"]:
                self.stats_text.insert(tk.END, f"  Owner: {self.bullet_data['owner']}\n")
                self.stats_text.insert(tk.END, f"  Pos: ({self.bullet_data['x']:.0f}, {self.bullet_data['y']:.0f})\n")
            
            self.stats_text.config(state=tk.DISABLED)

            # Update Player List
            self.player_list_text.config(state=tk.NORMAL)
            self.player_list_text.delete(1.0, tk.END)
            
            if not self.players:
                self.player_list_text.insert(tk.END, get_text('player_list_empty'))
            else:
                # Sort players alphabetically for consistent display
                sorted_players = sorted(self.players.keys())
                for uname in sorted_players:
                    info = self.players[uname] # Get info for player
                    status = get_text('status_alive') if self.alive_status.get(uname, False) else get_text('status_dead')
                    op_suffix = get_text('is_operator') if uname in self.operators else ""
                    kills_info = f" (Kills: {self.player_kills.get(uname, 0)})"
                    self.player_list_text.insert(tk.END, f"- {uname} ({status}{op_suffix}){kills_info}\n")
            self.player_list_text.config(state=tk.DISABLED)

    def _get_local_ip(self):
        """Gets the local IP address of the machine."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            IP = s.getsockname()[0]
        except Exception:
            IP = "127.0.0.1" # Fallback to localhost
        finally:
            s.close()
        return IP

    def start_server(self):
        if self.server_running:
            self._log_to_ui("[UI]: Server is already running.")
            return

        # Prompt for server name and password if not set
        if not self.server_name or self.server_password is None:
            temp_name = simpledialog.askstring("Server Setup", get_text("server_name_prompt"), initialvalue=self.server_name)
            if temp_name is None: return # User cancelled
            self.server_name = temp_name if temp_name else "DefaultServer"

            temp_password = simpledialog.askstring("Server Setup", get_text("server_password_prompt"), show='*')
            self.server_password = temp_password if temp_password else None

        self.server_running = True
        limit_display = 'Unlimited' if self.max_players == 0 else self.max_players
        self._log_to_ui(get_text('server_started', server_name=self.server_name, limit=limit_display))
        self._log_to_ui(get_text('share_address', host=self.server_host, port=self.server_port))

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.server_host, self.server_port))
            self.server_socket.listen()
        except Exception as e:
            self._log_to_ui(get_text('connection_refused_server_bind_error', host=self.server_host, port=self.server_port, error=e))
            self.server_running = False
            return

        self.server_accept_thread = threading.Thread(target=self._server_accept_loop, daemon=True)
        self.server_accept_thread.start()

        # Enable/Disable buttons
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)
        self.edit_button.config(state=tk.NORMAL)

    def _server_accept_loop(self):
        """Main loop for the server to accept new client connections."""
        while self.server_running:
            try:
                self.server_socket.settimeout(0.5) # Small timeout to allow checking server_running flag
                conn, addr = self.server_socket.accept()
                
                with self.lock:
                    if self.max_players > 0 and len(self.players) >= self.max_players:
                        self._log_to_ui(get_text('connection_rejected_full', addr=addr))
                        kick_reason = get_text("server_full_kick_reason", current=len(self.players), max=self.max_players)
                        conn.send(json.dumps({"kick": True, "reason": kick_reason}).encode())
                        conn.close()
                        continue
                
                client_thread = threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True)
                client_thread.start()

            except socket.timeout:
                pass # Expected, just means no new connection in this interval
            except Exception as e:
                if self.server_running: # Only log if server is intended to be running
                    self._log_to_ui(f"Error in server accept loop: {e}")
                break # Exit loop if a critical error occurs or server stops

    def _handle_client(self, conn, addr):
        username = None
        try:
            data = conn.recv(1024).decode()
            initial_data = json.loads(data)

            username = initial_data.get("username")
            client_password = initial_data.get("password")

            with self.lock:
                if not username or username in self.players: # Check for empty or duplicate username
                    reason = get_text('username_already_in_use', username=username) if username else "Invalid username."
                    self._log_to_ui(reason)
                    conn.send(json.dumps({"kick": True, "reason": reason}).encode())
                    conn.close()
                    return

                # Password checks
                if self.server_password and client_password != self.server_password:
                    self._log_to_ui(f"{addr} tried to connect with incorrect password.")
                    conn.send(json.dumps({"kick": True, "reason": get_text("password_incorrect")}).encode())
                    conn.close()
                    return
                elif self.server_password and not client_password:
                    self._log_to_ui(f"{addr} tried to connect without password (password required).")
                    conn.send(json.dumps({"kick": True, "reason": get_text("password_required")}).encode())
                    conn.close()
                    return

                # Register player
                self.players[username] = {"x": GAME_WIDTH // 2, "y": GAME_HEIGHT // 2, "shoot": False, "angle": 0} # Initial position
                self.alive_status[username] = True
                self.clients[username] = conn
                self.player_kills[username] = 0

            self._log_to_ui(get_text('client_connected', username=username, addr=addr))

            # Main loop for receiving data from this client
            while self.server_running:
                data = conn.recv(4096).decode()
                if not data: # Client disconnected
                    break

                data_json = json.loads(data)

                # ==== HANDLE CHAT MESSAGES ====
                if "chat" in data_json:
                    chat_text = data_json["chat"].strip()
                    if chat_text:
                        chat_full = f"{username}> {chat_text}"
                        self._log_to_ui(chat_full)
                        # Broadcast chat message to all connected clients
                        for c_username, c_conn in list(self.clients.items()):
                            try:
                                c_conn.send(json.dumps({"chat": chat_full}).encode())
                            except Exception as e:
                                self._log_to_ui(f"Failed to send chat to {c_username}: {e}")
                    continue # Continue to next loop iteration, don't process as game data

                # ==== HANDLE GAME STATE UPDATES ====
                with self.lock:
                    # Player shooting logic
                    if data_json.get("shoot") and not self.bullet_data["active"]:
                        player_x = self.players[username]["x"]
                        player_y = self.players[username]["y"]
                        player_angle = data_json.get("angle", 0)
                        
                        self.bullet_data["active"] = True
                        # Start bullet slightly ahead of player's center in the direction of fire
                        self.bullet_data["x"] = player_x + (PLAYER_SIZE / 2 + BULLET_SIZE) * math.cos(player_angle)
                        self.bullet_data["y"] = player_y + (PLAYER_SIZE / 2 + BULLET_SIZE) * math.sin(player_angle)
                        self.bullet_data["angle"] = player_angle
                        self.bullet_data["owner"] = username
                
                    # Update player position if alive or operator
                    if self.alive_status.get(username, False) or username in self.operators:
                        self.players[username].update({
                            "x": data_json["x"],
                            "y": data_json["y"],
                            "angle": data_json["angle"]
                        })
                    # Handle respawn request for non-operators
                    elif username in self.players and not self.alive_status.get(username, False):
                        if username not in self.operators: # Only allow respawn if not an operator
                            self.alive_status[username] = True
                            self.players[username].update({
                                "x": data_json["x"], # Client sends its desired respawn pos
                                "y": data_json["y"],
                                "angle": data_json["angle"]
                            })
                            self._log_to_ui(get_text('player_respawned_server_log', username=username))

                    # Update bullet position (regardless of who shot it)
                    if self.bullet_data["active"]:
                        self.bullet_data["x"] += self.bullet_data["speed"] * math.cos(self.bullet_data["angle"])
                        self.bullet_data["y"] += self.bullet_data["speed"] * math.sin(self.bullet_data["angle"])

                        # Check if bullet is out of bounds (using game area constants)
                        if not (0 <= self.bullet_data["x"] <= GAME_WIDTH and 0 <= self.bullet_data["y"] <= GAME_HEIGHT):
                            self.bullet_data["active"] = False
                            
                        # Check for bullet collision with players (only if bullet is still active after boundary check)
                        if self.bullet_data["active"]:
                            for target_username, target_info in list(self.players.items()): # Iterate on a copy for safe modification
                                if target_username == self.bullet_data["owner"] or \
                                   target_username in self.operators or \
                                   not self.alive_status.get(target_username, False):
                                    continue # Skip owner, operators, and already dead players

                                # Basic AABB (Axis-Aligned Bounding Box) collision check
                                # Player is a square, bullet is a circle.
                                # Find the closest point on the player's square to the bullet's center.
                                closest_x = max(target_info["x"] - PLAYER_SIZE / 2, min(self.bullet_data["x"], target_info["x"] + PLAYER_SIZE / 2))
                                closest_y = max(target_info["y"] - PLAYER_SIZE / 2, min(self.bullet_data["y"], target_info["y"] + PLAYER_SIZE / 2))

                                # Calculate distance between closest point and bullet center
                                distance_x = self.bullet_data["x"] - closest_x
                                distance_y = self.bullet_data["y"] - closest_y
                                distance_squared = (distance_x * distance_x) + (distance_y * distance_y)

                                if distance_squared < (self.bullet_data["size"] * self.bullet_data["size"]): # Collision detected
                                    self.alive_status[target_username] = False
                                    # Reset target player's position (server-side for consistency)
                                    self.players[target_username]["x"] = GAME_WIDTH // 2
                                    self.players[target_username]["y"] = GAME_HEIGHT // 2
                                    self.players[target_username]["shoot"] = False
                                    self.players[target_username]["angle"] = 0 # Reset angle
                                    
                                    self.bullet_data["active"] = False # Bullet "dies" on hit
                                    self._log_to_ui(get_text('player_killed_server_log', killer=self.bullet_data['owner'], target=target_username))
                                    
                                    # Update kill count for the owner of the bullet
                                    if self.bullet_data["owner"] in self.player_kills:
                                        self.player_kills[self.bullet_data["owner"]] += 1
                                    else:
                                        self.player_kills[self.bullet_data["owner"]] = 1 # First kill
                                    self._log_to_ui(f"Kill Score for {self.bullet_data['owner']}: {self.player_kills[self.bullet_data['owner']]}")
                                    
                                    if tada_sound:
                                        tada_sound.play() # Play sound on kill
                                    break # Only hit one player per bullet

                    # Prepare data to send to all clients (game state update)
                    send_data_dict = {
                        "players": self.players,
                        "alive": self.alive_status,
                        "operators": list(self.operators),
                        "bullet": self.bullet_data,
                        "kills": self.player_kills # Send kill counts
                    }
                    if "ping_request" in data_json and data_json["ping_request"]:
                        send_data_dict["ping"] = True
                    
                    # Always include server info
                    send_data_dict["server_info"] = {
                        "name": self.server_name,
                        "ip": self.server_host,
                        "max_players": self.max_players,
                        "current_players": len(self.players)
                    }

                    send_data = json.dumps(send_data_dict).encode()
                    # Send updated game state to all connected clients
                    for c_username, c_conn in list(self.clients.items()):
                        try:
                            c_conn.send(send_data)
                        except Exception as send_e:
                            self._log_to_ui(f"Error sending data to {c_username}: {send_e}")
                            self._remove_client(c_username) # Client might have disconnected, remove them

        except json.JSONDecodeError:
            self._log_to_ui(get_text('invalid_json_received', addr=addr))
        except ConnectionResetError:
            self._log_to_ui(get_text('client_forcibly_disconnected', username_or_addr=(username if username else addr)))
        except Exception as e:
            self._log_to_ui(get_text('client_handling_error', username_or_addr=(username if username else addr), error=e))
        finally:
            self._log_to_ui(get_text('client_disconnected', username=(username if username else addr)))
            if username:
                self._remove_client(username)

    def _remove_client(self, username):
        with self.lock:
            if username in self.clients:
                try:
                    self.clients[username].close()
                except:
                    pass # Socket might already be closed
                del self.clients[username]
            if username in self.players:
                del self.players[username]
            if username in self.alive_status:
                del self.alive_status[username]
            if username in self.operators:
                self.operators.remove(username)
                self._log_to_ui(get_text('operator_removed_on_disconnect', username=username))
            if username in self.player_kills:
                del self.player_kills[username]

    def stop_server(self):
        if not self.server_running:
            self._log_to_ui("[UI]: Server is not running.")
            return

        self._log_to_ui(get_text('shutting_down_server'))
        self.server_running = False

        # Send shutdown signal to all clients and close their connections
        with self.lock:
            for c_username, c_conn in list(self.clients.items()):
                try:
                    c_conn.send(json.dumps({"shutdown": True}).encode())
                    c_conn.close()
                except Exception as e:
                    self._log_to_ui(f"Error sending shutdown to {c_username}: {e}")
            # Clear all game state data
            self.clients.clear()
            self.players.clear()
            self.alive_status.clear()
            self.operators.clear()
            self.player_kills.clear()
            self.bullet_data["active"] = False # Reset bullet on shutdown

        # Close the server listening socket
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
                self.server_socket.close()
            except OSError as e:
                self._log_to_ui(f"Error shutting down server socket: {e}")
            self.server_socket = None
        
        # Wait for the accept thread to finish
        if self.server_accept_thread and self.server_accept_thread.is_alive():
            self.server_accept_thread.join(timeout=2)

        self._log_to_ui(get_text('server_stopped'))
        # Update UI button states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)
        self.edit_button.config(state=tk.DISABLED)

    def restart_server(self):
        self._log_to_ui(get_text('restarting_server'))
        self.stop_server() # Stop gracefully first
        self.master.after(1000, self.start_server) # Wait 1 second before restarting

    def _edit_server_settings(self):
        """Opens a pop-up window to edit server name and password."""
        edit_window = tk.Toplevel(self.master)
        edit_window.title(get_text("edit_server_settings_title"))
        edit_window.geometry("350x200")
        edit_window.transient(self.master) # Make it modal
        edit_window.grab_set()

        # Server Name
        tk.Label(edit_window, text=get_text("edit_server_name_label"), font=("Arial", 10)).pack(pady=(10, 2))
        server_name_entry = tk.Entry(edit_window, width=40, font=("Arial", 10))
        server_name_entry.insert(0, self.server_name)
        server_name_entry.pack(pady=2)

        # Server Password
        tk.Label(edit_window, text=get_text("edit_server_password_label"), font=("Arial", 10)).pack(pady=(10, 2))
        server_password_entry = tk.Entry(edit_window, width=40, show="*", font=("Arial", 10))
        # Display a placeholder if password exists, otherwise leave empty
        if self.server_password:
            server_password_entry.insert(0, "********")
        server_password_entry.pack(pady=2)

        def save_settings():
            new_name = server_name_entry.get().strip()
            new_password_raw = server_password_entry.get()
            
            # Determine new password based on input and existing password
            if self.server_password and new_password_raw == "********":
                new_password = self.server_password # User didn't change, keep old
            elif new_password_raw == "":
                new_password = None # User explicitly cleared
            else:
                new_password = new_password_raw # New password entered

            confirm = messagebox.askyesno(
                get_text("confirm_save_title"),
                get_text("confirm_save_message"),
                parent=edit_window
            )

            if confirm:
                with self.lock:
                    self.server_name = new_name if new_name else "DefaultServer"
                    self.server_password = new_password
                
                self._log_to_ui(get_text("changes_saved_message"))
                edit_window.destroy()
            else:
                self._log_to_ui(get_text("changes_discarded_message"))
                edit_window.destroy()
                # If changes are discarded, user might want to re-edit immediately
                # self.master.after(100, self._edit_server_settings) # Option to reopen

        tk.Button(edit_window, text="OK", command=save_settings, font=("Arial", 10), bg="#d0d0d0").pack(pady=10)

    def _handle_command_input(self, event=None):
        command = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END) # Clear input field immediately

        if not command:
            return

        self._log_to_ui(f"[UI Command]: {command}")

        cmd_parts = command.split(" ", 1)
        cmd_name = cmd_parts[0].lower()
        cmd_arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

        with self.lock: # Ensure thread safety when modifying server state
            if cmd_name == "kick":
                name = cmd_arg
                if name in self.clients:
                    self._log_to_ui(get_text('kicking_player', name=name))
                    try:
                        self.clients[name].send(json.dumps({"kick": True}).encode())
                        self.clients[name].close()
                    except Exception as e:
                        self._log_to_ui(f"Error sending kick or closing socket for {name}: {e}")
                    self._remove_client(name)
                else:
                    self._log_to_ui(get_text('player_not_found', name=name))
            elif cmd_name == "op":
                name = cmd_arg
                if name in self.players:
                    self.operators.add(name)
                    self._log_to_ui(get_text('player_op_success', name=name))
                    if name in self.clients:
                        try:
                            self.clients[name].send(json.dumps({"message": get_text("op_message_client")}).encode())
                        except: pass
                else:
                    self._log_to_ui(get_text('player_op_fail_offline', name=name))
            elif cmd_name == "unop":
                name = cmd_arg
                if name in self.operators:
                    self.operators.remove(name)
                    self._log_to_ui(get_text('player_unop_success', name=name))
                    if name in self.clients:
                        try:
                            self.clients[name].send(json.dumps({"message": get_text("unop_message_client")}).encode())
                        except: pass
                else:
                    self._log_to_ui(get_text('player_unop_fail_not_op', name=name))
            elif cmd_name == "sertask":
                self._show_server_tasks_menu()
            elif cmd_name == "check":
                target_username = cmd_arg
                self._log_to_ui(get_text('player_status_title', username=target_username))
                if target_username in self.players: # Check players dictionary, not just clients
                    status_msg = get_text('player_status_online_alive', username=target_username) if self.alive_status.get(target_username, False) else get_text('player_status_online_dead', username=target_username)
                    self._log_to_ui(status_msg)
                    if target_username in self.operators:
                        self._log_to_ui(get_text('player_status_op', username=target_username))
                    self._log_to_ui(f"  Kills: {self.player_kills.get(target_username, 0)}")
                else:
                    self._log_to_ui(get_text('player_status_offline', username=target_username))
                self._log_to_ui("--------------------")
            elif cmd_name == "list":
                online_players = list(self.players.keys())
                self._log_to_ui(get_text('player_list_title', count=len(online_players)))
                if not online_players:
                    self._log_to_ui(get_text('player_list_empty'))
                else:
                    # Sort players alphabetically for consistent display
                    for i, uname in enumerate(sorted(online_players)):
                        status = get_text('status_alive') if self.alive_status.get(uname, False) else get_text('status_dead')
                        op_suffix = get_text('is_operator') if uname in self.operators else ""
                        kills_suffix = f" (Kills: {self.player_kills.get(uname, 0)})"
                        self._log_to_ui(get_text('player_list_item', index=i+1, username=uname, status=status, operator_suffix=op_suffix) + kills_suffix)
                self._log_to_ui("--------------------")
            elif cmd_name == "playerlimit":
                self._set_player_limit(cmd_arg)
            elif cmd_name == "shutdown":
                self.stop_server()
            elif cmd_name == "restart":
                self.restart_server()
            elif cmd_name == "kickall":
                self._log_to_ui(get_text('kicking_all_players'))
                for name in list(self.clients.keys()):
                    self._log_to_ui(get_text('kicking_player', name=name))
                    try:
                        self.clients[name].send(json.dumps({"kick": True}).encode())
                        self.clients[name].close()
                    except Exception as e:
                        self._log_to_ui(f"Error sending kick or closing socket for {name}: {e}")
                    self._remove_client(name)
            else:
                self._log_to_ui(get_text('unknown_command'))

    def _set_player_limit(self, limit_str):
        try:
            limit = int(limit_str)
            if limit < 0:
                self._log_to_ui(get_text('limit_invalid_negative'))
            else:
                self.max_players = limit
                self._log_to_ui(get_text('player_limit_set', limit=self.max_players))
        except ValueError:
            self._log_to_ui(get_text('limit_invalid_number'))

    def _show_server_tasks_menu(self):
        """Displays a menu for server tasks (informational, as direct commands are preferred)."""
        self._log_to_ui(get_text('server_tasks_prompt'))
        self._log_to_ui(f"- {get_text('task_shutdown')}")
        self._log_to_ui(f"- {get_text('task_restart')}")
        self._log_to_ui(f"- {get_text('task_kick_all')}")
        self._log_to_ui(f"- {get_text('task_set_limit')}")
        self._log_to_ui(get_text("commands_for_server_title"))
        self._log_to_ui("You can type 'shutdown', 'restart', 'kickall', 'playerlimit [number]' directly.")

    def _on_closing(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit? This will stop the server process too."):
            self.stop_server() # Try to gracefully stop the server threads
            self.master.destroy() # Destroy the GUI window

# Helper function for getting user input via messagebox (for start-up)
def _get_user_input(title, prompt, default_value="", show_password=False):
    """Shows a simple input dialog for server setup."""
    result = simpledialog.askstring(title, prompt, initialvalue=default_value, show="*" if show_password else None)
    return result if result is not None else default_value

def main():
    global current_language

    print("DEBUG: Creating main Tkinter window.")
    root = tk.Tk()
    root.geometry("1000x650") # Tambahkan ini lagi, untuk memastikan
   # root.withdraw()
    print("DEBUG: Main window hidden.")

    # Simple language selection dialog
    print("DEBUG: Creating language dialog.")
    lang_dialog = tk.Toplevel(root)
    lang_dialog.title(get_text("language_selection"))
    lang_dialog.geometry("300x150")
    lang_dialog.transient(root)
    lang_dialog.grab_set()

    tk.Label(lang_dialog, text=get_text("language_selection"), font=("Arial", 12)).pack(pady=10)
    tk.Label(lang_dialog, text=get_text("type_eng"), font=("Arial", 10)).pack()
    tk.Label(lang_dialog, text=get_text("type_id"), font=("Arial", 10)).pack()

    lang_entry = tk.Entry(lang_dialog, font=("Arial", 10))
    lang_entry.pack(pady=5)
    lang_entry.focus_set()

    selected_lang = tk.StringVar()

    def set_and_destroy():
        choice = lang_entry.get().strip().upper()
        set_language(choice)
        selected_lang.set(choice)
        print(f"DEBUG: Language dialog closed, choice: {choice}")
        lang_dialog.destroy()

    lang_entry.bind("<Return>", lambda event: set_and_destroy())
    tk.Button(lang_dialog, text="OK", command=set_and_destroy).pack(pady=5)

    print("DEBUG: Waiting for language dialog to close...")
    root.wait_window(lang_dialog)
    print("DEBUG: Language dialog closed. Deiconifying main window.")
    root.deiconify() # Tampilkan kembali jendela utama setelah dialog ditutup

    print("DEBUG: Initializing ConterbitServerApp.")
    app = ConterbitServerApp(root)
    print("DEBUG: ConterbitServerApp initialized.")

    # Initial splash screen in console
    splash_screen = """
    ____  _ __  ______             __          _____             
   / __ )(_) /_/ ____/___  __  ______  / /____  _____  / ___/___  ______    _____  _____
  / __  / / __/ /   / __ \\/ / / / __ \\/ __/ _ \\/ ___/  \\__ \\/ _ \\/ ___/ | / / _ \\/ ___/
 / /_/ / / /_/ /___/ /_/ / /_/ / /_/ / /_/  __/ /    ___/ /  __/ /   | |/ /  __/ /   
/_____/_\\__\\\\____/\\____/\\__,_/_/_/ /_/\\__/\\___/_/     /____/\\___/\\_/    |___/\\___/_/    

    """
    print(splash_screen) # This will still print to the console where the script is run

    print("DEBUG: Starting main Tkinter loop.")
    root.mainloop()
    print("DEBUG: Main Tkinter loop ended.")

if __name__ == "__main__":
    main()
