import socket
import json
import os
import logging


class ChunkDownloader:
    def __init__(self, content_dict_file):
        self.content_dict = self.load_content_dict(content_dict_file)
        self.chunk_dir = 'downloaded_chunks'
        os.makedirs(self.chunk_dir, exist_ok=True)
        logging.basicConfig(filename='download.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

    def load_content_dict(self, file):
        with open(file, "r") as f:
            content_dict = json.load(f)
        return content_dict

    def download_chunks(self):
        for chunk_name in self.content_dict.keys():
            self.download_chunk(chunk_name)

    def download_chunk(self, chunk_name):
        if chunk_name not in self.content_dict:
            print(f"Chunk {chunk_name} not found in content dictionary.")
            return

        ip_addresses = self.content_dict[chunk_name]
        for ip_address in ip_addresses:
            if self.try_download_chunk(chunk_name, ip_address):
                return

        print(f"CHUNK {chunk_name} CANNOT BE DOWNLOADED FROM ONLINE PEERS.")

    def try_download_chunk(self, chunk_name, ip_address):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip_address, 5002))
                request = {"requestedcontent": chunk_name}
                s.sendall(json.dumps(request).encode())

                content = b""
                while True:
                    data = s.recv(102400)
                    if not data:
                        break
                    content += data

                chunk_file_path = os.path.join(self.chunk_dir, chunk_name)
                with open(chunk_file_path, "wb") as f:
                    f.write(content)

                logging.info(f"Chunk {chunk_name} downloaded from {ip_address} and saved.")
                print(f"Chunk {chunk_name} downloaded from {ip_address} and saved.")
                return True

        except Exception as e:
            error_msg = f"Error while downloading {chunk_name} from {ip_address}: {str(e)}"
            logging.error(error_msg)
            print(error_msg)

        return False

    def merge_downloaded_chunks(self):
        output_file = input("Please enter the desired name for your file including extension: Example: picture.png : ")
        chunk_files = [f for f in os.listdir(self.chunk_dir) if os.path.isfile(os.path.join(self.chunk_dir, f))]
        chunk_files.sort(key=lambda x: int(x.split('_')[1]))

        existing_chunks = [chunk for chunk in chunk_files if chunk in self.content_dict]
        existing_chunks.sort(key=lambda x: int(x.split('_')[1]))

        with open(output_file, "wb") as output:
            for chunk_file in existing_chunks:
                chunk_file_path = os.path.join(self.chunk_dir, chunk_file)
                with open(chunk_file_path, "rb") as chunk:
                    chunk_data = chunk.read()
                    logging.info(f"Merging chunk: {chunk_file}, Size: {len(chunk_data)}")
                    output.write(chunk_data)

        print(f"All downloaded chunks merged into {output_file}.")


def main():
    content_dict_file = "C:\\Users\\Monster\\PycharmProjects\\Chunk_Sender_With_Ip\\Data"
    downloader = ChunkDownloader(content_dict_file)
    downloader.download_chunks()
    downloader.merge_downloaded_chunks()


if __name__ == "__main__":
    main()
