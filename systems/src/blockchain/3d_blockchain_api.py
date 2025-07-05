"""
3D Blockchain REST API (Python Flask Skeleton)
---------------------------------------------
Provides plug-and-play API endpoints for the 3D blockchain system.
"""
from flask import Flask, request, jsonify
from 3d_blockchain import Blockchain3D

app = Flask(__name__)
blockchain = Blockchain3D()

@app.route('/blockchain', methods=['GET'])
def get_chain():
    return jsonify({"chain": [block.__dict__ for block in blockchain.chain]})

@app.route('/mine_block', methods=['POST'])
def mine_block():
    data = request.json
    blockchain.create_block(data['x'], data['y'], data['z'], data['transactions'])
    return jsonify({"message": "Block added", "chain": [block.__dict__ for block in blockchain.chain]})

if __name__ == '__main__':
    app.run(debug=True)
