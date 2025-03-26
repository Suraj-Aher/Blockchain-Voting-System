from flask import Flask, render_template, request, redirect
import hashlib
import json
from time import time

app = Flask(__name__)

# Random voter database with 20-30 pre-stored valid voter IDs (for validation)
VALID_VOTERS = {f"voter_{i}" for i in range(1, 31)}

class BlockchainVotingSystem:
    def __init__(self):
        self.chain = []               # Blockchain containing valid votes
        self.current_votes = []       # Unmined votes
        self.fake_votes = []          # Store fake votes here
        self.create_block(previous_hash='1', proof=100)  # Genesis block

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'votes': self.current_votes,
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.current_votes = []  # Reset vote list after mining
        self.chain.append(block)
        return block

    def add_vote(self, voter_id, candidate):
        if voter_id in VALID_VOTERS:
            vote = {'voter_id': voter_id, 'candidate': candidate}
            self.current_votes.append(vote)
        else:
            # If voter_id is not valid, store it as a fake vote
            self.fake_votes.append({'voter_id': voter_id, 'candidate': candidate})
        return self.last_block['index'] + 1

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def last_block(self):
        return self.chain[-1]

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            block, prev_block = self.chain[i], self.chain[i - 1]
            if block['previous_hash'] != self.hash(prev_block):
                return False
            if not self.valid_proof(prev_block['proof'], block['proof']):
                return False
        return True

blockchain = BlockchainVotingSystem()

@app.route('/')
def index():
    return render_template('index.html', blockchain=blockchain.chain, fake_votes=blockchain.fake_votes)

@app.route('/add_vote', methods=['POST'])
def add_vote():
    voter_id, candidate = request.form['voter_id'], request.form['candidate']
    blockchain.add_vote(voter_id, candidate)
    return redirect('/')

@app.route('/mine_block')
def mine_block():
    last_proof = blockchain.last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    previous_hash = blockchain.hash(blockchain.last_block)
    blockchain.create_block(proof, previous_hash)
    return redirect('/')

@app.route('/validate')
def validate():
    is_valid = blockchain.is_chain_valid()
    return render_template('validate.html', is_valid=is_valid)

if __name__ == '__main__':
    app.run(debug=True)
