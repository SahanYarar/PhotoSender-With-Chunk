import socket
import json
import os
import logging

logging.basicConfig(filename='content_discovery.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Receiver IP and port
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_host = '0.0.0.0'
receiver_port = 5001
CONTENT_DIRECTORY = "C:\\Users\\Monster\\PycharmProjects\\Chunk_Sender_With_Ip\\Data"
chunk_size = 102400
def parse_broadcast_message(message):
    try:
        data = json.loads(message)
        return data.get("chunks", [])
    except json.JSONDecodeError:
        return []

receiver_socket.bind((receiver_host, receiver_port))

logging.info("Content Discovery started. Listening for broadcast messages...")
print("Content Discovery started. Listening for broadcast messages...")

if os.path.exists(CONTENT_DIRECTORY):
    # Delete the file
    os.remove(CONTENT_DIRECTORY)
    logging.info(f"The file '{CONTENT_DIRECTORY}' has been deleted.")
else:
    logging.info(f"The file '{CONTENT_DIRECTORY}' does not exist.")

if not os.path.exists(CONTENT_DIRECTORY):
    with open(CONTENT_DIRECTORY, "w") as file:
        json.dump({}, file)

while True:
    message, addr = receiver_socket.recvfrom(chunk_size)
    print(f"Connected to {addr}")
    logging.info('Received data from: %s', addr)

    chunks = parse_broadcast_message(message.decode())

    with open(CONTENT_DIRECTORY, "r") as file:
        content_dictionary = json.load(file)

    for chunk in chunks:
        content_dictionary.setdefault(chunk, []).append(addr[0])

    hosted_content = ", ".join(chunks)
    logging.info('%s: %s', addr[0], hosted_content)

    with open(CONTENT_DIRECTORY, "w") as file:
        json.dump(content_dictionary, file)
        print("File Updated")

    exit(0)
