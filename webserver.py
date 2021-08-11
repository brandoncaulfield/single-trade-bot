from flask import Flask
from helper import *
from time import sleep

app = Flask(__name__)

@app.route("/")
def display_order_log():
    return "Home Page 2"

@app.route("/stream")
def stream():
    def generate():
        with open('app.log') as file:
            while True:
                yield file.read()
                sleep(5)
    return app.response_class(generate(), mimetype='text/plain')
    
app.run('0.0.0.0')

# import asyncio

# import websockets

# async def get_log():
#         with open('application.log') as file:
#             # return file.read()
#             return app.response_class(file.read(), mimetype='text/plain')

# async def test(websocket, path):

#     with open('application.log') as file:
#             while True:
#                 log = await get_log()
#                 await websocket.send(log)
#                 await asyncio.sleep(3)

    # while True:

        # data = foo()
        # data_string = json.dumps(data)
        # print(data)
        # now = datetime.datetime.utcnow().isoformat() + "Z"
        # await websocket.send(now)
        # await websocket.send(data_string)
        # await asyncio.sleep(random.random() * 3)


# async def handler(websocket, path):
#     async for message in websocket:
#         print(message)
#         await websocket.send(f'Message received: {message}')


# start_server = websockets.serve(test, "127.0.0.1", 5678)

# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()