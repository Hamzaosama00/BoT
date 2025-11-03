import asyncio
import random
import socket
import time
from mcproto import ClientBound, ServerBound, Connection

SERVER_HOST = "TheUnexpectedSMP.aternos.me"
SERVER_PORT = 40070
USERNAME = "BoT"

CHECK_INTERVAL = 5
MOVE_INTERVAL = 7


def is_online():
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((SERVER_HOST, SERVER_PORT))
        s.close()
        return True
    except:
        return False


async def bot_loop():
    while True:
        print("Checking server online status...")
        if not is_online():
            print("Server offline... waiting...")
            time.sleep(CHECK_INTERVAL)
            continue

        print("✅ Server ONLINE — attempting login...")

        conn = Connection()
        await conn.connect(SERVER_HOST, SERVER_PORT)

        # Offline mode login (cracked SMP)
        conn.send(ServerBound.HandshakePacket(
            protocol_version=763,
            server_address=SERVER_HOST,
            server_port=SERVER_PORT,
            next_state=2  # login
        ))

        conn.send(ServerBound.LoginStartPacket(
            username=USERNAME
        ))

        print("Logging in...")

        logged_in = False
        x = y = z = 0

        while True:
            try:
                pkt = await conn.read_packet()

                # Join complete
                if isinstance(pkt, ClientBound.JoinGamePacket):
                    print("✅ Joined game world!")
                    logged_in = True

                # Set initial position
                if isinstance(pkt, ClientBound.PlayerPositionAndLookPacket):
                    x, y, z = pkt.x, pkt.y, pkt.z
                    print("Spawned at:", x, y, z)

                # KeepAlive response
                if isinstance(pkt, ClientBound.KeepAlivePacket):
                    conn.send(ServerBound.KeepAlivePacket(
                        keep_alive_id=pkt.keep_alive_id
                    ))

                # Movement loop
                if logged_in:
                    dx = random.uniform(-0.2, 0.2)
                    dz = random.uniform(-0.2, 0.2)
                    x += dx
                    z += dz

                    conn.send(ServerBound.PlayerPositionPacket(
                        x=x, y=y, z=z, on_ground=True
                    ))

                    print("Moved small step.")
                    await asyncio.sleep(MOVE_INTERVAL)

            except Exception as e:
                print("❌ Disconnected:", e)
                break

        print("Reconnecting soon...")
        time.sleep(3)


if __name__ == "__main__":
    asyncio.run(bot_loop())
