import aiohttp
import asyncio
from typing import Optional, List, Dict, Any
from config import get_settings

settings = get_settings()

class TokenService:
    """Service for fetching token data from various blockchain APIs."""
    
    # Cache for token data to avoid repeated API calls
    _cache = {}
    _cache_ttl = 60  # seconds
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _is_cache_valid(self, key: str) -> bool:
        import time
        if key in self._cache:
            return time.time() - self._cache[key]['timestamp'] < self._cache_ttl
        return False
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        if self._is_cache_valid(key):
            return self._cache[key]['data']
        return None
    
    def _set_cache(self, key: str, data: Any):
        import time
        self._cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    # ==================== SOLANA TOKEN METHODS ====================
    
    async def get_solana_token_info(self, token_address: str) -> Optional[Dict]:
        """Fetch Solana token info from Jupiter API."""
        cache_key = f"solana_token_{token_address}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            session = await self._get_session()
            # Jupiter price API
            url = f"https://price.jup.ag/v4/price?ids={token_address}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    token_data = data.get('data', {}).get(token_address, {})
                    
                    # Also try to get metadata from Jupiter token list
                    metadata = await self._get_solana_token_metadata(token_address)
                    
                    result = {
                        'address': token_address,
                        'name': metadata.get('name', token_data.get('name', 'Unknown')),
                        'symbol': metadata.get('symbol', token_data.get('symbol', 'UNK')),
                        'decimals': metadata.get('decimals', token_data.get('decimals', 9)),
                        'price_usd': token_data.get('price'),
                        'price_change_24h': token_data.get('priceChange24h'),
                        'logo_uri': metadata.get('logoURI', ''),
                        'chain': 'solana'
                    }
                    self._set_cache(cache_key, result)
                    return result
        except Exception as e:
            print(f"Error fetching Solana token info: {e}")
        return None
    
    async def _get_solana_token_metadata(self, token_address: str) -> Dict:
        """Get token metadata from Jupiter token list."""
        try:
            session = await self._get_session()
            url = "https://tokens.jup.ag/tokens.json"
            async with session.get(url) as resp:
                if resp.status == 200:
                    tokens = await resp.json()
                    for token in tokens:
                        if token.get('address') == token_address:
                            return token
        except Exception:
            pass
        return {}
    
    async def search_solana_tokens(self, query: str) -> List[Dict]:
        """Search Solana tokens by name or symbol."""
        cache_key = f"solana_search_{query.lower()}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            session = await self._get_session()
            url = "https://tokens.jup.ag/tokens.json"
            async with session.get(url) as resp:
                if resp.status == 200:
                    tokens = await resp.json()
                    query_lower = query.lower()
                    results = []
                    for token in tokens:
                        name = token.get('name', '').lower()
                        symbol = token.get('symbol', '').lower()
                        if query_lower in name or query_lower in symbol:
                            results.append({
                                'address': token.get('address'),
                                'name': token.get('name'),
                                'symbol': token.get('symbol'),
                                'decimals': token.get('decimals', 9),
                                'logo_uri': token.get('logoURI', ''),
                                'chain': 'solana'
                            })
                            if len(results) >= 20:
                                break
                    self._set_cache(cache_key, results)
                    return results
        except Exception as e:
            print(f"Error searching Solana tokens: {e}")
        return []
    
    async def get_solana_trending(self, limit: int = 10) -> List[Dict]:
        """Get trending Solana tokens from Birdeye or DexScreener."""
        cache_key = "solana_trending"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached[:limit]
        
        try:
            session = await self._get_session()
            # Try Birdeye API first
            url = "https://public-api.birdeye.so/defi/token_trending?sort_by=v24hUSD&sort_type=desc&offset=0&limit=20"
            headers = {"X-API-KEY": ""}  # Add API key if available
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    tokens = data.get('data', {}).get('tokens', [])
                    results = []
                    for token in tokens:
                        results.append({
                            'address': token.get('address'),
                            'name': token.get('name'),
                            'symbol': token.get('symbol'),
                            'price_usd': token.get('price'),
                            'price_change_24h': token.get('v24hChangePercent'),
                            'volume_24h': token.get('v24hUSD'),
                            'liquidity_usd': token.get('liquidity'),
                            'logo_uri': token.get('logoURI', ''),
                            'chain': 'solana'
                        })
                    self._set_cache(cache_key, results)
                    return results[:limit]
        except Exception as e:
            print(f"Error fetching Solana trending from Birdeye: {e}")
        
        # Fallback to DexScreener
        try:
            session = await self._get_session()
            url = "https://api.dexscreener.com/latest/dex/trending/solana"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pairs = data.get('pairs', [])
                    results = []
                    seen = set()
                    for pair in pairs:
                        base = pair.get('baseToken', {})
                        addr = base.get('address')
                        if addr and addr not in seen:
                            seen.add(addr)
                            results.append({
                                'address': addr,
                                'name': base.get('name'),
                                'symbol': base.get('symbol'),
                                'price_usd': pair.get('priceUsd'),
                                'price_change_24h': pair.get('priceChange', {}).get('h24'),
                                'volume_24h': pair.get('volume', {}).get('h24'),
                                'liquidity_usd': pair.get('liquidity', {}).get('usd'),
                                'logo_uri': pair.get('info', {}).get('imageUrl', ''),
                                'chain': 'solana'
                            })
                            if len(results) >= limit:
                                break
                    self._set_cache(cache_key, results)
                    return results[:limit]
        except Exception as e:
            print(f"Error fetching Solana trending from DexScreener: {e}")
        
        return []
    
    # ==================== EVM TOKEN METHODS ====================
    
    async def get_evm_token_info(self, token_address: str, chain: str = "ethereum") -> Optional[Dict]:
        """Fetch EVM token info from 1inch or CoinGecko."""
        cache_key = f"evm_token_{chain}_{token_address}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            session = await self._get_session()
            # Try 1inch token API
            chain_id = settings.get_chain_id(chain)
            url = f"https://api.1inch.dev/token/v1.2/{chain_id}/custom/{token_address}"
            headers = {"Authorization": f"Bearer {getattr(settings, 'ONEINCH_API_KEY', '')}"} if hasattr(settings, 'ONEINCH_API_KEY') else {}
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    token = data.get('token', {})
                    result = {
                        'address': token_address,
                        'name': token.get('name', 'Unknown'),
                        'symbol': token.get('symbol', 'UNK'),
                        'decimals': token.get('decimals', 18),
                        'price_usd': None,  # 1inch doesn't always return price
                        'logo_uri': token.get('logoURI', ''),
                        'chain': chain
                    }
                    self._set_cache(cache_key, result)
                    return result
        except Exception as e:
            print(f"Error fetching EVM token info from 1inch: {e}")
        
        # Fallback to CoinGecko
        try:
            session = await self._get_session()
            # Search by contract address on CoinGecko
            chain_map = {
                'ethereum': 'ethereum',
                'base': 'base',
                'arbitrum': 'arbitrum-one',
                'bsc': 'binance-smart-chain',
                'polygon': 'polygon-pos',
                'avalanche': 'avalanche',
            }
            cg_chain = chain_map.get(chain, 'ethereum')
            url = f"https://api.coingecko.com/api/v3/coins/{cg_chain}/contract/{token_address}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result = {
                        'address': token_address,
                        'name': data.get('name', 'Unknown'),
                        'symbol': data.get('symbol', 'UNK').upper(),
                        'decimals': data.get('detail_platforms', {}).get(cg_chain, {}).get('decimals', 18),
                        'price_usd': data.get('market_data', {}).get('current_price', {}).get('usd'),
                        'price_change_24h': data.get('market_data', {}).get('price_change_percentage_24h'),
                        'logo_uri': data.get('image', {}).get('small', ''),
                        'chain': chain
                    }
                    self._set_cache(cache_key, result)
                    return result
        except Exception as e:
            print(f"Error fetching EVM token info from CoinGecko: {e}")
        
        return None
    
    async def search_evm_tokens(self, query: str, chain: str = "ethereum") -> List[Dict]:
        """Search EVM tokens by name or symbol."""
        cache_key = f"evm_search_{chain}_{query.lower()}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            session = await self._get_session()
            # Use 1inch search or CoinGecko search
            url = f"https://api.coingecko.com/api/v3/search?query={query}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    coins = data.get('coins', [])
                    results = []
                    for coin in coins:
                        if coin.get('platform_id') in ['ethereum', 'base', 'arbitrum-one', 'binance-smart-chain', 'polygon-pos', 'avalanche']:
                            results.append({
                                'address': coin.get('contract_address'),
                                'name': coin.get('name'),
                                'symbol': coin.get('symbol', '').upper(),
                                'price_usd': coin.get('current_price'),
                                'logo_uri': coin.get('large', ''),
                                'chain': chain
                            })
                            if len(results) >= 20:
                                break
                    self._set_cache(cache_key, results)
                    return results
        except Exception as e:
            print(f"Error searching EVM tokens: {e}")
        return []
    
    async def get_evm_trending(self, chain: str = "ethereum", limit: int = 10) -> List[Dict]:
        """Get trending EVM tokens from DexScreener."""
        cache_key = f"evm_trending_{chain}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached[:limit]
        
        try:
            session = await self._get_session()
            chain_map = {
                'ethereum': 'ethereum',
                'base': 'base',
                'arbitrum': 'arbitrum',
                'bsc': 'bsc',
                'polygon': 'polygon',
                'avalanche': 'avalanche',
            }
            ds_chain = chain_map.get(chain, 'ethereum')
            url = f"https://api.dexscreener.com/latest/dex/trending/{ds_chain}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pairs = data.get('pairs', [])
                    results = []
                    seen = set()
                    for pair in pairs:
                        base = pair.get('baseToken', {})
                        addr = base.get('address')
                        if addr and addr not in seen:
                            seen.add(addr)
                            results.append({
                                'address': addr,
                                'name': base.get('name'),
                                'symbol': base.get('symbol'),
                                'price_usd': pair.get('priceUsd'),
                                'price_change_24h': pair.get('priceChange', {}).get('h24'),
                                'volume_24h': pair.get('volume', {}).get('h24'),
                                'liquidity_usd': pair.get('liquidity', {}).get('usd'),
                                'logo_uri': pair.get('info', {}).get('imageUrl', ''),
                                'chain': chain
                            })
                            if len(results) >= limit:
                                break
                    self._set_cache(cache_key, results)
                    return results[:limit]
        except Exception as e:
            print(f"Error fetching EVM trending from DexScreener: {e}")
        return []
    
    # ==================== UNIFIED METHODS ====================
    
    async def get_token_info(self, token_address: str, chain: str) -> Optional[Dict]:
        """Get token info for any chain."""
        if chain.lower() == 'solana':
            return await self.get_solana_token_info(token_address)
        else:
            return await self.get_evm_token_info(token_address, chain)
    
    async def search_tokens(self, query: str, chain: str = "solana") -> List[Dict]:
        """Search tokens on any chain."""
        if chain.lower() == 'solana':
            return await self.search_solana_tokens(query)
        else:
            return await self.search_evm_tokens(query, chain)
    
    async def get_trending(self, chain: str = "solana", limit: int = 10) -> List[Dict]:
        """Get trending tokens for any chain."""
        if chain.lower() == 'solana':
            return await self.get_solana_trending(limit)
        else:
            return await self.get_evm_trending(chain, limit)


# Global instance
token_service = TokenService()

