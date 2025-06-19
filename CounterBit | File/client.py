import pygame
import socket
import threading
import json
import math
import time
import sys
import os 

# --- Inisialisasi Pygame ---
WIDTH, HEIGHT = 900, 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CounterBit Ultimete Edition")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)

# --- Inisialisasi Mixer Pygame untuk Suara ---
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512) 

# --- Muat File Suara ---
script_dir = os.path.dirname(__file__)
sfx_dir = os.path.join(script_dir, "Sfx")

intro_sound = None
pew_sound = None
spawn_sound = None

try:
    intro_sound = pygame.mixer.Sound(os.path.join(sfx_dir, "intro.mp3"))
    pew_sound = pygame.mixer.Sound(os.path.join(sfx_dir, "Pew.mp3"))
    spawn_sound = pygame.mixer.Sound(os.path.join(sfx_dir, "Spawn.mp3"))
    
    intro_sound.set_volume(0.5) 
    pew_sound.set_volume(0.3)
    spawn_sound.set_volume(0.7)
except pygame.error as e:
    print(f"Error memuat file suara: {e}")
    print("Pastikan file 'intro.mp3', 'Pew.mp3', dan 'Spawn.mp3' ada di folder 'CounterBit/Sfx/'.")
    intro_sound = None 
    pew_sound = None
    spawn_sound = None

# --- Mainkan Suara Intro saat Game Dimulai ---
if intro_sound:
    intro_sound.play()


def draw_text(text, x, y, color=(0,0,0), font_to_use=font, center_x=False):
    img = font_to_use.render(text, True, color)
    if center_x:
        x = x - img.get_width() // 2
    screen.blit(img, (x, y))

# --- Input Username, IP Server, dan Password ---
username = input("Masukkan username: ")
server_ip = input("Masukkan alamat IP server (misal: 127.0.0.1): ") 
client_password = input("Masukkan password server (kosongkan jika tidak ada password): ").strip()

# --- Pengaturan Jaringan ---
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    initial_data = {"username": username, "password": client_password if client_password else None} 
    client.connect((server_ip, 5555)) 
    client.send(json.dumps(initial_data).encode())
except ConnectionRefusedError:
    print(f"Koneksi ke {server_ip}:5555 ditolak. Pastikan server berjalan dan IP benar.")
    pygame.quit()
    sys.exit()
except socket.gaierror:
    print(f"Nama host atau alamat IP '{server_ip}' tidak dikenal.")
    pygame.quit()
    sys.exit()
except Exception as e:
    print(f"Terjadi kesalahan koneksi: {e}")
    pygame.quit()
    sys.exit()

