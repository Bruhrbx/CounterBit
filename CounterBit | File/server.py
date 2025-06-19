import socket
import threading
import json
import sys
import time
import os
import math 
import pygame 

# --- Global Variables ---
clients = {}
players = {}
alive_status = {}
operators = set()
server_running = True
lock = threading.Lock()
server_name = "DefaultServer"
current_language = {}
server_password = None
max_players = 0 # 0 berarti tidak ada batas pemain
player_kills = {} # NEW: Dictionary untuk menyimpan skor kill setiap pemain
# --- Peluru di Server ---
bullet_data = {
    "active": False,
    "x": 0,
    "y": 0,
    "angle": 0,
    "owner": "", 
    "speed": 15, 
    "size": 5    
}
# --- End Peluru di Server ---

# --- Inisialisasi Pygame Mixer (Untuk Suara di Server) ---
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# --- Muat File Suara Tada! ---
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
# --- End Muat File Suara ---


# --- Language Dictionaries ---
LANG_EN = {
    "server_name_prompt": "Enter a name for this server (e.g., qwertino): ",
    "server_password_prompt": "Enter a password for the server (leave blank for no password): ",
    "server_started": "Server '{server_name}' started. Player Limit: {limit}.", # DIUBAH
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
    "username_already_in_use": "Username '{username}' is already in use.", # BARU
}

LANG_ID = {
    "server_name_prompt": "Masukkan nama untuk server ini (contoh: qwertino): ",
    "server_password_prompt": "Masukkan password untuk server (kosongkan jika tanpa password): ",
    "server_started": "Server '{server_name}' dimulai. Batas Pemain: {limit}.", # DIUBAH
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
    "username_already_in_use": "Username '{username}' sudah digunakan.", # BARU
}


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
        set_language("ENG")
    return current_language.get(key, f"MISSING_TEXT_KEY[{key}]").format(**kwargs)

# --- FUNGSI BARU: Mengatur Batas Pemain ---
def set_player_limit(limit_str):
    global max_players
    try:
        limit = int(limit_str)
        if limit < 0:
            print(f"[{time.strftime('%H:%M:%S')}] {get_text('limit_invalid_negative')}")
        else:
            max_players = limit
            print(f"[{time.strftime('%H:%M:%S')}] {get_text('player_limit_set', limit=max_players)}")
    except ValueError:
        print(f"[{time.strftime('%H:%M:%S')}] {get_text('limit_invalid_number')}")
# --- END FUNGSI BARU ---


