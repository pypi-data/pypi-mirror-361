import asyncio
import sys
import random
import string
import json
import requests
import websockets


def generate_client_id():
    return "ng-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


async def tunnel(local_port, client_id):
    SERVER_URL = f"wss://ngpebble.onrender.com/ws/{client_id}"
    LOCAL_HOST = f"http://localhost:{local_port}"

    async with websockets.connect(SERVER_URL) as ws:
        print(f"[*] Tunnel established")
        print(
            f"[*] Public URL: https://ngpebble.onrender.com/proxy/{client_id}/")

        while True:
            try:
                data = await ws.recv()
                payload = json.loads(data)

                method = payload["method"]
                path = payload["path"]
                headers = payload.get("headers", {})
                body = payload.get("body", "")

                resp = requests.request(
                    method,
                    f"{LOCAL_HOST}/{path}",
                    headers=headers,
                    data=body
                )

                await ws.send(json.dumps({
                    "status": resp.status_code,
                    "body": resp.text
                }))

            except Exception as e:
                await ws.send(json.dumps({
                    "status": 500,
                    "body": f"[Tunnel Error] {str(e)}"
                }))


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m ngpebble <local_port>")
        sys.exit(1)

    port = sys.argv[1]
    client_id = generate_client_id()

    asyncio.run(tunnel(port, client_id))


if __name__ == "__main__":
    main()
