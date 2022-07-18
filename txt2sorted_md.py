from collections import namedtuple
from itertools import count
import re
import requests

API_SEARCH_URL = "https://jo.azores.gov.pt/api/public/search/ato?"
API_ATO_URL = "https://jo.azores.gov.pt/api/public/ato/"
RETURN_URL = "https://jo.azores.gov.pt/#/ato/"

Record = namedtuple('Record', ['ano', 'serie', 'response', 'hash'])

with open('jo_raa_2022.md') as f:
    lines22 = [line for line in f]
with open('jo_raa_2021.txt') as f:
    lines21 = [line for line in f]
with open('jo_raa_2020.txt') as f:
    lines20 = [line for line in f]
lines = lines22 + lines21 + lines20
# print(lines)
hash_form = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
hashes = map(lambda x: re.search(hash_form, x), lines)
records = []
for i in hashes:
    if i:
        url = API_ATO_URL + i.group()
        response = requests.get(url)
        response_json = response.json() if response and response.status_code == 200 else None
        jornal_ano = response_json['idJornal']['ano']
        jornal_serie = response_json['idJornal']['numeroJornal']
        records.append(Record(int(jornal_ano),int(jornal_serie),response_json,i.group()))
sorted_records = sorted(records, key=lambda t: (-t[0], -t[1]))
for ja,js,json,hash in sorted_records:
        money = re.findall(
            r"(\d{,3})?\.?(\d{,3})?\.(\d{,3})(,\d{2})\w?€", json['considerandos'])
        autoria = (str(json['autoria']).replace('_','', -1)).replace('\n','').replace(".&nbsp;","")
        try:
            max_val = max(list(map(lambda m: int(''.join(
                [re.sub('[,. ]', '', x) for x in m[:-1] if isinstance(x, str)])), money)))
            entry=f"""
{json['descricaoPublicacao']}. 

Autoria: {autoria}.

Sumário: {response_json['sumario']}

Montante máximo referido no corpo do documento: {max_val:,}€

[{RETURN_URL}{hash}]({RETURN_URL}{hash})

---

"""
            print(entry)
        except Exception as e:
            print(e)
            pass
