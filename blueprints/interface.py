import jwt
import time
import math
import requests
import json
import base64
from pprint import pprint
from datetime import datetime, timedelta
import operator
import itertools
from copy import deepcopy



def combine_fees(input_data):
    new_data = deepcopy(input_data)
    data = new_data[1]
    if data["records"]:
        d = sorted(data["records"], key=operator.itemgetter("type"))
        output_dict = {}
        for i, g in itertools.groupby(d, key=operator.itemgetter("type")):
            output_dict[i] = list(g)

        other_records = []
        for key, value in output_dict.items():
            if key != "Fee":
                other_records = [*other_records, *value]

        fee_not_found_records = []
        if "Fee" in output_dict:
            fee_records = output_dict["Fee"]
            for record in fee_records:
                found = False
                if "original_authorization_id" in record:
                    for index, org_record in enumerate(other_records):
                        if "id" in org_record:
                            if org_record["id"] == record["original_authorization_id"]:
                                other_records[index]["account_amount"] = round(other_records[index]["account_amount"] + \
                                    record["account_amount"],2)
                                found = True
                                break
                if not found:
                    fee_not_found_records.append(record)

        other_records = [*other_records, *fee_not_found_records]
        new_data[1]["records"] = other_records
    return new_data


def sort_by_date(input_data):
    new_data = deepcopy(input_data)
    for item in new_data[1]["records"]:
        temp = datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=5)
        item["date"] = temp.strftime("%Y-%m-%dT%H:%M:%SZ")
    # temp_data = (input_data[0], input_data[1].copy())
    # records = temp_data[1]["records"].copy()
    records = new_data[1]["records"].copy()
    records.sort(reverse=True, key=lambda x: x['date'])
    # records.sort(reverse=True, key=lambda x: datetime.strptime(
    #     x['date'], "%Y-%m-%dT%H:%M:%SZ"), )
    new_data[1]["records"] = records
    return new_data


def find_card(json_data: dict, last_four_digits: str):
    for card in json_data["cards"]:
        if "masked_card_number" in card:
            if card["masked_card_number"].endswith(last_four_digits):
                return card
    return None


