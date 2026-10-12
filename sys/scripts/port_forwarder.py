"""Lightweight TCP port forwarder for Chrome CDP multi-profile endpoints.
Forwards incoming connections on ports 9223 and 9224 to the primary Chrome debugging port 9222.
"""
import asyncio
import sys

async def forward(reader_in, writer_in, target_port=9222):
    try:
        reader_out, writer_out = await asyncio.open_connection('127.0.0.1', target_port)
    except Exception as e:
        writer_in.close()
        await writer_in.wait_closed()
        return

    async def pipe(r, w):
        try:
            while not r.at_eof():
                data = await r.read(65536)
                if not data:
                    break
                w.write(data)
                await w.drain()
        except Exception:
            pass
        finally:
            try:
                w.close()
                await w.wait_closed()
            except Exception:
                pass

    await asyncio.gather(pipe(reader_in, writer_out), pipe(reader_out, writer_in))

async def start_proxy(listen_port, target_port=9222):
    server = await asyncio.start_server(
        lambda r, w: forward(r, w, target_port),
        '127.0.0.1', listen_port
    )
    print(f"Proxy listening on 127.0.0.1:{listen_port} -> 127.0.0.1:{target_port}")
    return server

async def main():
    servers = []
    for port in [9223, 9224]:
        try:
            s = await start_proxy(port, target_port=9222)
            servers.append(s)
        except Exception as e:
            print(f"Port {port} already bound or failed: {e}")

    if not servers:
        print("No servers started.")
        return

    print("CDP Port Forwarder active. Press Ctrl+C to stop.")
    await asyncio.gather(*(s.serve_forever() for s in servers))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
