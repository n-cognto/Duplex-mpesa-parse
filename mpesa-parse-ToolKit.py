import re
from datetime import datetime
from typing import Dict, Optional

class DualMPESAParser:
    def __init__(self):
        # Base confirmation patterns
        self.base_patterns = {
            'ENGLISH': r"(?P<transaction_id>[A-Z0-9]{10})\s+[Cc]onfirmed\.?\s*",
            'SWAHILI': r"(?P<transaction_id>[A-Z0-9]{10})\s+Imethibitishwa\.?\s*"
        }
        
        # Transaction patterns for English and Swahili
        self.transaction_patterns = {
            'ENGLISH': {
                # ...existing English patterns...
                'RECEIVED': r"You\shave\sreceived\sKsh(?P<received_amount>[\d,.]+)\sfrom\s(?P<sender_name>[^0-9]+?)(?:\s(?P<sender_phone>\d+))?",
                'PAID': r"Ksh(?P<paid_amount>[\d,.]+)\spaid\sto\s(?P<paid_to>[^.]+)",
                'SENT': r"Ksh(?P<sent_amount>[\d,.]+)\ssent\sto\s(?P<recipient>[^0-9]+?)(?:\sfor\saccount\s(?P<account_number>[^\s]+))?(?:\s(?P<recipient_phone>\d+))?",
                'MSHWARI': r"Ksh(?P<mshwari_amount>[\d,.]+)\stransferred\s(?P<mshwari_direction>(?:from|to))\sM-Shwari\saccount",
                'AIRTIME': r"You\sbought\sKsh(?P<airtime_amount>[\d,.]+)\sof\sairtime(?:\sfor\s(?P<airtime_phone>\d+))?",
                'WITHDRAW': r"(?:(?:on\s[^.]+?)?\s*Withdraw\s*Ksh(?P<withdraw_amount>[\d,.]+)\sfrom\s(?P<agent_details>[^.]+))",
                'BALANCE_CHECK': r"Your\saccount\sbalance\swas:\sM-PESA\sAccount\s:\sKsh(?P<balance_amount>[\d,.]+)"
            },
            'SWAHILI': {
                # ...existing Swahili patterns...
                'KUTUMA': (
                    r"Ksh(?P<kutuma_amount>[\d,.]+)\s"
                    r"imetumwa\skwa\s"
                    r"(?P<kutuma_recipient>[^0-9]+?)\s"
                    r"(?P<kutuma_phone>\d{10})\s"
                    r"(?:tarehe|siku)\s"
                    r"(?P<kutuma_date>\d{1,2}/\d{1,2}/\d{2})\s"
                    r"saa\s(?P<kutuma_time>\d{1,2}:\d{2}\s*[AP]M)"
                ),
                'KUPOKEA': (
                    r"Umepokea\sKsh(?P<kupokea_amount>[\d,.]+)\s"
                    r"kutoka\s"
                    r"(?P<kupokea_sender>[^0-9]+?)\s"
                    r"(?P<kupokea_phone>\d{10})\s"
                    r"mnamo\s"
                    r"(?P<kupokea_date>\d{1,2}/\d{1,2}/\d{2})\s"
                    r"saa\s(?P<kupokea_time>\d{1,2}:\d{2}\s*[AP]M)"
                ),
                'SALIO': (
                    r"Baki\syako\sni:\s"
                    r"Akaunti\sya\sM-PESA\s:\s"
                    r"Ksh(?P<salio_amount>[\d,.]+)\s"
                    r"(?:Tarehe|tarehe)\s"
                    r"(?P<salio_date>\d{1,2}/\d{1,2}/\d{2})\s"
                    r"saa\s(?P<salio_time>\d{1,2}:\d{2}\s*[AP]M)"
                ),
                'KULIPA_TILL': (
                    r"Umelipa\sKsh(?P<kulipa_amount>[\d,.]+)\s"
                    r"kwa\s(?P<kulipa_merchant>[^0-9]+?)\s"
                    r"(?P<kulipa_date>\d{1,2}/\d{1,2}/\d{2})\s"
                    r"(?P<kulipa_time>\d{1,2}:\d{2}\s*[AP]M)"
                ),
                'DATA': (
                    r"Ksh(?P<data_amount>[\d,.]+)\s"
                    r"zimetumwa\skwa\sSAFARICOM\sDATA\sBUNDLES"
                    r"(?:\skwa\sakaunti\sSAFARICOM\sDATA\sBUNDLES)?\s"
                    r"mnamo\s"
                    r"(?P<data_date>\d{1,2}/\d{1,2}/\d{2})\s"
                    r"saa\s(?P<data_time>\d{1,2}:\d{2}\s*[AP]M)"
                ),
                'MJAZO': (
                    r"Umenunua\sKsh(?P<mjazo_amount>[\d,.]+)\s"
                    r"ya\smjazo\s"
                    r"(?:siku|tarehe)\s"
                    r"(?P<mjazo_date>\d{1,2}/\d{1,2}/\d{2})\s"
                    r"saa\s(?P<mjazo_time>\d{1,2}:\d{2}\s*[AP]M)"
                ),
                'PAYBILL': (
                    r"Ksh(?P<paybill_amount>[\d,.]+)\s"
                    r"imetumwa\skwa\s(?P<paybill_name>[^k]+?)\s"
                    r"kwa\sakaunti\snambari\s(?P<paybill_account>\d+)"
                ),
                'KUPOKEA_BANK': (
                    r"Umepokea\sKsh(?P<kupokea_bank_amount>[\d,.]+)\s"
                    r"kutoka\s(?P<kupokea_bank_name>[^0-9]+?)\s"
                    r"(?P<kupokea_bank_account>\d+)\s"
                    r"mnamo\s"
                    r"(?P<kupokea_bank_date>\d{1,2}/\d{1,2}/\d{2})\s"
                    r"saa\s(?P<kupokea_bank_time>\d{1,2}:\d{2}\s*[AP]M)"
                ),
                'POCHI_LA_BIASHARA': (
                    r"Ksh(?P<pochi_amount>[\d,.]+)\s"
                    r"imetumwa\skwa\s"
                    r"(?P<pochi_recipient>[^0-9]+?)\s"
                    r"(?:tarehe|siku)\s"
                    r"(?P<pochi_date>\d{1,2}/\d{1,2}/\d{2})\s"
                    r"saa\s(?P<pochi_time>\d{1,2}:\d{2}\s*[AP]M)"
                )
            }
        }
        
        # Additional information patterns
        self.additional_patterns = {
            'mpesa_balance': r"Baki\s(?:yako|mpya)(?:\sya|\smpya\skatika|\skatika)\sM-PESA\sni\sKsh(?P<mpesa_balance>[\d,.]+)",
            'transaction_cost': r"Gharama\sya\s(?:kutuma|kununua|matumizi|kulipa)\sni\sKsh(?P<transaction_cost>[\d,.]+)",
            'daily_limit': r"Kiwango\scha\sPesa\sunachoweza\skutuma\skwa\ssiku\sni\s(?P<daily_limit>[\d,.]+)"
        }
        
        # Failed transaction patterns
        self.failed_patterns = {
            'ENGLISH': re.compile(
                r"Failed\.\s"
                r"(?:"
                r"(?:You\sdo\snot\shave\senough\smoney)|"
                r"(?:Insufficient\sfunds\sin\syour\sM-PESA\saccount)|"
                r"(?:You\shave\sinsufficient\sfunds)|"
                r"(?:Insufficient\sfunds\sin\syour\sM-PESA\saccount\sas\swell\sas\sFuliza\sM-PESA)|"
                r"(?:You\shave\sinsufficient\sfunds\sin\syour\sM-Shwari\saccount)|"
                r"(?:You\shave\sreached\syour\sFuliza\sM-PESA\slimit)|"
                r"(?:Your\sFuliza\sM-PESA\slimit\sis\snot\savailable\sat\sthis\stime)"
                r")"
            ),
            'SWAHILI': re.compile(
                r"(?:"
                r"Hakuna\spesa\sza\skutosha|"
                r"Imefeli|"
                r"Umekataa\skuidhinisha\samali|"
                r"Huduma\shi\shaipatikani"
                r")"
            )
        }
        
        # Compile patterns
        self.compile_patterns()

    def compile_patterns(self):
        """Compile all patterns into the main regex pattern"""
        self.compiled_patterns = {}
        for lang, base_pattern in self.base_patterns.items():
            transaction_part = '|'.join(
                f"(?P<{tx_type}>{pattern})"
                for tx_type, pattern in self.transaction_patterns[lang].items()
            )
            
            additional_part = ''.join(
                f"(?:.*?{pattern})?"
                for pattern in self.additional_patterns.values()
            )
            
            complete_pattern = (
                f"(?:{base_pattern})?"  # Made base pattern optional for failed transactions
                f"({transaction_part})"
                f"{additional_part}"
            )
            
            self.compiled_patterns[lang] = re.compile(complete_pattern, re.IGNORECASE | re.DOTALL)

    def clean_amount(self, amount_str: str) -> float:
        """Clean amount string and convert to float."""
        if not amount_str:
            return 0.0
        cleaned = amount_str.replace(',', '').replace(' ', '').strip().rstrip('.')
        return float(cleaned)

    def parse_message(self, message: str) -> Dict[str, any]:
        """Parse an M-PESA message and extract details."""
        if not isinstance(message, str):
            return {"error": "Message must be a string"}
        
        # Determine language
        lang = 'ENGLISH' if 'Confirmed' in message or 'confirmed' in message else 'SWAHILI'
        
        # Check for failed transaction
        failed_match = self.failed_patterns[lang].search(message)
        if failed_match:
            return {
                "status": "FAILED",
                "reason": failed_match.group(0),
                "original_message": message
            }
        
        # Match message against pattern
        match = self.compiled_patterns[lang].search(message)
        if not match:
            return {"error": "Message format not recognized"}
            
        result = {k: v for k, v in match.groupdict().items() if v is not None}
        
        # Clean up values
        for key in result:
            if isinstance(result[key], str):
                result[key] = result[key].strip()
        
        # Set transaction status
        result['status'] = 'SUCCESS'
        
        # Determine transaction type and clean amount
        for tx_type in self.transaction_patterns[lang].keys():
            if result.get(tx_type):
                result['transaction_type'] = tx_type
                amount_key = f"{tx_type.lower()}_amount"
                if amount_key in result:
                    result['amount'] = self.clean_amount(result[amount_key])
                    del result[amount_key]
                break
        
        # Clean numeric fields
        numeric_fields = {
            'mpesa_balance': 'mpesa_balance',
            'transaction_cost': 'transaction_cost',
            'daily_limit': 'daily_limit'
        }
        
        for eng_key, swa_key in numeric_fields.items():
            if eng_key in result:
                result[swa_key] = self.clean_amount(result[eng_key])
                del result[eng_key]
        
        # Parse date and time if present
        if 'date' in result and 'time' in result:
            try:
                datetime_str = f"{result['date']} {result['time']}"
                result['datetime'] = datetime.strptime(datetime_str, '%d/%m/%y %I:%M %p')
                del result['date']
                del result['time']
            except ValueError:
                pass
        
        return result