class InterfaceWallet:
    def __init__(self):
        #Main account id get from wallester account
        self.main_account_id = "914b23a6cad1154f90afed744751652a"
        self.public_key = ""
        self.private_key = ""
        with open("key_private", "r") as fh:
            self.private_key = fh.read()
        with open("key_public", "r") as fh:
            self.public_key = fh.read()
        #Company id get from wallester 
        self.company_id = "e917ac914f21570a974d236788f1780e"
        self.headers = {
            "Authorization": "",
            "Content-Type": "application/json"
        }

    def get_encoded(self):
                                #Api key get from wallester
        auth_data = {"api_key": "6XenZdrlCCIEIy3aQnb5QytgmHJ1K6fX",
                     "ts": math.floor(time.time())
                     }
        encoded = jwt.encode(auth_data, self.private_key, algorithm='RS256')
        return encoded

    def get_card(self, last_four_digits: str):
        count = 1000
        offset = 0
        url = f"https://api-frontend.wallester.com/v1/companies/{self.company_id}/cards"
        encoded = self.get_encoded()
        headers = self.headers.copy()
        headers["Authorization"] = "Bearer " + encoded
        params = {
            "from_record": offset,
            "records_count": count
        }
        response = requests.get(url, headers=headers, params=params)
        cards = {"cards": []}
        if response.status_code == 200:
            data = response.json()
            cards["cards"] = data["cards"]
            total_number = data["total_records_number"]
            last_fetched = offset + count
            if total_number > last_fetched:
                while total_number > last_fetched:
                    offset = last_fetched
                    encoded = self.get_encoded()
                    headers["Authorization"] = "Bearer " + encoded
                    params = {
                        "from_record": offset,
                        "records_count": count
                    }
                    response = requests.get(
                        url, headers=headers, params=params)
                    if response.status_code == 200:
                        data_new = response.json()
                        cards["cards"] = [*cards["cards"], *data_new["cards"]]
                        last_fetched = last_fetched + count
                    else:
                        result = f"Card fetched failed, {response.status_code}"
                        return (False, result)
            print("company cards fetched successfull")
            with open(f"latest_company_cards.json", "w") as fh:
                json.dump(cards, fh, indent=4)
            card = find_card(cards, last_four_digits)
            return (True, card)
        else:
            result = f"Main card fetched failed, {response.status_code}"
        return (False, result)

    def get_card_transactions(self, last_four_digits: str):
        card = self.get_card(last_four_digits)
        if card[0]:
            if card[1]:
                card = card[1]
                card_id = card["id"]
                print(
                    f"Card {last_four_digits} found successfull with id {card_id}")
                transactions = self.fetch_card_transactions_api(card_id)
                if transactions[0]:
                    if transactions[1]:
                        transactions = transactions[1]
                        print("Successfully fetched tranactions")
                        with open(f"card_transactions_{last_four_digits}.json", "w") as fh:
                            json.dump(transactions, fh, indent=4)
                        return (True, transactions)
                    else:
                        tranactions = {"transactions": []}
                        return (True, transactions)
            else:
                result = f"Card ending with {last_four_digits} not found."
                print(result)
                return (False, result)
        else:
            print(card[1])
            return (False, card[1])

    def fetch_card_transactions_api(self, card_id: str):
        try:
            count = 1000
            offset = 0
            url = f"https://api-frontend.wallester.com/v1/cards/{card_id}/transactions"
            encoded = self.get_encoded()
            params = {
                "from_record": offset,
                "records_count": count
            }
            headers = self.headers.copy()
            headers["Authorization"] = "Bearer " + encoded
            response = requests.get(url, headers=headers, params=params)
            tranactions = {"transactions": []}
            if response.status_code == 200:
                data = response.json()
                tranactions["transactions"] = data["transactions"]
                total_number = data["total_records_number"]
                last_fetched = offset + count
                if total_number > last_fetched:
                    while total_number > last_fetched:
                        offset = last_fetched
                        encoded = self.get_encoded()
                        headers["Authorization"] = "Bearer " + encoded
                        params = {
                            "from_record": offset,
                            "records_count": count
                        }
                        response = requests.get(
                            url, headers=headers, params=params)
                        if response.status_code == 200:
                            data_new = response.json()
                            tranactions["transactions"] = [
                                *tranactions["transactions"], *data_new["transactions"]]
                            last_fetched = last_fetched + count
                        else:
                            result = f"Get card transaction failed for {card_id} with status code, {response.status_code}"
                            return (False, result) 
                return (True, tranactions)
            else:
                result = f"Get main card transaction failed for {card_id} with status code, {response.status_code}"
                return (False, result)
        except Exception as e:
            result = f"Error in getting getting card trasaction, {str(e)}"
            return (False, result)

    def card_action(self, last_four_digits: str, action: str):
        print("Performing card action", last_four_digits, action)
        try:
            card = self.get_card(last_four_digits)
            if card[0]:
                if card[1]:
                    card = card[1]
                    card_id = card["id"]
                    url = ""
                    payload = {}
                    if action == "unfreeze":
                        url = f"https://api-frontend.wallester.com/v1/cards/{card_id}/unblock"
                    if action == "freeze":
                        url = f"https://api-frontend.wallester.com/v1/cards/{card_id}/block"
                        payload = {
                            "block_type": "BlockedByCardholder"
                        }
                    # close
                    if action == "permanentaly close":
                        url = f"https://api-frontend.wallester.com/v1/cards/{card_id}/close"
                        payload = {
                            "close_reason": "ClosedByCardholder"
                        }
                    encoded = self.get_encoded()
                    headers = self.headers.copy()
                    headers["Authorization"] = "Bearer " + encoded
                    response = requests.patch(
                        url, headers=headers, json=payload)
                    if response.status_code == 200:
                        result = f"{action.upper()} action performed successfully on  card ending with{last_four_digits}"
                        print(result)
                        return (True, result)
                    else:
                        result = f"{action.upper()} action failed due to {response.status_code}"
                        print(result)
                        return (False, result)
                else:
                    result = f"Card ending with {last_four_digits} not found."
                    print(result)
                    return (False, result)
            else:
                result = f"Card ending with {last_four_digits} not found"
                print(result)
                return (False, result)
        except Exception as e:
            result = f"Error in getting performing card action, {str(e)}"
            print(result)
            return (False, result)

    def get_account(self, account_id: str):
        print ("Getting account for ", account_id)
        try:
            url = f"https://api-frontend.wallester.com/v1/accounts/{account_id}"
            encoded = self.get_encoded()
            headers = self.headers.copy()
            headers["Authorization"] = "Bearer " + encoded
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                return (True, result)
            else:
                result = f"Account with  id {account_id} not found"
                print(result)
                return (False, result)
        except Exception as e:
            result = f"Error in getting account, {str(e)}"
            print(result)
            return (False, result)


    def transfer_amount(self, source_account_id: str, destination_account_id: str, amount: str, description: str):
        print ("Doing trasaction with details, ", source_account_id, destination_account_id, amount, description)
        # return (False, "Transaction Failed")
        # return (True, "Transaction Successfull")
        try:
            url = "https://api-frontend.wallester.com/v1/payments/account-transfer"
            if len(description) > 256:
                description = description[0:256]
            encoded = self.get_encoded()
            headers = self.headers.copy()
            headers["Authorization"] = "Bearer " + encoded
            payload = {
                "from_account_id": source_account_id,
                "to_account_id":  destination_account_id,
                "amount": float(amount),
                "description": description,
            }
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201 or response.status_code == 200:
                result = "Amount transfer successfully"
                return (True, result)
            else:
                result = f"Amount transfer failed due to {response.status_code}"
                print(result)
                return (False, result)
        except Exception as e:
            result = f"Error in processing transfer, {str(e)}"
            print(result)
            return (False, result)

    def get_account_statement(self, account_id):
        try:
            count = 1000
            offset = 0
            url = f"https://api-frontend.wallester.com/v1/accounts/{account_id}/statement"
            encoded = self.get_encoded()
            params = {
                "from_record": offset,
                "records_count": count,
                "include_transactions": False,
                "include_fees": True,
                "include_authorizations": True,
                "include_account_adjustments": True
            }
            headers = self.headers.copy()
            headers["Authorization"] = "Bearer " + encoded
            response = requests.get(url, headers=headers, params=params)
            records = {"records": []}
            if response.status_code == 200:
                data = response.json()
                records["records"] = data["records"]
                total_number = data["total_records_number"]
                last_fetched = offset + count
                api_calls_count = 1
                if total_number > last_fetched:
                    # only fetch last 3000 transactions to save time delay
                    while total_number > last_fetched and api_calls_count < 3:
                        api_calls_count = api_calls_count + 1
                        offset = last_fetched
                        encoded = self.get_encoded()
                        headers["Authorization"] = "Bearer " + encoded
                        params = {
                            "from_record": offset,
                            "records_count": count,
                            "include_transactions": False,
                            "include_fees": True,
                            "include_authorizations": True,
                            "include_account_adjustments": True
                        }
                        response = requests.get(
                            url, headers=headers, params=params)
                        if response.status_code == 200:
                            data_new = response.json()
                            records["records"] = [
                                *records["records"], *data_new["records"]]
                            last_fetched = last_fetched + count
                        else:
                            result = f"Get account transaction failed for {account_id} with status code, {response.status_code}"
                            return (False, result)

                with open("original.json", "w") as fh:
                    json.dump(records, fh, indent=4)
                updated = combine_fees((True, records))
                updated = sort_by_date(updated)
                return (updated)
            else:
                result = f"Get main account transaction failed for {account_id} with status code, {response.status_code}"
                return (False, result)
        except Exception as e:
            result = f"Error in getting account statement, {str(e)}"
            print(result)
            return (False, result)



def main():
    wallet_object = InterfaceWallet()
    # wallet_object.get_card_transactions("0845")
    # wallet_object.get_account(wallet_object.main_account_id)
    statement = wallet_object.get_account_statement("22b3ae0e-94c6-4d40-9554-c9ad4939bcfc")
    # print(len(statement[1]["records"]))
    # updated = combine_fees(statement)
    # updated = sort_by_date(updated)
    # with open("original.json", "w") as fh:
    #     json.dump(statement[1], fh, indent=4)
    # pprint(statement)
    with open("updated.json", "w") as fh:
        json.dump(statement[1], fh, indent=4)


if __name__ == "__main__":
    main()