# --- Variabel Game ---
player_pos = [WIDTH//2, HEIGHT//2]
shoot = False
angle = 0

players = {}
alive = {}
operators = set()

dead = False
respawn_cooldown = 5
respawn_timer = 0

kill_count = 0
last_ping_time = 0
current_ping = 0
ping_interval = 1 

shooting_cooldown = 0.5 # Cooldown menembak dalam detik
last_shot_time = 0    # Waktu terakhir tembakan dilakukan

# --- Variabel Peluru & Reload ---
MAX_BULLETS = 10
current_bullets = 5  # Dimulai dengan 5 peluru dari 10
reloading = False
reload_start_time = 0
RELOAD_TIME_SECONDS = 1.5 # Durasi reload dalam detik
# --- END Variabel Peluru & Reload ---

server_name_display = "Connecting..."
server_ip_display = server_ip

# --- Variabel Batas Pemain (BARU) ---
server_max_players = 0
current_online_players = 0
# --- END Variabel Batas Pemain ---

lock = threading.Lock()
running_game = True 

# --- Peluru (Tambahan) ---
bullet_active = False
bullet_pos = [0, 0]
bullet_angle = 0
bullet_owner = "" # Siapa yang menembakkan peluru ini

# --- Thread untuk Menerima Data ---
def receive_data():
    global players, alive, dead, respawn_timer, player_pos, current_ping, last_ping_time, running_game, server_name_display, server_ip_display, operators, bullet_active, bullet_pos, bullet_angle, bullet_owner
    global server_max_players, current_online_players # BARU: Deklarasikan global
    
    while running_game:
        try:
            data = client.recv(4096).decode()
            if not data:
                print("Server disconnected.")
                break
            
            data_json = json.loads(data)

            if data_json.get("kick"):
                reason = data_json.get("reason", "Anda telah dikeluarkan dari server.")
                # Cek apakah alasan kick adalah karena server penuh (BARU)
                if "Server is full!" in reason or "Server penuh!" in reason:
                    # Ambil angka pemain dan batas dari pesan jika ada
                    parts = reason.split(':')
                    if len(parts) > 1:
                        player_counts = parts[1].strip() # Contoh: "45/45"
                        print(f"Server Penuh! {player_counts}")
                    else:
                        print(f"Server Penuh! {reason}") # Fallback jika format pesan tidak sesuai
                else:
                    print(f"Anda dikeluarkan dari server: {reason}")
                
                running_game = False 
                break
            if data_json.get("shutdown"):
                print("Server dimatikan.")
                running_game = False 
                break
            if "message" in data_json:
                print(f"Pesan Server: {data_json['message']}")

            with lock:
                players = data_json.get("players", {})
                alive = data_json.get("alive", {})
                operators = set(data_json.get("operators", []))
                
                # Update status peluru dari server
                if "bullet" in data_json:
                    bullet_info = data_json["bullet"]
                    bullet_active = bullet_info["active"]
                    if bullet_active:
                        bullet_pos = [bullet_info["x"], bullet_info["y"]]
                        bullet_angle = bullet_info["angle"]
                        bullet_owner = bullet_info["owner"]
                    else:
                        bullet_owner = "" 
                else:
                    bullet_active = False 

                if "ping" in data_json and last_ping_time != 0:
                    current_ping = int((time.time() - last_ping_time) * 1000)
                    last_ping_time = 0
                
                if "server_info" in data_json: # DIUBAH
                    server_info = data_json["server_info"]
                    server_name_display = server_info.get("name", "Unknown Server")
                    server_ip_display = server_info.get("ip", server_ip)
                    server_max_players = server_info.get("max_players", 0)     # BARU
                    current_online_players = server_info.get("current_players", 0) # BARU

                if username in operators:
                    dead = False
                elif not alive.get(username, True):
                    if not dead:
                        print("Anda mati!")
                        dead = True
                        respawn_timer = time.time() + respawn_cooldown
                        player_pos = [WIDTH//2, HEIGHT//2] 
                        if spawn_sound:
                            spawn_sound.play()
                else:
                    dead = False
        except json.JSONDecodeError:
            print("Received malformed JSON from server.")
        except ConnectionResetError:
            print("Koneksi ke server terputus.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break
        
    running_game = False 
    pygame.quit()
    sys.exit()

threading.Thread(target=receive_data, daemon=True).start()

# --- Helper Functions for Drawing ---
def username_to_color(name):
    h = sum(ord(c) for c in name)
    return ((h*50) % 256, (h*80) % 256, (h*110) % 256)

def draw_player(x, y, color, angle, alive_status, is_self=False, is_operator=False):
    size = 30
    rect = pygame.Rect(x - size//2, y - size//2, size, size)
    
    if not alive_status:
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        s.fill((128, 128, 128, 100))
        screen.blit(s, rect.topleft)
        pygame.draw.rect(screen, (50, 50, 50), rect, 2)
    else:
        pygame.draw.rect(screen, color, rect)
        if is_self:
            pygame.draw.rect(screen, (255, 255, 0), rect, 2)
        
        if is_operator:
            pygame.draw.rect(screen, (0, 255, 255), rect, 3) 

        gun_length = 20
        end_x = x + gun_length * math.cos(angle)
        end_y = y + gun_length * math.sin(angle)
        gun_color = (0, 0, 0) 
        pygame.draw.line(screen, gun_color, (x, y), (end_x, end_y), 3)
    return rect

# --- Main Game Loop ---
while running_game:
    clock.tick(60)
    screen.fill((255, 255, 255))

    mx, my = pygame.mouse.get_pos()
    dx = mx - player_pos[0]
    dy = my - player_pos[1]
    angle = math.atan2(dy, dx)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_game = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if dead and username not in operators:
                respawn_button_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 40, 100, 30)
                if respawn_button_rect.collidepoint(mx, my) and time.time() >= respawn_timer:
                    try:
                        client.send(json.dumps({
                            "x": WIDTH//2,
                            "y": HEIGHT//2,
                            "shoot": False,
                            "angle": 0
                        }).encode())
                        with lock:
                            player_pos = [WIDTH//2, HEIGHT//2]
                            dead = False
                        print("Mengirim permintaan hidup kembali...")
                    except Exception as e:
                        print(f"Error sending respawn data: {e}")
                
                exit_button_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 80, 120, 30)
                if exit_button_rect.collidepoint(mx, my):
                    print("Keluar dari game...")
                    running_game = False
                    break
            elif not dead or username in operators: 
                now = time.time()
                # LOGIKA TEMBAK DENGAN PELURU (DIUBAH)
                if not reloading and current_bullets > 0: 
                    if now - last_shot_time >= shooting_cooldown:
                        try:
                            client.send(json.dumps({
                                "x": player_pos[0], 
                                "y": player_pos[1], 
                                "shoot": True, 
                                "angle": angle 
                            }).encode())
                            if pew_sound:
                                pew_sound.play()
                            print(f"{username} menembak!")
                            current_bullets -= 1 
                            last_shot_time = now 
                        except Exception as e:
                            print(f"Error sending shoot command: {e}")
                    else:
                        remaining_cooldown = int(shooting_cooldown - (now - last_shot_time)) + 1
                        print(f"Cooldown menembak: {remaining_cooldown} detik.")
                elif reloading:
                    print("Sedang reload, tidak bisa menembak.")
                else: 
                    print("Tidak ada peluru! Tekan 'R' untuk reload.")
        
        elif event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_r:
                if current_bullets < MAX_BULLETS and not reloading:
                    reloading = True
                    reload_start_time = time.time()
                    print("Memulai reload...")
                elif reloading:
                    print("Sudah dalam proses reload.")
                else: 
                    print("Peluru penuh!")


    # --- LOGIKA RELOAD DALAM LOOP UTAMA ---
    if reloading:
        now = time.time()
        if now - reload_start_time >= RELOAD_TIME_SECONDS:
            current_bullets = MAX_BULLETS
            reloading = False
            print("Reload selesai!")

    if not dead or username in operators: 
        keys = pygame.key.get_pressed()
        speed = 5
        if keys[pygame.K_w]: player_pos[1] -= speed
        if keys[pygame.K_s]: player_pos[1] += speed
        if keys[pygame.K_a]: player_pos[0] -= speed
        if keys[pygame.K_d]: player_pos[0] += speed

        player_pos[0] = max(0, min(player_pos[0], WIDTH))
        player_pos[1] = max(0, min(player_pos[1], HEIGHT))

        if time.time() - last_ping_time > ping_interval and last_ping_time == 0:
            data_to_send = json.dumps({
                "x": player_pos[0],
                "y": player_pos[1],
                "shoot": False, 
                "angle": angle,
                "ping_request": True
            })
            last_ping_time = time.time()
        else:
            data_to_send = json.dumps({
                "x": player_pos[0],
                "y": player_pos[1],
                "shoot": False, 
                "angle": angle
            })

        try:
            client.send(data_to_send.encode())
        except Exception as e:
            pass

    # --- Gambar Peluru dari Server ---
    with lock:
        if bullet_active and bullet_owner != "": 
            bullet_color = (255, 255, 0) # Kuning
            bullet_size = 5 
            pygame.draw.circle(screen, bullet_color, (int(bullet_pos[0]), int(bullet_pos[1])), bullet_size)
    # --- End Gambar Peluru ---

    with lock:
        for uname, info in players.items():
            color = username_to_color(uname)
            alive_stat = alive.get(uname, True)
            is_op = (uname in operators)
            
            is_self_player = (uname == username)
            draw_player(info["x"], info["y"], color, info["angle"], alive_stat, is_self=is_self_player, is_operator=is_op)
            
            display_name = uname
            if is_op:
                display_name = f"{uname} (OP)"
            
            text_surface = font.render(display_name, True, color)
            text_rect = text_surface.get_rect(center=(info["x"], info["y"] - 20))
            screen.blit(text_surface, text_rect)

    if dead and username not in operators:
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0,0))

        draw_text("Kamu Mati", WIDTH//2, HEIGHT//2 - 20, (255, 0, 0), center_x=True)

        respawn_button_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 40, 100, 30)
        now = time.time()
        remaining = max(0, int(respawn_timer - now))
        if remaining == 0:
            pygame.draw.rect(screen, (0, 150, 0), respawn_button_rect)
            draw_text("Hidupkan", respawn_button_rect.x + 10, respawn_button_rect.y + 5, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (100, 100, 100), respawn_button_rect)
            draw_text(f"Cooldown {remaining}s", respawn_button_rect.x + 5, respawn_button_rect.y + 5, (200, 200, 200))
            
        exit_button_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 80, 120, 30)
        pygame.draw.rect(screen, (200, 0, 0), exit_button_rect)
        draw_text("Exit Server", exit_button_rect.x + 10, exit_button_rect.y + 5, (255, 255, 255))

    kill_text = f"Kills: {kill_count}"
    ping_text = f"Ping: {current_ping} ms"

    # --- Tampilan Cooldown Tembak / Status Peluru ---
    if not dead or username in operators:
        now = time.time()
        if reloading:
            remaining_reload_time = int(RELOAD_TIME_SECONDS - (now - reload_start_time)) + 1
            status_text = f"Reloading... {remaining_reload_time}s"
            draw_text(status_text, WIDTH // 2, HEIGHT - 50, (200, 50, 50), small_font, center_x=True)
        elif current_bullets == 0:
            status_text = "Tidak Ada Peluru! Tekan 'R' untuk Reload"
            draw_text(status_text, WIDTH // 2, HEIGHT - 50, (200, 50, 50), small_font, center_x=True)
        elif now - last_shot_time < shooting_cooldown:
            remaining_cooldown_shoot = int(shooting_cooldown - (now - last_shot_time)) + 1
            shooting_cooldown_text = f"Tembak Cooldown: {remaining_cooldown_shoot}s"
            draw_text(shooting_cooldown_text, WIDTH // 2, HEIGHT - 50, (200, 50, 50), small_font, center_x=True)
    # --- END Tampilan Cooldown Tembak / Status Peluru ---

    draw_text(kill_text, 10, HEIGHT - 30, (0,0,0), small_font)
    ping_text_width = small_font.size(ping_text)[0]
    draw_text(ping_text, WIDTH - ping_text_width - 10, HEIGHT - 30, (0,0,0), small_font)

    server_info_text = f"Server: {server_name_display} ({server_ip_display})"
    draw_text(server_info_text, 10, 10, (50, 50, 50), small_font)

    # --- Tampilkan jumlah peluru ---
    bullet_count_text = f"Peluru: {current_bullets}/{MAX_BULLETS}"
    draw_text(bullet_count_text, 10, 35, (50, 50, 50), small_font)
    # --- END Tampilkan jumlah peluru ---

    # --- Tampilan Batas Pemain (BARU) ---
    if server_max_players > 0: # Hanya tampilkan jika ada batas yang ditetapkan
        player_limit_text = f"Pemain: {current_online_players}/{server_max_players}"
        # Posisikan agar tidak tumpang tindih dengan ping atau info server
        draw_text(player_limit_text, WIDTH - small_font.size(player_limit_text)[0] - 10, 35, (50, 50, 50), small_font)
    # --- END Tampilan Batas Pemain ---

    pygame.display.flip()

client.close()
pygame.quit()
sys.exit()
