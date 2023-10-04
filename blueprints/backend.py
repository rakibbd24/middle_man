
from typing import Dict, Optional
from .interface import InterfaceWallet
from pprint import pprint
import math
import re

class Api:
    """
    Api class to manage the call the backend to get data
    """
    _api_base_url = "https://api.backend.com"

    def __init__(self):
        self.wallet = InterfaceWallet()
        self.max_transaction_per_message = 10

    def get_transactions(self, card_no: str, page_no: int) -> dict:
        """
        Returns the transactions
        :param card_no: str
        :param page_no: int
        :return: str
        """
        page_no = int(page_no)
        result = self.wallet.get_account(card_no)
        name = ""
        balance = ""
        if result[0]:
            data = result[1]
            currency_code = str(data["account"]["currency_code"])
            balance = str(data["account"]["available_amount"])
            balance = f'{balance} {currency_code}'
            name = str(data["account"]["name"])
        else:
            msg = "Error in getting account"
            return {"status": "error", "result": result[1]}
        api_data = self.wallet.get_account_statement(card_no)
        if api_data[0]:
            result = {}
            result["transactions"] = [] 
            data = api_data[1]
            transactions = data.get("records")
            total_pages_records = math.ceil(len(transactions) / 10)
            start = page_no * self.max_transaction_per_message
            end = start + self.max_transaction_per_message
            paged_transaction = transactions[start: end]
            page_no_show = page_no + 1
            result["name"] = name
            result["balance"] = balance
            result["page_number"] = page_no_show
            result["total_pages"] = total_pages_records
            result["total_count"] = len(transactions)
            msg_head = f"Name: {name},    Available Balance: {balance}\n\nPage number: {page_no_show},    Total Pages: {total_pages_records}\n\n"
            if paged_transaction:
                all_msgs = []
                
                for record in paged_transaction:
                    c_transaction = {
                    "date": "",
                    "merchant_name": "",
                    "amount": "",
                    "status": "",
                    "response_code": ""
                    }
                    amount = record["account_amount"]
                    if amount < 0:
                        amount = str(amount)
                    else:
                        amount = "+" + str(amount)
                    
                    c_transaction["date"] = record["date"]
                    c_transaction["merchant_name"] = re.sub('(?i)' + re.escape('novogad ltd'), 'Payzocard topup', record["merchant_name"])
                    c_transaction["amount"] = amount + " " + record["account_currency_code"]
                    c_transaction["status"] = record["status"]
                    # msg not used here in this api
                    msg = f'{record["date"]}, {record["merchant_name"]} {amount} {record["account_currency_code"]}, ' \
                        f'{record["status"]}'
                    if "response_code" in record:
                        msg = msg + f', Reason: {record["response_code"]}'
                        c_transaction["response_code"] = record["response_code"]
                    result["transactions"].append(c_transaction)
                    all_msgs.append(msg)
                msg = ("\n\n".join(all_msgs))
                msg  = msg_head + msg
                return {"status": "success", "result": result}
            else:
                msg = "No transaction for this page number"
                return {"status": "error", "result": msg}

        else:
            msg = "Error in getting account transactions"
            return {"status": "error", "result": msg}


    def get_balance(self, card_no: str) -> str:
        """
        Returns the balance of the user
        :return: str
        """
        result = self.wallet.get_account(self.wallet.main_account_id)
        if result[0]:
            data = result[1]
            amount = str(data["account"]["available_amount"])
            currency_code = str(data["account"]["currency_code"])
            balance = str(data["account"]["balance"])
            name = str(data["account"]["name"])
            # data = f"{name}\n\n.Your account balance is {balance} {currency_code}.\n\nAvailable amount {amount} {currency_code}."
            data = f"{amount} {currency_code}"

            if data is None:
                data = f"your balance: 0".capitalize()
            return {"status": "success", "result": data}

        else:
            msg = f"No account balance for given account"
            return {"status": "error", "result": msg}

    def do_transfer(self, source_account_id: str, destination_account_id: str, amount: str, description: str) -> str:
        """
        """
        result = self.wallet.transfer_amount(source_account_id, destination_account_id, amount, description)
        if not result[0]:
            msg = f"Unable to perform the transfer. Make sure the details are correct"
            return {"status": "error", "result": msg}
        else:
            msg = "Transfer successfull."
            return {"status": "success", "result": msg}



    def control_card(self, card_no: str, action: str) -> str:
        """
        calls the card control api
        :param card_no: str
        :param action: str
        :return: None
        """
        result = self.wallet.card_action(card_no, action)
        if not result[0]:
            msg = f"Unable to perform the action {action}".capitalize()
            return {"status": "error", "result": msg}
        else:
            msg = f"{action.title()} action performed".capitalize()
            return {"status": "success", "result": msg}

    def status_card(self, card_no: str) -> str:
        """
        calls the card control api
        :param card_no: str
        :return: str
        """
        card = self.wallet.get_card(card_no)
        if card[0]:
            if card[1]:
                card = card[1]
                status = card["status"]
                # msg = "Current cards stauts: " + status 
                msg = status 
                return {"status": "success", "result": msg}

        msg = "Unable to get the card status for this card."
        return {"status": "error", "result": msg}
