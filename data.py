import requests
from datetime import datetime
import time
import pytz
import psycopg2

def fetch_polygon_tx_hash(address, start, tx_hash):
    try:
        url = f"https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress=0xc2132d05d31c914a87c6611c10748aeb04b58e8f&address={address}&sort=desc&startblock={start+1}&endblock=99999999&apikey=apikey"
        time.sleep(0.5)
        resp = requests.get(url, timeout=60)
        tx_results = []
        if resp.status_code == 200:
            if resp.json()['status'] == '1':
                data = resp.json()['result']
                for tx in data:  
                    if tx['hash'] == tx_hash:
                        # Convertir a GMT-3
                        gmt3 = pytz.timezone('Etc/GMT+3')
                        tx_datetime = datetime.fromtimestamp(float(tx['timeStamp']), pytz.utc).astimezone(gmt3)

                        # Formatear la fecha y hora
                        formatted_datetime = tx_datetime.strftime('%Y-%m-%d %H:%M:%S')

                        tx_results.append({
                            'address': address, 
                            'amount_usdt': float(tx['value']) / 1000000, 
                            'tx_hash': tx['hash'], 
                            'datetime': formatted_datetime, 
                            'block_number': tx['blockNumber'], 
                            'network_id': 5
                        })
            return tx_results
        else:
            raise Exception("Bad response from server")
    except Exception as e:
        print(f"Exception {e} for address: {address}")
        raise

conn = psycopg2.connect("dbname=yourdbname user=youruser password=yourpassword host=yourhost")

cur = conn.cursor()

txids = [
'0xa65d6066e4673d7943312af3c0ece70b746e2e4fb51847b1f712a28da6733836',
'0x0b7a6c43f079c6b58c541f84683d0d6926ce720a1e4a1a22fc91c1e5c7e36b5e',
'0x9c95e8a0b8daab7e7238d23e9c304b55012a9d8b0e8e20164d6cefb32f80d20a',
'0x74cb7f2b2e434f23521f0a14b52dba2f8b2a66d78fe09907188a2bb910dd0724',
'0xbe5257b64162b155f55c9e84a0e6a3967ea2868829824030737a9f2127f14ef2',
'0xeffb85e37227e9b3d17f5c409619e8eea98186d8c9cbd3d965cde52992291c91',
'0xbd45b7c58adb339524dd4cdb0de5f5253a85491767400b5bd19363e19350bc87',
'0xaf594a96554082657d46ded04f5d7eeff5a77d8fcf77b0dc7736b890231c34ad',
'0x463dcac656a1a1a7bbcf160ec39bc637dfed82c99d6404e39af1860a58dacf40',
'0xdee7075e201fc0d4019295cda11709b25a2e681f617b5b319c78f21c6d35f046',
'0x307d7004ee3513fb318560b8be9e0b67751e78ac87f92de77f42a2f56933f246',
'0xe7c7aaa67baf183718c4558d6198a0f952bec6d64e214024f740f993217a74f3',
'0x99805284d0b720dda8cac2edd3b409fa675ef953547b632921a60414c7a2d759',
'0x81b6dc43edb1f4d8a321dc78197ff9195999c46f0d0802cf81a72a10975f7d7e',
'0x26d8955c08db958d43d60fbcc6269de20b47aa5f9dac1f13deedd5686f9572a3',
'0xbff7e38f2c0d3ade8b2b37d6c798bcad715065afb68b4223ccf19227153067dd'
]

query = """
SELECT pprs.txid, mw.address
FROM pix_payment_req_status pprs 
JOIN pix_payment_requests ppr ON ppr.pix_id = pprs.pix_id 
JOIN quotes q ON q.quote_id = ppr.quote_id 
JOIN checkouts c ON c.merchant_id = q.merchant_id AND c.store_id = q.store_id AND c.checkout_id = q.checkout_id 
JOIN merchant_wallets mw ON mw.wallet_id = c.wallet_id AND mw.merchant_id = c.merchant_id 
WHERE pprs.txid IN %s
AND pprs.pix_payment_status_id = 1;
"""
cur.execute(query, (tuple(txids),))

resultados = cur.fetchall()
objtTxid = {txid: address for txid, address in resultados}

cur.close()
conn.close()

data = []

for tx_hash, address in objtTxid.items():
    start = 0
    results = fetch_polygon_tx_hash(address, start, tx_hash)
    
    if results:
      data.extend(results)

ids = [
"1703374621925",
"1703374614529",
"1703375006178",
"1703375137141",
"1703376374330",
"1703376415632",
"1703377027604",
"1703377440056",
"1703377608775",
"1703377817337",
"1703378075792",
"1703375448140",
"1703376857460",
"1703377184246",
"1703374871315",
"1703374978797"
]

def fetch_data(pix_id):
    url = f"https://connect.smartpay.com.vc/api/swapix/opstatus?operation_id={pix_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        json_response = response.json()
        if json_response['status'] == 'ok' and 'data' in json_response:
            return json_response['data']  # Devuelve solo la parte 'data' del JSON
        else:
            print(f"Error in response data for operation_id {pix_id}: {json_response}")
            return None
    else:
        print(f"Error fetching data for operation_id {pix_id}: {response.status_code}, {response.text}")
        return None

data2 = []

for pix_id in ids:
    data_ = fetch_data(pix_id)
    if data_:
        data2.append(data_)

def merge_data(data1, data2):
    merged_data = []
    
    data1_dict = {item['tx_hash']: item for item in data1}
    
    # Iterar sobre data2 y unir con data1 si txid coincide con tx_hash
    for item in data2:
        txid = item.get('txid')
        if txid in data1_dict:
            merged_record = {**data1_dict[txid], **item}
            synthesized_record = {
                "tx_hash": merged_record["tx_hash"],
                "address": merged_record["address"],
                "amount_brl": float(merged_record["rate"]["total_brl"]),
                "amount_usdt": float(merged_record["rate"]["send_pxusdt"]),
                "swapix_fee_brl": float(merged_record["rate"]["fee_brl"]),
                "rate": float(merged_record["rate"]["price_usd"]),
                "datetime": merged_record["datetime"],
                "block_number": int(merged_record["block_number"]),
                "network_id": merged_record["network_id"],
            }
            
            merged_data.append(synthesized_record)

    return merged_data

final_data = merge_data(data, data2)
print(final_data)
