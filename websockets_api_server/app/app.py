import asyncio
import websockets

async def handle_connection(websocket, path):
    # Handle incoming WebSocket connection
    pass

async def main():
    async with websockets.serve(handle_connection, 'localhost', 8765):
        print('Server started on ws://localhost:8765')
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())