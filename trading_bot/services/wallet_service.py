@import json
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from eth_account import Account
from web3 import Web3
from web3.middleware import geth_poa_middleware
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.message import Message
from solders.transaction import Transaction
from mnemonic import Mnemonic
from config import get_settings
from utils.encryption import encrypt_data, decrypt_data
from utils.validators import validate_seed_phrase, validate_private_key_evm, validate_private_key_solana
from database.models import Wallet, ChainType, WalletType
from database.base import get_db


class WalletService:
    def __init__(self):
        self.settings = get_settings()
        self._evm_providers: Dict[str, Web3] = {}
        self._solana_client = None
    
    def _get_evm_provider(self, chain: str) -> Web3:
        chain = chain.lower()
        if chain not in self._evm_providers:
            rpc_url = self.settings.get_evm_rpc(chain)
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if chain in ["bsc", "polygon", "matic"]:
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self._evm_providers[chain] = w3
        return self._evm_providers[chain]
    
    def _get_solana_client(self):
        if self._solana_client is None:
            from solana.rpc.async_api import AsyncClient
            self._solana_client = AsyncClient(self.settings.SOLANA_RPC)
        return self._solana_client
    
    def derive_evm_from_seed(self, seed_phrase: str, chain: str, account_index: int = 0, address_index: int = 0) -> Tuple[str, str]:
        seed = Bip39SeedGenerator(seed_phrase).Generate()
        coin_map = {
            "ethereum": Bip44Coins.ETHEREUM,
            "eth": Bip44Coins.ETHEREUM,
            "base": Bip44Coins.ETHEREUM,
            "arbitrum": Bip44Coins.ETHEREUM,
            "arb": Bip44Coins.ETHEREUM,
            "bsc": Bip44Coins.BINANCE_SMART_CHAIN,
            "polygon": Bip44Coins.POLYGON,
            "matic": Bip44Coins.POLYGON,
            "avalanche": Bip44Coins.AVALANCHE,
            "avax": Bip44Coins.AVALANCHE,
        }
        coin = coin_map.get(chain.lower(), Bip44Coins.ETHEREUM)
        bip44_ctx = Bip44.FromSeed(seed, coin)
        account_ctx = bip44_ctx.Purpose().Coin().Account(account_index).Change(Bip44Changes.CHAIN_EXT).AddressIndex(address_index)
        private_key = account_ctx.PrivateKey().Raw().ToHex()
        address = account_ctx.PublicKey().ToAddress()
        return address, private_key
    
    def derive_solana_from_seed(self, seed_phrase: str, account_index: int = 0) -> Tuple[str, str]:
        seed = Bip39SeedGenerator(seed_phrase).Generate()
        bip44_ctx = Bip44.FromSeed(seed, Bip44Coins.SOLANA)
        account_ctx = bip44_ctx.Purpose().Coin().Account(account_index).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        private_key_bytes = account_ctx.PrivateKey().Raw().ToBytes()
        keypair = Keypair.from_seed(private_key_bytes)
        address = str(keypair.pubkey())
        private_key_b58 = keypair.to_base58_string()
        return address, private_key_b58
    
    def get_evm_account_from_private_key(self, private_key: str) -> Account:
        pk = private_key.strip()
        if pk.startswith("0x"):
            pk = pk[2:]
        return Account.from_key("0x" + pk)
    
    def get_solana_keypair_from_private_key(self, private_key: str) -> Keypair:
        pk = private_key.strip()
        try:
            return Keypair.from_base58_string(pk)
        except Exception:
            pass
        if len(pk) == 64:
            return Keypair.from_bytes(bytes.fromhex(pk))
        elif len(pk) == 128:
            return Keypair.from_seed(bytes.fromhex(pk))
        raise ValueError("Invalid Solana private key format")
    
    async def get_evm_balance(self, chain: str, address: str, token_address: Optional[str] = None) -> Decimal:
        w3 = self._get_evm_provider(chain)
        checksum_address = w3.to_checksum_address(address)
        if token_address is None:
            balance_wei = await w3.eth.get_balance(checksum_address)
            return Decimal(balance_wei) / Decimal(10**18)
        else:
            token_contract = w3.eth.contract(
                address=w3.to_checksum_address(token_address),
                abi=[{"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}]
            )
            balance = await token_contract.functions.balanceOf(checksum_address).call()
            return Decimal(balance) / Decimal(10**18)
    
    async def get_solana_balance(self, address: str, token_mint: Optional[str] = None) -> Decimal:
        client = self._get_solana_client()
        pubkey = Pubkey.from_string(address)
        if token_mint is None:
            response = await client.get_balance(pubkey)
            lamports = response.value
            return Decimal(lamports) / Decimal(10**9)
        else:
            from spl.token.client import Token
            from spl.token.constants import TOKEN_PROGRAM_ID
            token_client = Token(client, Pubkey.from_string(token_mint), TOKEN_PROGRAM_ID, None)
            accounts = await token_client.get_accounts_by_owner(pubkey)
            total = sum(acc.amount for acc in accounts)
            return Decimal(total) / Decimal(10**9)
    
    async def build_evm_tx(self, chain: str, from_address: str, to_address: str, value: int, data: bytes = b"", gas_limit: Optional[int] = None) -> dict:
        w3 = self._get_evm_provider(chain)
        nonce = await w3.eth.get_transaction_count(w3.to_checksum_address(from_address))
        gas_price = await w3.eth.gas_price
        gas_price = int(gas_price * self.settings.GAS_MULTIPLIER)
        if gas_limit is None:
            try:
                gas_limit = await w3.eth.estimate_gas({
                    "from": w3.to_checksum_address(from_address),
                    "to": w3.to_checksum_address(to_address),
                    "value": value,
                    "data": data,
                })
                gas_limit = int(gas_limit * 1.2)
            except Exception:
                gas_limit = 21000 if not data else 300000
        return {
            "nonce": nonce,
            "gasPrice": gas_price,
            "gas": gas_limit,
            "to": w3.to_checksum_address(to_address),
            "value": value,
            "data": data,
            "chainId": self.settings.get_chain_id(chain),
        }
    
    def sign_evm_tx(self, private_key: str, tx_dict: dict) -> str:
        account = self.get_evm_account_from_private_key(private_key)
        signed = account.sign_transaction(tx_dict)
        return "0x" + signed.rawTransaction.hex()
    
    async def send_evm_tx(self, chain: str, signed_tx: str) -> str:
        w3 = self._get_evm_provider(chain)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx)
        return tx_hash.hex()
    
    async def build_and_send_solana_tx(self, keypair: Keypair, instructions: list, priority_fee: Optional[int] = None) -> str:
        from solana.rpc.commitment import Confirmed
        from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit
        client = self._get_solana_client()
        if priority_fee is None:
            priority_fee = int(self.settings.PRIORITY_FEE_SOL * 10**9)
        recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
        all_instructions = [
            set_compute_unit_price(priority_fee),
            set_compute_unit_limit(200000),
        ] + instructions
        message = Message.new_with_blockhash(all_instructions, keypair.pubkey(), recent_blockhash)
        transaction = Transaction([keypair], message, recent_blockhash)
        result = await client.send_raw_transaction(transaction.serialize(), opts={"skip_preflight": False, "preflight_commitment": Confirmed})
        return str(result.value)
    
    async def import_wallet(self, user_id: int, chain: str, wallet_type: str, data: str, name: Optional[str] = None) -> Wallet:
        from sqlalchemy import select, update
        chain = chain.lower()
        wallet_type = wallet_type.lower()
        if wallet_type == "seed_phrase":
            is_valid, error = validate_seed_phrase(data)
            if not is_valid:
                raise ValueError(f"Invalid seed phrase: {error}")
            if chain in ["evm", "ethereum", "eth", "base", "arbitrum", "arb", "bsc", "polygon", "matic", "avalanche", "avax"]:
                address, private_key = self.derive_evm_from_seed(data, chain)
                encrypted_data = encrypt_data(json.dumps({"seed_phrase": data, "private_key": private_key}))
            elif chain in ["solana", "sol"]:
                address, private_key = self.derive_solana_from_seed(data)
                encrypted_data = encrypt_data(json.dumps({"seed_phrase": data, "private_key": private_key}))
            else:
                raise ValueError(f"Unsupported chain: {chain}")
        elif wallet_type == "private_key":
            if chain in ["evm", "ethereum", "eth", "base", "arbitrum", "arb", "bsc", "polygon", "matic", "avalanche", "avax"]:
                is_valid, address, error = validate_private_key_evm(data)
                if not is_valid:
                    raise ValueError(f"Invalid EVM private key: {error}")
                encrypted_data = encrypt_data(json.dumps({"private_key": data}))
            elif chain in ["solana", "sol"]:
                is_valid, address, error = validate_private_key_solana(data)
                if not is_valid:
                    raise ValueError(f"Invalid Solana private key: {error}")
                encrypted_data = encrypt_data(json.dumps({"private_key": data}))
            else:
                raise ValueError(f"Unsupported chain: {chain}")
        else:
            raise ValueError(f"Unknown wallet type: {wallet_type}")
        
        async with get_db() as session:
            chain_enum = ChainType.EVM
            if chain in ["solana", "sol"]:
                chain_enum = ChainType.SOLANA
            elif chain in ["ton"]:
                chain_enum = ChainType.TON
            
            existing = await session.execute(
                select(Wallet).where(
                    Wallet.user_id == user_id,
                    Wallet.chain == chain_enum,
                    Wallet.address == address
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Wallet already imported")
            
            await session.execute(
                update(Wallet).where(
                    Wallet.user_id == user_id,
                    Wallet.chain == chain_enum,
                    Wallet.is_default == True
                ).values(is_default=False)
            )
            
            wallet_type_enum = WalletType.SEED_PHRASE if wallet_type == "seed_phrase" else WalletType.PRIVATE_KEY
            wallet = Wallet(
                user_id=user_id,
                chain=chain_enum,
                address=address,
                name=name or f"{chain.capitalize()} Wallet",
                wallet_type=wallet_type_enum,
                encrypted_data=encrypted_data,
                is_active=True,
                is_default=True,
            )
            session.add(wallet)
            await session.flush()
            await session.refresh(wallet)
            return wallet
    
    async def get_user_wallets(self, user_id: int, chain: Optional[str] = None) -> List[Wallet]:
        from sqlalchemy import select
        async with get_db() as session:
            query = select(Wallet).where(Wallet.user_id == user_id, Wallet.is_active == True)
            if chain:
                chain_enum = ChainType.EVM
                if chain.lower() in ["solana", "sol"]:
                    chain_enum = ChainType.SOLANA
                elif chain.lower() in ["ton"]:
                    chain_enum = ChainType.TON
                query = query.where(Wallet.chain == chain_enum)
            result = await session.execute(query.order_by(Wallet.is_default.desc(), Wallet.created_at))
            return list(result.scalars().all())
    
    async def get_wallet(self, wallet_id: int, user_id: int) -> Optional[Wallet]:
        from sqlalchemy import select
        async with get_db() as session:
            result = await session.execute(
                select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user_id)
            )
            return result.scalar_one_or_none()
    
    async def get_wallet_private_data(self, wallet: Wallet) -> dict:
        decrypted = decrypt_data(wallet.encrypted_data)
        return json.loads(decrypted) if decrypted else {}
    
    async def set_default_wallet(self, user_id: int, wallet_id: int) -> bool:
        from sqlalchemy import select, update
        async with get_db() as session:
            wallet = await session.execute(
                select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user_id)
            )
            wallet = wallet.scalar_one_or_none()
            if not wallet:
                return False
            await session.execute(
                update(Wallet).where(
                    Wallet.user_id == user_id,
                    Wallet.chain == wallet.chain,
                    Wallet.is_default == True
                ).values(is_default=False)
            )
            wallet.is_default = True
            return True
    
    async def delete_wallet(self, user_id: int, wallet_id: int) -> bool:
        from sqlalchemy import select, update
        async with get_db() as session:
            wallet = await session.execute(
                select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user_id)
            )
            wallet = wallet.scalar_one_or_none()
            if not wallet:
                return False
            wallet.is_active = False
            return True
    
    async def update_wallet_balances(self, wallet: Wallet) -> dict:
        balances = {}
        try:
            if wallet.chain == ChainType.EVM:
                native_bal = await self.get_evm_balance(wallet.chain.value, wallet.address)
                balances["native"] = str(native_bal)
            elif wallet.chain == ChainType.SOLANA:
                native_bal = await self.get_solana_balance(wallet.address)
                balances["native"] = str(native_bal)
            wallet.balance_cache = balances
            wallet.last_balance_update = datetime.utcnow()
            async with get_db() as session:
                session.add(wallet)
        except Exception:
            pass
        return balances
