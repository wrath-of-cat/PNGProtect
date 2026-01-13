from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.watermarking import load_image_from_bytes, extract_watermark_lsb
from app.services.hashing import sha256_bytes
import os
from web3 import Web3

router = APIRouter()


@router.get('/abi', summary='Get registry contract ABI and address')
async def get_registry_abi():
    # Minimal ABI for frontend use
    abi = [
        {"inputs":[{"internalType":"bytes32","name":"uuidHash","type":"bytes32"}],"name":"register","outputs":[],"stateMutability":"nonpayable","type":"function"},
        {"inputs":[{"internalType":"bytes32","name":"uuidHash","type":"bytes32"}],"name":"getOwner","outputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"timestamp","type":"uint256"}],"stateMutability":"view","type":"function"}
    ]
    contract_address = os.environ.get('CONTRACT_ADDRESS') or None
    return {"abi": abi, "contract_address": contract_address}


@router.post('/verify-image', summary='Extract watermark UUID from uploaded image and check on-chain owner')
async def verify_image_onchain(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='Invalid file type')
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail='Empty payload')

    image = load_image_from_bytes(raw)
    extracted_text, match_ratio = extract_watermark_lsb(image)
    if extracted_text == 'Unknown':
        return {'found': False, 'message': 'No watermark UUID found', 'match_ratio': match_ratio}

    # compute bytes32 hash using keccak256 (web3)
    uuid_hash = Web3.keccak(text=extracted_text)

    rpc = os.environ.get('POLYGON_RPC_URL')
    contract_address = os.environ.get('CONTRACT_ADDRESS')
    if not rpc or not contract_address:
        return {'found': True, 'watermark_id': extracted_text, 'match_ratio': match_ratio, 'onchain': False, 'message': 'RPC or contract not configured'}

    w3 = Web3(Web3.HTTPProvider(rpc))
    abi = [
        {"inputs":[{"internalType":"bytes32","name":"uuidHash","type":"bytes32"}],"name":"getOwner","outputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"timestamp","type":"uint256"}],"stateMutability":"view","type":"function"}
    ]
    contract = w3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=abi)
    try:
        owner, timestamp = contract.functions.getOwner(uuid_hash).call()
        if owner == '0x0000000000000000000000000000000000000000':
            return {'found': True, 'watermark_id': extracted_text, 'match_ratio': match_ratio, 'onchain': False}
        return {'found': True, 'watermark_id': extracted_text, 'match_ratio': match_ratio, 'onchain': True, 'owner': owner, 'timestamp': timestamp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'On-chain query failed: {e}')
