# Dual MPESA Parser

The `DualMPESAParser` is a Python class designed to parse M-PESA transaction messages in both English and Swahili. It extracts relevant details from the messages, such as transaction type, amount, sender/recipient information, and balance details.

## Features

- Supports parsing of M-PESA messages in both English and Swahili.
- Extracts transaction details such as transaction ID, amount, sender/recipient, date, time, and balance.
- Handles various transaction types including received, paid, sent, M-Shwari, airtime purchase, withdrawal, balance check, and more.
- Identifies and handles failed transactions.

## Installation

Ensure you have Python 3 installed. Clone the repository and navigate to the directory containing `dual_purpose.py`.

```bash
git clone <repository-url>
cd <repository-directory>
```

## Usage

You can use the `DualMPESAParser` class in your Python scripts to parse M-PESA messages. Below is an example of how to use the parser:

```python
from dual_purpose import DualMPESAParser

parser = DualMPESAParser()

message = "TA22OI958I Confirmed.Ksh50.00 transferred from M-Shwari account on 2/1/25 at 11:00 AM. M-Shwari balance is Ksh925.46 .M-PESA balance is Ksh359.50 .Transaction cost Ksh.0.00"
result = parser.parse_message(message)

print(result)
```

## Example Messages

Here are some example messages and their parsed results:

### English Messages

1. **Message:**
   ```
   TA22OI958I Confirmed.Ksh50.00 transferred from M-Shwari account on 2/1/25 at 11:00 AM. M-Shwari balance is Ksh925.46 .M-PESA balance is Ksh359.50 .Transaction cost Ksh.0.00
   ```

   **Parsed Result:**
   ```json
   {
       "transaction_id": "TA22OI958I",
       "mshwari_amount": "50.00",
       "mshwari_direction": "from",
       "datetime": "2025-01-02 11:00:00",
       "mpesa_balance": 359.50,
       "transaction_cost": 0.0,
       "status": "SUCCESS",
       "transaction_type": "MSHWARI",
       "amount": 50.0
   }
   ```

2. **Message:**
   ```
   TA27OIFCSZ Confirmed.on 2/1/25 at 11:01 AMWithdraw Ksh300.00 from 343595 - Anzal Express Ltdlongonot farm along moi south lake Agg New M-PESA balance is Ksh30.50. Transaction cost, Ksh29.00. Amount you can transact within the day is 498,710.00.
   ```

   **Parsed Result:**
   ```json
   {
       "transaction_id": "TA27OIFCSZ",
       "withdraw_amount": "300.00",
       "agent_details": "343595 - Anzal Express Ltdlongonot farm along moi south lake Agg",
       "datetime": "2025-01-02 11:01:00",
       "mpesa_balance": 30.50,
       "transaction_cost": 29.0,
       "daily_limit": 498710.0,
       "status": "SUCCESS",
       "transaction_type": "WITHDRAW",
       "amount": 300.0
   }
   ```

### Swahili Messages

1. **Message:**
   ```
   TAD62EDKVQ Imethibitishwa Ksh1.00 imetumwa kwa Eliud Otieno 0792469173 tarehe 13/1/25 saa 5:44 PM. Baki yako ya M-PESA ni Ksh263.47. Gharama ya kutuma ni Ksh0.00.
   ```

   **Parsed Result:**
   ```json
   {
       "transaction_id": "TAD62EDKVQ",
       "kutuma_amount": "1.00",
       "kutuma_recipient": "Eliud Otieno",
       "kutuma_phone": "0792469173",
       "datetime": "2025-01-13 17:44:00",
       "mpesa_balance": 263.47,
       "transaction_cost": 0.0,
       "status": "SUCCESS",
       "transaction_type": "KUTUMA",
       "amount": 1.0
   }
   ```

2. **Message:**
   ```
   TAD72CZ6J3 Imethibitishwa. Baki yako ni: Akaunti ya M-PESA : Ksh263.47 Tarehe 13/1/25 saa 5:36 PM. Gharama ya matumizi ni Ksh0.00.
   ```

   **Parsed Result:**
   ```json
   {
       "transaction_id": "TAD72CZ6J3",
       "salio_amount": "263.47",
       "datetime": "2025-01-13 17:36:00",
       "transaction_cost": 0.0,
       "status": "SUCCESS",
       "transaction_type": "SALIO",
       "amount": 263.47
   }
   ```

## Running Tests

The script includes a `test_parser` function that demonstrates how to parse various M-PESA messages. You can run this function to see the parser in action:

```bash
python dual_purpose.py
```

## License

This project is licensed under the MIT License.
