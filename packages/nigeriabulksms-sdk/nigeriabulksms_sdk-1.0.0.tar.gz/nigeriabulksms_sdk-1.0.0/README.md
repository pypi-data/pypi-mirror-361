# NigeriaBulkSMS Python SDK

A production-grade Python SDK for the [NigeriaBulkSMS.com](https://nigeriabulksms.com/) API. This SDK provides a simple, robust, and type-safe way to integrate bulk SMS, voice messaging, and data fetching functionalities into your Python applications.

## Features

*   🚀 **Easy to use** - Simple and intuitive API
*   🛡️ **Robust error handling** - Comprehensive error types and validation
*   📱 **SMS & Voice** - Support for text messages, voice calls, and TTS
*   📊 **Data fetching** - Access to account balance, history, and more

## Installation

Install the package using pip:

```bash
pip install nigeriabulksms-sdk
```

## Basic Usage

First, import the `NigeriaBulkSMSClient` and initialize it with your username and password.

```python
from nigeriabulksms_sdk import NigeriaBulkSMSClient
from nigeriabulksms_sdk.exceptions import NigeriaBulkSMSException

# Replace with your actual API credentials
USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

client = NigeriaBulkSMSClient(USERNAME, PASSWORD)

print("Testing NigeriaBulkSMS SDK...\n")

try:
    # Send an SMS
    print("Attempting to send SMS...")
    sms_response = client.sms.send(
        message="Hello from Python SDK test!",
        sender="TestSender",
        mobiles=["2348030000000"]
    )
    print(f"SMS Send Response: {sms_response}\n")

except NigeriaBulkSMSException as e:
    print(f"Caught NigeriaBulkSMSException for SMS: {e.message} (Code: {e.code})\n")
except Exception as e:
    print(f"Caught unexpected Exception for SMS: {e}\n")

try:
    # Get account balance
    print("Attempting to get balance...")
    balance_response = client.data.get_balance()
    print(f"Balance Response: {balance_response}\n")

except NigeriaBulkSMSException as e:
    print(f"Caught NigeriaBulkSMSException for Balance: {e.message} (Code: {e.code})\n")
except Exception as e:
    print(f"Caught unexpected Exception for Balance: {e}\n")

try:
    # Test TTS call
    print("Attempting to send TTS call...")
    tts_response = client.call.send_tts(
        message="This is a test text to speech message.",
        sender="2348030000000", # Use a mobile number as sender for TTS
        mobiles=["2348030000000"]
    )
    print(f"TTS Call Response: {tts_response}\n")

except NigeriaBulkSMSException as e:
    print(f"Caught NigeriaBulkSMSException for TTS: {e.message} (Code: {e.code})\n")
except Exception as e:
    print(f"Caught unexpected Exception for TTS: {e}\n")
```

## API Reference

### `NigeriaBulkSMSClient(username, password, base_url=None)`

The main client class to interact with the NigeriaBulkSMS API.

*   `username` (str): Your NigeriaBulkSMS username.
*   `password` (str): Your NigeriaBulkSMS password.
*   `base_url` (str, optional): The base URL for the API. Defaults to `https://portal.nigeriabulksms.com/api/`.

### SMS Service (`client.sms`)

#### `send(message, sender, mobiles)`

Sends a text message to one or more mobile numbers.

*   `message` (str): The content of the SMS message.
*   `sender` (str): The sender ID (max 11 alphanumeric characters).
*   `mobiles` (str or list): A single mobile number string or a list of mobile number strings. Numbers should be in international format (e.g., `2348030000000`).

### Call Service (`client.call`)

#### `send_tts(message, sender, mobiles)`

Sends a Text-to-Speech (TTS) call to one or more mobile numbers.

*   `message` (str): The text to be converted to speech.
*   `sender` (str): The sender ID.
*   `mobiles` (str or list): A single mobile number string or a list of mobile number strings.

#### `send_audio(audio_reference, sender, mobiles)`

Sends a pre-recorded audio call to one or more mobile numbers using an audio reference.

*   `audio_reference` (str): The reference ID of the uploaded audio file.
*   `sender` (str): The sender ID.
*   `mobiles` (str or list): A single mobile number string or a list of mobile number strings.

### Audio Service (`client.audio`)

#### `upload(url)`

Uploads an audio file from a given URL to the NigeriaBulkSMS platform.

*   `url` (str): The URL of the audio file (e.g., `https://example.com/audio.mp3`).

### Data Service (`client.data`)

#### `get_balance()`

Retrieves the current account balance.

#### `get_profile()`

Retrieves the customer profile information.

#### `get_contacts()`

Retrieves the list of contacts.

#### `get_numbers()`

Retrieves the list of saved numbers.

#### `get_groups()`

Retrieves the list of groups.

#### `get_audios()`

Retrieves the list of saved audio files.

#### `get_history()`

Retrieves the message history.

#### `get_scheduled()`

Retrieves the list of scheduled messages.

#### `get_reports()`

Retrieves the delivery reports.

#### `get_payments()`

Retrieves the payment history.

## Error Handling

The SDK raises `NigeriaBulkSMSException` for API-specific errors. You should wrap your API calls in `try-except` blocks to handle these exceptions gracefully.

```python
from nigeriabulksms_sdk import NigeriaBulkSMSClient
from nigeriabulksms_sdk.exceptions import NigeriaBulkSMSException

client = NigeriaBulkSMSClient("YOUR_USERNAME", "YOUR_PASSWORD")

try:
    response = client.sms.send("Test message", "TestApp", ["2348000000000"])
    print(response)
except NigeriaBulkSMSException as e:
    print(f"API Error: {e.message} (Code: {e.code})")
except Exception as e:
    print(f"General Error: {e}")
```

Common error codes are:

*   `100`: Incomplete request parameters
*   `101`: Request denied
*   `110`: Login status failed
*   `111`: Login status denied
*   `150`: Insufficient funds
*   `191`: Internal error

For a full list of error codes, refer to the [official NigeriaBulkSMS API documentation](https://nigeriabulksms.com/sms-gateway-api-in-nigeria/).

## Contributing

Feel free to contribute to this SDK by submitting issues or pull requests on GitHub.

## License

This SDK is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).

---

**Author:** Timothy Dake
*   **LinkedIn:** [https://www.linkedin.com/in/timothy-dake-14801571/](https://www.linkedin.com/in/timothy-dake-14801571/)
*   **X (formerly Twitter):** [@timothydake](https://twitter.com/timothydake)
*   **Email:** [timdake4@gmail.com](mailto:timdake4@gmail.com)


