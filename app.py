from flask import Flask, render_template_string, request
import os
from mnemonic import Mnemonic
from eth_account import Account
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Wallet Breeder</title>
    <style>
        body { background: #0a0a0a; color: #0f0; font-family: monospace; text-align: center; }
        button { background: #111; border: 1px solid #0f0; color: #0f0; padding: 10px 20px; margin: 5px; cursor: pointer; }
        pre { background: #111; padding: 10px; white-space: pre-wrap; text-align: left; }
    </style>
</head>
<body>
    <h1>💀 WALLET BREEDER 💀</h1>
    <form method="POST">
        <button name="type" value="exodus">Exodus (BTC/ETH)</button>
        <button name="type" value="trust">Trust Wallet</button>
        <button name="type" value="coinbase">Coinbase Wallet</button>
        <button name="type" value="metamask">MetaMask</button>
    </form>
    {% if wallets %}
        <h2>5 Fresh Wallets for {{ wallet_type }}</h2>
        {% for w in wallets %}
            <pre>
Address: {{ w.address }}
Private Key: {{ w.private_key }}
Mnemonic (12 words): {{ w.mnemonic }}
            </pre>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

def generate_mnemonic():
    return Mnemonic("english").generate(strength=128)

def exodus_wallets(n=5):
    out = []
    for _ in range(n):
        mnem = generate_mnemonic()
        seed = Bip39SeedGenerator(mnem).Generate()
        btc = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).DeriveDefaultPath()
        btc_addr = btc.PublicKey().ToAddress()
        btc_priv = btc.PrivateKey().Raw().ToHex()
        Account.enable_unaudited_hdwallet_features()
        eth = Account.from_mnemonic(mnem, account_path="m/44'/60'/0'/0/0")
        out.append({
            'address': f"BTC: {btc_addr}\nETH: {eth.address}",
            'private_key': f"BTC: {btc_priv}\nETH: {eth.key.hex()}",
            'mnemonic': mnem
        })
    return out

def trust_wallets(n=5):
    out = []
    for _ in range(n):
        mnem = generate_mnemonic()
        Account.enable_unaudited_hdwallet_features()
        eth = Account.from_mnemonic(mnem, account_path="m/44'/60'/0'/0/0")
        out.append({
            'address': f"ETH/BSC: {eth.address}",
            'private_key': eth.key.hex(),
            'mnemonic': mnem
        })
    return out

def coinbase_wallets(n=5):
    return trust_wallets(n)  # same derivation path for ETH

def metamask_wallets(n=5):
    return trust_wallets(n)

@app.route('/', methods=['GET','POST'])
def index():
    wallets = None
    wallet_type = ""
    if request.method == 'POST':
        wallet_type = request.form['type']
        if wallet_type == 'exodus':
            wallets = exodus_wallets(5)
        elif wallet_type == 'trust':
            wallets = trust_wallets(5)
        elif wallet_type == 'coinbase':
            wallets = coinbase_wallets(5)
        elif wallet_type == 'metamask':
            wallets = metamask_wallets(5)
    return render_template_string(HTML_TEMPLATE, wallets=wallets, wallet_type=wallet_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
