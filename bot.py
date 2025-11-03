# bot.py
"""
BoT - Fully Automatic Auto-Join, Auto-Reconnect, Silent Movement Bot
Perfect for Aternos SMP (Cracked + Offline mode).
"""

import time
import random
import socket
import logging
import threading
from minecraft.networking.connection import Connection
from minecraft.networking.packets import clientbound, serverbound

# -------- CONFIG --------
USERNAME = "BoT"
SERVER_HOST = "TheUnexpectedSMP.aternos.me"
SERVER_PORT = 40070

CHECK_INTERVAL = 5      # seconds (server ping interval)
MOVE_INTERVAL = 10
ROTATE_INTERVAL = 5
RECONNECT_DELAY = 10
# ------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [BoT] %(message)s")


class AutoJoinBot:
    def __init__(self):
        self.conn = None
        self.running = True
        self.x = self.y = self.z = 0

    # ----- TCP Ping ----- #
    def is_server_online(self):
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect((SERVER_HOST, SERVER_PORT))
            s.close()
            return True
        except:
            return False

    # ----- MAIN LOOP ----- #
    def start(self):
        while self.running:
            logging.info("Checking if server is online...")
            if not self.is_server_online():
                logging.info("Server offline... checking again.")
                time.sleep(CHECK_INTERVAL)
                continue

            logging.info("Server is ONLINE ✅ Joining...")
            self.join_server()

            logging.info(f"Reconnecting in {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)

    def join_server(self):
        try:
            self.conn = Connection(SERVER_HOST, SERVER_PORT, username=USERNAME)

            self.conn.register_packet_listener(self.on_join, clientbound.play.JoinGamePacket)
            self.conn.register_packet_listener(self.on_pos, clientbound.play.PlayerPositionAndLookPacket)
            self.conn.register_packet_listener(self.on_keepalive, clientbound.play.KeepAlivePacket)

            self.conn.connect()
            logging.info("✅ Successfully Joined Server")

            # Start movement / rotation loops
            threading.Thread(target=self.move_loop, daemon=True).start()
            threading.Thread(target=self.rotate_loop, daemon=True).start()

            # Stay connected
            while self.conn.running:
                time.sleep(1)

        except Exception as e:
            logging.error(f"Join Error: {e}")

        logging.info("Disconnected ❌")

    # ----- PACKET HANDLERS ----- #

    def on_join(self, packet):
        logging.info("✅ Spawned in world")

    def on_pos(self, packet):
        self.x, self.y, self.z = packet.x, packet.y, packet.z

    def on_keepalive(self, packet):
        keep = serverbound.play.KeepAlivePacket()
        keep.keep_alive_id = packet.keep_alive_id
        self.conn.write_packet(keep)

    # ----- MOVEMENT ----- #

    def move_loop(self):
        while self.running:
            try:
                if self.conn:
                    self.x += random.uniform(-0.1, 0.1)
                    self.z += random.uniform(-0.1, 0.1)

                    pkt = serverbound.play.PlayerPositionPacket()
                    pkt.x = self.x
                    pkt.y = self.y
                    pkt.z = self.z
                    pkt.on_ground = True

                    self.conn.write_packet(pkt)
                    logging.info("Moving…")
            except:
                pass
            time.sleep(MOVE_INTERVAL)

    def rotate_loop(self):
        while self.running:
            try:
                if self.conn:
                    yaw = random.uniform(0, 360)
                    pitch = random.uniform(-10, 10)

                    pkt = serverbound.play.PlayerPositionAndLookPacket()
                    pkt.x = self.x
                    pkt.y = self.y
                    pkt.z = self.z
                    pkt.yaw = yaw
                    pkt.pitch = pitch
                    pkt.on_ground = True

                    self.conn.write_packet(pkt)
                    logging.info("Rotating…")
            except:
                pass
            time.sleep(ROTATE_INTERVAL)


if __name__ == "__main__":
    bot = AutoJoinBot()
    bot.start()