def handle_client(conn, addr):
    """
    Handles individual communication with each connected client.
    Each client will have its own handle_client() thread.
    """
    global clients, players, alive_status, server_running, server_name, operators, server_password, bullet_data, max_players, player_kills # Tambahkan player_kills
    username = None
    try:
        data = conn.recv(1024).decode()
        data_json = json.loads(data)
        username = data_json.get("username")
        client_password = data_json.get("password")

        with lock: 
            # 1. Periksa username duplikat lebih awal (opsional, tapi bagus untuk mencegah masalah)
            if username in players:
                print(f"[{time.strftime('%H:%M:%S')}] {get_text('username_already_in_use', username=username)}")
                conn.send(json.dumps({"kick": True, "reason": get_text('username_already_in_use', username=username)}).encode())
                conn.close()
                return

            # 2. Periksa apakah server penuh
            if max_players > 0 and len(players) >= max_players:
                print(f"[{time.strftime('%H:%M:%S')}] {get_text('connection_rejected_full', addr=addr)}")
                kick_reason = get_text("server_full_kick_reason", current=len(players), max=max_players)
                conn.send(json.dumps({"kick": True, "reason": kick_reason}).encode())
                conn.close()
                return 
            
            # 3. Periksa password
            if server_password and client_password != server_password:
                print(f"[{time.strftime('%H:%M:%S')}] {addr} tried to connect with incorrect password.")
                conn.send(json.dumps({"kick": True, "reason": get_text("password_incorrect")}).encode())
                conn.close()
                return
            elif server_password and not client_password:
                print(f"[{time.strftime('%H:%M:%S')}] {addr} tried to connect without password (password required).")
                conn.send(json.dumps({"kick": True, "reason": get_text("password_required")}).encode())
                conn.close()
                return

            # Jika lolos semua pemeriksaan, tambahkan klien
            players[username] = {"x": 300, "y": 300, "shoot": False, "angle": 0}
            alive_status[username] = True
            clients[username] = conn
            player_kills[username] = 0 # NEW: Inisialisasi skor kill untuk pemain baru

        print(f"[{time.strftime('%H:%M:%S')}] {get_text('client_connected', username=username, addr=addr)}")

        while server_running:
            data = conn.recv(4096).decode()
            if not data:
                break
            
            data_json = json.loads(data)

            with lock:
                if data_json.get("shoot") and not bullet_data["active"]:
                    player_x = players[username]["x"]
                    player_y = players[username]["y"]
                    player_angle = data_json.get("angle", 0) 
                    
                    bullet_data["active"] = True
                    bullet_data["x"] = player_x + 20 * math.cos(player_angle)
                    bullet_data["y"] = player_y + 20 * math.sin(player_angle)
                    bullet_data["angle"] = player_angle
                    bullet_data["owner"] = username 
            
                if alive_status.get(username, False):
                    players[username].update({
                        "x": data_json["x"],
                        "y": data_json["y"],
                        "shoot": data_json.get("shoot", False),
                        "angle": data_json["angle"]
                    })
                elif username in players and not alive_status.get(username, False):
                    if username not in operators:
                        alive_status[username] = True
                        players[username].update({
                            "x": data_json["x"],
                            "y": data_json["y"],
                            "shoot": data_json.get("shoot", False),
                            "angle": data_json["angle"]
                        })
                        print(f"[{time.strftime('%H:%M:%S')}] {get_text('player_respawned_server_log', username=username)}")


            # Update bullet position only if active
            if bullet_data["active"]:
                bullet_data["x"] += bullet_data["speed"] * math.cos(bullet_data["angle"])
                bullet_data["y"] += bullet_data["speed"] * math.sin(bullet_data["angle"])

                # Check if bullet is out of bounds
                if not (-10 <= bullet_data["x"] <= 610 and -10 <= bullet_data["y"] <= 410):
                    bullet_data["active"] = False
                
                # Check for bullet collision with players (if still active)
                if bullet_data["active"]: 
                    for target_username, target_info in players.items():
                        # Skip if target is the owner, an operator, or already dead
                        if target_username == bullet_data["owner"] or \
                           target_username in operators or \
                           not alive_status.get(target_username, False):
                            continue

                        player_center_x = target_info["x"]
                        player_center_y = target_info["y"]
                        player_half_size = 15 
                        bullet_radius = bullet_data["size"]

                        closest_x = max(player_center_x - player_half_size, min(bullet_data["x"], player_center_x + player_half_size))
                        closest_y = max(player_center_y - player_half_size, min(bullet_data["y"], player_center_y + player_half_size))

                        distance_x = bullet_data["x"] - closest_x
                        distance_y = bullet_data["y"] - closest_y

                        distance_squared = (distance_x * distance_x) + (distance_y * distance_y)

                        if distance_squared < (bullet_radius * bullet_radius):
                            alive_status[target_username] = False
                            players[target_username]["x"] = 300
                            players[target_username]["y"] = 300
                            players[target_username]["shoot"] = False
                            players[target_username]["angle"] = 0
                            
                            bullet_data["active"] = False 
                            print(f"[{time.strftime('%H:%M:%S')}] {get_text('player_killed_server_log', killer=bullet_data['owner'], target=target_username)}") 
                            
                            # NEW: Tambahkan kill ke pemilik peluru
                            if bullet_data["owner"] in player_kills:
                                player_kills[bullet_data["owner"]] += 1
                            else:
                                player_kills[bullet_data["owner"]] = 1 # Inisialisasi jika belum ada
                            print(f"[{time.strftime('%H:%M:%S')}] Skor Kill {bullet_data['owner']}: {player_kills[bullet_data['owner']]}")

                            break 

            # Prepare data to send to all clients
            send_data_dict = {
                "players": players,
                "alive": alive_status,
                "operators": list(operators), 
                "bullet": bullet_data,
                "kills": player_kills # NEW: Kirim data kills ke klien
            }
            if "ping_request" in data_json and data_json["ping_request"]:
                send_data_dict["ping"] = True
            
            send_data_dict["server_info"] = {
                "name": server_name,
                "ip": get_local_ip(),
                "max_players": max_players,      
                "current_players": len(players) 
            }

            with lock:
                send_data = json.dumps(send_data_dict)
                for c in clients.values():
                    try:
                        c.send(send_data.encode())
                    except:
                        pass

    except json.JSONDecodeError:
        print(f"[{time.strftime('%H:%M:%S')}] {get_text('invalid_json_received', addr=addr)}")
    except ConnectionResetError:
        print(f"[{time.strftime('%H:%M:%S')}] {get_text('client_forcibly_disconnected', username_or_addr=(username if username else addr))}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] {get_text('client_handling_error', username_or_addr=(username if username else addr), error=e)}")
    finally:
        print(f"[{time.strftime('%H:%M:%S')}] {get_text('client_disconnected', username=(username if username else addr))}")
        with lock:
            if username in clients:
                clients[username].close()
                del clients[username]
            if username in players:
                del players[username]
            if username in alive_status:
                del alive_status[username]
            if username in operators:
                operators.remove(username)
                print(f"[{time.strftime('%H:%M:%S')}] {get_text('operator_removed_on_disconnect', username=username)}")
            if username in player_kills: # NEW: Hapus skor kill pemain saat disconnect
                del player_kills[username]


