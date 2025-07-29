# ngpebble

Effortlessly expose your localhost to the internet using FastAPI and WebSocket technology.

## Installation & Usage

### Step 1: Install ngpebble

```bash
pip install ngpebble
```

### Step 2: Start the Tunnel

Run the following command to expose your local server (replace `3000` with your local port):

```bash
ngpebble 3000
```

### Step 3: Access Your Public URL

Once the tunnel is established, you'll receive a public URL like:

```
https://ngpebble.onrender.com/proxy/ng-xxxxx/
```

Use this URL to access your localhost from anywhere!

---
**Note:** Ensure your local server is running before starting the tunnel.