def test_parser():
    parser = DualMPESAParser()
    
    # Test messages
    test_messages = [
        # English messages
        "TA22OI958I Confirmed.Ksh50.00 transferred from M-Shwari account on 2/1/25 at 11:00 AM. M-Shwari balance is Ksh925.46 .M-PESA balance is Ksh359.50 .Transaction cost Ksh.0.00",
        "TA27OIFCSZ Confirmed.on 2/1/25 at 11:01 AMWithdraw Ksh300.00 from 343595 - Anzal Express Ltdlongonot farm along moi south lake Agg New M-PESA balance is Ksh30.50. Transaction cost, Ksh29.00. Amount you can transact within the day is 498,710.00. To move money from bank to M-PESA, dial *334#>Withdraw>From Bank to MPESA",
        "TA22OPE6TO confirmed.You bought Ksh10.00 of airtime for 0113169506 on 2/1/25 at 11:54 AM.New  balance is Ksh20.50. Transaction cost, Ksh0.00. Amount you can transact within the day is 498,700.00.You can now access M-PESA via *334#Failed. You do not have enough money in your M-PESA account to pay Ksh50.00 to Juddy Atieno Wandere. Your M-PESA balance is Ksh20.50.  Dial *334# to register for the M-PESA overdraw Services Fuliza.",
        
        # Swahili messages
        "TAD62EDKVQ Imethibitishwa Ksh1.00 imetumwa kwa John Doe 0769641937 tarehe 13/1/25 saa 5:44 PM. Baki yako ya M-PESA ni Ksh263.47. Gharama ya kutuma ni Ksh0.00.",
        "TAD72CZ6J3 Imethibitishwa. Baki yako ni: Akaunti ya M-PESA : Ksh263.47 Tarehe 13/1/25 saa 5:36 PM. Gharama ya matumizi ni Ksh0.00.",
        "TAF5BV0XRN Umenunua Ksh5.00 ya mjazo siku 15/1/25 saa 8:44 PM.Baki mpya ya M-PESA ni Ksh38.47.",
        "Hakuna pesa za kutosha katika akaunti yako ya M-PESA kuweza kutuma Ksh3,251.00."
    ]
    
    for message in test_messages:
        print("\nOriginal Message:", message)
        try:
            result = parser.parse_message(message)
            print("Parsed Result:")
            for key, value in result.items():
                print(f"{key}: {value}")
        except Exception as e:
            print(f"Error parsing message: {str(e)}")

if __name__ == "__main__":
    test_parser()

