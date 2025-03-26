import hashlib
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash="0")

    def create_block(self, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "data": [],
            "previous_hash": previous_hash
        }
        block["hash"] = self.hash_block(block)
        self.chain.append(block)

    def add_block(self, data):
        previous_block = self.chain[-1]
        self.create_block(previous_hash=previous_block["hash"])
        self.chain[-1]["data"] = data

    @staticmethod
    def hash_block(block):
        block_string = f'{block["index"]}{block["timestamp"]}{block["data"]}{block["previous_hash"]}'
        return hashlib.sha256(block_string.encode()).hexdigest()