def show_server_tasks_menu():
    """Menampilkan menu Server Tasks dan menangani pilihan."""
    global server_running 
    
    print(f"\n[{time.strftime('%H:%M:%S')}] {get_text('server_tasks_prompt')}")
    print(f"- {get_text('task_shutdown')}")
    print(f"- {get_text('task_restart')}")
    print(f"- {get_text('task_kick_all')}")
    print(f"- {get_text('task_set_limit')}") 
    
    while True:
        choice = input(get_text('type_choice')).strip()
        
        if choice == "1": # ShutDown
            print(f"[{time.strftime('%H:%M:%S')}] {get_text('shutting_down_server')}")
            server_running = False
            with lock:
                for c in list(clients.values()):
                    try:
                        c.send(json.dumps({"shutdown": True}).encode())
                        c.close()
                    except:
                        pass
                clients.clear()
                players.clear()
                alive_status.clear()
                operators.clear()
                player_kills.clear() # NEW: Kosongkan kills saat shutdown
            break 
        
        elif choice == "2": # Restart
            print(f"[{time.strftime('%H:%M:%S')}] {get_text('restarting_server')}")
            server_running = False 
            with lock:
                for c in list(clients.values()):
                    try:
                        c.send(json.dumps({"shutdown": True}).encode()) 
                        c.close()
                    except:
                        pass
                clients.clear()
                players.clear()
                alive_status.clear()
                operators.clear()
                player_kills.clear() # NEW: Kosongkan kills saat restart
            os.execv(sys.executable, ['python'] + sys.argv)
            
        elif choice == "3": # Kick All
            print(f"[{time.strftime('%H:%M:%S')}] {get_text('kicking_all_players')}")
            with lock:
                for username_to_kick, conn_to_kick in list(clients.items()): 
                    try:
                        conn_to_kick.send(json.dumps({"kick": True, "reason": get_text("kicking_all_players")}).encode())
                        conn_to_kick.close()
                        del clients[username_to_kick]
                        if username_to_kick in players:
                            del players[username_to_kick]
                        if username_to_kick in alive_status:
                            del alive_status[username_to_kick]
                        if username_to_kick in operators:
                            operators.remove(username_to_kick)
                        if username_to_kick in player_kills: # NEW: Hapus skor kill saat kick all
                            del player_kills[username_to_kick]
                        print(f"[{time.strftime('%H:%M:%S')}] {username_to_kick} kicked.")
                    except Exception as e:
                        print(f"[{time.strftime('%H:%M:%S')}] Error kicking {username_to_kick}: {e}")
            break 
        
        elif choice == "4": # Set Player Limit
            limit_str = input(get_text('player_limit_prompt')).strip()
            set_player_limit(limit_str)
            break 
        
        else:
            print(f"[{time.strftime('%H:%M:%S')}] {get_text('invalid_task_choice')}")

