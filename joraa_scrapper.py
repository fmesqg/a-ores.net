import pandas as pd
import requests
import re
import sys
import getopt

API_SEARCH_URL = "https://jo.azores.gov.pt/api/public/search/ato?"
API_ATO_URL = "https://jo.azores.gov.pt/api/public/ato/"
RETURN_URL = "https://jo.azores.gov.pt/#/ato/"


def main(argv):
    min_amount = 100000
    max_amount = 10000000000000
    init_date = ''
    end_date = ''
    try:
        opts, _ = getopt.getopt(
            argv, "", ["from=", "until=", "min=","max=" "max-results="])
    except getopt.GetoptError:
        print('bad options')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--from':
            init_date = arg
        if opt == '--until':
            end_date = arg
        if opt == '--min':
            min_amount = float(arg)
        if opt == '--max':
            max_amount = float(arg)
        if opt == '--max-results':
            max_results = int(arg)
    
    start_dates = list(map(lambda i: str(i).replace(' 00:00:00',''),pd.date_range(init_date,end_date, freq='5D')))
    # print(start_dates)
    end_dates = (start_dates[1:]) + [end_date]
    # print(end_dates)
    intervals = zip(start_dates, end_dates)
    ato_ids_to_check = set()
    for i in intervals:
        #check if result size > 500
    # TODO make this neat with a join
        query = f'fromDate={i[0]}&toDate={i[1]}'
        response = requests.get(f"{API_SEARCH_URL}{query}")
        search_response_json = response.json(
            ) if response and response.status_code == 200 else None

        if search_response_json and 'list' in search_response_json:
            if search_response_json['resultSize'] > 500:
                raise ValueError("Too many results, get smaller search step") # TODO do this automatically
            for entry in search_response_json['list']:
                ato_ids_to_check.add(entry.get('id'))
    print(f"Numero de atos a verificar: {len(ato_ids_to_check)}")

    total = 0
    checked = 0
    for i in ato_ids_to_check:
        url = API_ATO_URL + i
        response = requests.get(url)
        response_json = response.json(    ) if response and response.status_code == 200 else None
        checked += 1
        # print(f"checked: {checked}")

        # temp = re.findall(
        #     r".{,15}€", response.text)
        # for i in temp:
        #     print(i)
        money = re.findall(
            r"(\d{,3})?\.?(\d{,3})?\.(\d{,3})(,\d{2})\w?€", response.text)
        try:
            max_val = max(list(map(lambda m: int(''.join(
            [re.sub('[,. ]', '', x) for x in m[:-1] if isinstance(x, str)])), money)))
            # print(f"{response_json['sumario']}: {max_val}")
            # if ((max_val > min_amount)):
            if ((max_val > min_amount) and (max_val < max_amount)):
                total += 1
                print(f"{response_json['sumario']}\nverbas: {max_val}€\nlink: {RETURN_URL}{i}")
                print(f"Verificados {checked} de {len(ato_ids_to_check)}")
        except Exception as e:
            # print(e)
            pass
            
# TODO max 500 returned

if __name__ == "__main__":
    main(sys.argv[1:])
