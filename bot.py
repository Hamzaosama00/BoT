from lodestone import Client, OfflineSession
import asyncio
import random
import socket
import time

SERVER_HOST = "TheUnexpectedSMP.aternos.me"
SERVER_PORT = 40070
USERNAME = "BoT"

CHECK_INTERVAL = 5
MOVE_INTERVAL = 8


def server_online():
    """TCP Check if server is online"""
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((SERVER_HOST, SERVER_PORT))
        s.close()
        return True
    except:
        return False


async def run_bot():
    while True:
        print("Checking server status...")
        if not server_online():
            print("Server offline, rechecking...")
            time.sleep(CHECK_INTERVAL)
            continue

        print("✅ Server ONLINE — Joining...")

        session = OfflineSession(USERNAME)
        client = Client(session)

        try:
            await client.connect(SERVER_HOST, SERVER_PORT)
            print("✅ Connected to SMP!")

            # Movement Loop
            async def movement():
                while client.connected:
                    try:
                        dx = random.uniform(-0.2, 0.2)
                        dz = random.uniform(-0.2, 0.2)

                        await client.position.move(dx, 0, dz)
                        print(f"Moved tiny step dx={dx}, dz={dz}")

                        await asyncio.sleep(MOVE_INTERVAL)
                    except:
                        break

            asyncio.create_task(movement())

            # Stay alive
            while client.connected:
                await asyncio.sleep(1)

        except Exception as e:
            print("❌ Error:", e)

        print("Disconnected. Reconnecting...")
        time.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_bot())
