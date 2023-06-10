import socket
import json
import os
import logging
import datetime

logging.basicConfig(filename='sender.log', level=logging.INFO, format='%(asctime)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_comp = '192.168.2.148'  # Change this to the IP address of the computer that runs the receiver code
this_comp = '192.168.2.205'  # Change this to your current IPv4 address
UDP_PORT = 5001
TCP_PORT = 5002
chunk_size = 10240

image_name = input("Please enter the name of the file you want to send without the extension: ")
image_ext = input("Please enter the extension of the file you want to send: Example: .jpg : ")
image_path = image_name + image_ext

chunk_dir = 'chunk_files'
os.makedirs(chunk_dir, exist_ok=True)

chunk_files = []
with open(image_path, 'rb') as file:
    index = 1
    while True:
        chunk_data = file.read(chunk_size)
        if not chunk_data:
            break
        chunk_file_path = f'{chunk_dir}/{image_name}_{index}'
        with open(chunk_file_path, 'wb') as chunk_file:
            chunk_file.write(chunk_data)
        chunk_files.append(chunk_file_path)
        index += 1

# Prepare and send the broadcast message
chunk_list = [os.path.splitext(os.path.basename(chunk_file))[0] for chunk_file in chunk_files]
message = {'chunks': chunk_list}
broadcast_message = json.dumps(message).encode()

sender_socket.sendto(broadcast_message, (receiver_comp, UDP_PORT))
logging.info('Broadcast message sent: %s', message)


class ChunkUploader:
    def __init__(self, content_directory):
        self.content_directory = content_directory

    def handle_request(self, conn, addr):
        data = conn.recv(chunk_size).decode()
        request = json.loads(data)

        if "requestedcontent" in request:
            chunk_name = request["requestedcontent"]
            file_path = os.path.join(self.content_directory, chunk_name)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    content = f.read()
                conn.sendall(content)
                logging.info("Chunk %s sent to %s.", chunk_name, addr[0])
            else:
                logging.info("Chunk %s not found.", chunk_name)
        else:
            logging.info("Invalid request format.")

        conn.close()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((this_comp, TCP_PORT))
            s.listen()

            while True:
                conn, addr = s.accept()
                self.handle_request(conn, addr)


def main():
    content_directory = "chunk_files"

    uploader = ChunkUploader(content_directory)
    print("Starting Uploader")
    uploader.start()


if __name__ == "__main__":
    main()