def command_listener():
    """
    Listens for commands from the server console.
    """
    global server_running, operators
    while server_running:
        try:
            cmd = input().strip() 
            if cmd.startswith("kick "):
                name = cmd.split(" ", 1)[1].strip()
                with lock:
                    if name in clients:
                        print(f"[{time.strftime('%H:%M:%S')}] {get_text('kicking_player', name=name)}")
                        try:
                            clients[name].send(json.dumps({"kick": True}).encode())
                            clients[name].close()
                        except Exception as e:
                            print(f"[{time.strftime('%H:%M:%S')}] Error sending kick or closing socket for {name}: {e}")
                        del clients[name]
                        if name in players:
                            del players[name]
                        if name in alive_status:
                            del alive_status[name]
                        if name in operators:
                            operators.remove(name)
                            print(f"[{time.strftime('%H:%M:%S')}] {get_text('operator_removed_on_disconnect', username=name)}")
                        if name in player_kills: # NEW: Hapus skor kill saat kick
                            del player_kills[name]
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] {get_text('player_not_found', name=name)}")
            elif cmd.startswith("op "):
                name = cmd.split(" ", 1)[1].strip()
                with lock:
                    if name in players:
                        operators.add(name)
                        print(f"[{time.strftime('%H:%M:%S')}] {get_text('player_op_success', name=name)}")
                        if name in clients:
                            try:
                                clients[name].send(json.dumps({"message": get_text("op_message_client")}).encode())
                            except: pass 
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] {get_text('player_op_fail_offline', name=name)}")
            elif cmd.startswith("unop "):
                name = cmd.split(" ", 1)[1].strip()
                with lock:
                    if name in operators:
                        operators.remove(name)
                        print(f"[{time.strftime('%H:%M:%S')}] {get_text('player_unop_success', name=name)}")
                        if name in clients:
                            try:
                                clients[name].send(json.dumps({"message": get_text("unop_message_client")}).encode())
                            except: pass 
            
            elif cmd == "sertask": 
                show_server_tasks_menu()
                if not server_running: 
                    break 
            
            elif cmd.startswith("check "):
                target_username = cmd.split(" ", 1)[1].strip()
                with lock:
                    print(f"\n[{time.strftime('%H:%M:%S')}] {get_text('player_status_title', username=target_username)}")
                    if target_username in clients: 
                        status_msg = ""
                        if alive_status.get(target_username, False): 
                            status_msg = get_text('player_status_online_alive', username=target_username)
                        else: 
                            status_msg = get_text('player_status_online_dead', username=target_username)
                        
                        print(status_msg)
                        if target_username in operators:
                            print(get_text('player_status_op', username=target_username))
                        if target_username in player_kills: # NEW: Tampilkan skor kill di check command
                            print(f"  Kills: {player_kills[target_username]}")
                    else: 
                        print(get_text('player_status_offline', username=target_username))
                    print(f"[{time.strftime('%H:%M:%S')}] --------------------")
            
            elif cmd == "list":
                with lock:
                    online_players = list(players.keys())
                    print(f"\n[{time.strftime('%H:%M:%S')}] {get_text('player_list_title', count=len(online_players))}")
                    if not online_players:
                        print(get_text('player_list_empty'))
                    else:
                        for i, uname in enumerate(online_players):
                            status = get_text('status_alive') if alive_status.get(uname, False) else get_text('status_dead')
                            op_suffix = get_text('is_operator') if uname in operators else ""
                            kills_suffix = f" (Kills: {player_kills.get(uname, 0)})" # NEW: Tampilkan kills di list command
                            print(get_text('player_list_item', index=i+1, username=uname, status=status, operator_suffix=op_suffix) + kills_suffix)
                    print(f"[{time.strftime('%H:%M:%S')}] --------------------")
            
            elif cmd.startswith("playerlimit "): 
                limit_str = cmd.split(" ", 1)[1].strip()
                set_player_limit(limit_str)
            
            else:
                print(f"[{time.strftime('%H:%M:%S')}] {get_text('unknown_command')}")
            
            sys.stdout.write("Ketik : ") 
            sys.stdout.flush() 
            
        except EOFError:
            print(f"[{time.strftime('%H:%M:%S')}] {get_text('eof_received_command_listener')}")
            server_running = False 
            break
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] {get_text('unexpected_command_error', error=e)}")

def get_local_ip():
    """Gets the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80)) 
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1" 
    finally:
        s.close()
    return IP

def display_server_commands(server_name, host_ip, port):
    print("\n" + "_" * 50)
    print(f"{get_text('commands_for_server_title')}")
    print(f"Nama Server : {server_name}")
    print(f"IP: {host_ip}:{port}")
    print("_" * 50)
    print("\n") 
    print("|     kick [username]         |       check [username]    |")
    print("\n") 
    print("|     op [username]           |        list               |")
    print("\n") 
    print("|     unop [username]         |        sertask            |")
    print("\n") 
    print("|     playerlimit [number]    |                           |") 
    print("\n") 
    sys.stdout.write("Ketik : ") 
    sys.stdout.flush() 

def main():
    global server_running, server_name, server_password

    splash_screen = """
    ____  _ __  ______                  __               _____                          
   / __ )(_) /_/ ____/___  __  ______  / /____  _____   / ___/___  ______   _____  _____
  / __  / / __/ /   / __ \\/ / / / __ \\/ __/ _ \\/ ___/   \\__ \\/ _ \\/ ___/ | / / _ \\/ ___/
 / /_/ / / /_/ /___/ /_/ / /_/ / / / / /_/  __/ /      ___/ /  __/ /   | |/ /  __/ /    
/_____/_/\\__\\\\____/\\____/\\__,_/_/_/ /_/\\__/\\___/_/      /____/\\___/\\_/    |___/\\___/_/     
                                                                                        
    """
    print(splash_screen)

    set_language("ENG") 
    print(get_text("language_selection"))
    print(get_text("type_eng"))
    print(get_text("type_id"))
    lang_choice = input(get_text("your_choice")).strip().upper()
    set_language(lang_choice)

    server_name = input(get_text("server_name_prompt"))
    if not server_name:
        server_name = "DefaultServer"
    
    password_input = input(get_text("server_password_prompt")).strip()
    if password_input:
        server_password = password_input
    else:
        server_password = None

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    
    HOST = get_local_ip()
    PORT = 5555

    try:
        server.bind((HOST, PORT))
        server.listen() 
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] {get_text('connection_refused_server_bind_error', host=HOST, port=PORT, error=e)}")
        sys.exit(1) 

    # NEW: Konfirmasi batas pemain saat server dimulai
    print(f"[{time.strftime('%H:%M:%S')}] {get_text('server_started', server_name=server_name, limit=max_players)}")
    print(f"[{time.strftime('%H:%M:%S')}] {get_text('share_address', host=HOST, port=PORT)}")
    
    display_server_commands(server_name, HOST, PORT)

    if tada_sound:
        tada_sound.play()

    threading.Thread(target=command_listener, daemon=True).start()

    while server_running:
        try:
            conn, addr = server.accept() 
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except socket.timeout:
            continue
        except OSError as e:
            if server_running: 
                print(f"[{time.strftime('%H:%M:%S')}] Error accept server: {e}")
            break 
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Terjadi error tak terduga di loop utama: {e}")
            break 

    server.close()
    print(f"[{time.strftime('%H:%M:%S')}] {get_text('server_stopped')}")

if __name__ == "__main__":
    main()
