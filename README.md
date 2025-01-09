# lottery-random

`lottery-random` is a true random lottery ticket generator with the help of the random.org API. It emails you true random numbers for the configured lottery ticket packs via Azure Communication Services in the following format:

---

**Lottery numbers for John Smith**

Lottery numbers for John Smith

Lottery 5: [2, 5, 26, 43, 87], [3, 27, 42, 54, 87]<br>
Lottery 6: [4, 7, 18, 32, 38, 39], [1, 2, 13, 27, 37, 40], [9, 17, 23, 30, 41, 43], [4, 8, 9, 12, 28, 37]<br>
EuroJackpot: [15, 20, 23, 28, 44 | 1, 8], [2, 3, 24, 39, 41 | 2, 8], [3, 4, 8, 9, 11 | 5, 9]<br>

Timestamp: 2019/05/09 03:25:32 (UTC)

This email was sent you by Jane Smith (jane@smith.com) using https://github.com/luczsoma/lottery-random.

---

## Requirements

- Python >=3
- An API key for the [random.org API](https://api.random.org)\*
- An [Azure Communication Services](https://learn.microsoft.com/en-us/azure/communication-services/) instance with an endpoint and an API key

\*Please note that you are not allowed to use an API key with neither Developer nor Non-Profit API key licenses: visit https://api.random.org/pricing for details.

## Usage

Clone the repository:

```sh
git clone https://github.com/luczsoma/lottery-random.git
```

Create a virtual environment and activate it:

```sh
python -m venv venv
. ./venv/bin/activate
```

Install all dependencies:

```sh
pip install -r requirements.txt
```

Clone the example configuration file into your config file:

```sh
cp config.example.json config.json
```

Fill the config file with your desired configuration, and you are ready to go. Run the following command to send randomly filled lottery tickets to the given email addresses:

```sh
python src/lottery-random.py
```

## Running lottery-random periodically

There are quite a few methods to run `lottery-random` periodically. E.g., if you have an always-on server anywhere on the internet you can add an entry to your user's crontab file. Enter:

```sh
crontab -e
```

Then enter the following:

```
0 0 * * 0 python lottery-random.py
```

This will run lottery-random every Sunday at midnight (according to your server's time zone).

## Configuration options

You can see the JSON schema of the `config.json` file defined in `config.schema.json`. Your `config.json` file must comply with the provided schema.

### API key for the random.org API

Provide your random.org API key in the `random_org_api_key` field:

```json
{
  // …
  "random_org_api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  // …
}
```

Please note that you are not allowed to use an API key with neither Developer nor Non-Profit API key licenses: visit https://api.random.org/pricing for details.

### Azure Communication Services

Provide your Azure Communication Services endpoint and API key in the `azure_email_endpoint` and `azure_email_key` fields, respectively:

```json
{
  // …
  "azure_email_endpoint": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "azure_email_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  // …
}
```

### Email sender name and address

Provide the email address and name configured in Azure Communicationn Services in the `sender_email` and `sender_name` fields, respectively. Please note that these values will be visible in the email in the following form: "This email was sent you by {sender_name} ({sender_email}) using https://github.com/luczsoma/lottery-random.".

```json
{
  // …
  "sender_email": "yourserver@yourdomain.com",
  "sender_name": "Your Name"
  // …
}
```

### Lottery game definitions

A lottery game definition is the description of a particular lottery game: it defines how a valid ticket looks like.

E.g., a EuroJackpot ticket consists of two sets of numbers:

- 5 numbers from the [1–50] interval,
- 2 numbers from the [1–12] interval.

This can be configured as follows:

```json
{
  // …
  "games": [
    {
      "name": "EuroJackpot",
      "fields": [
        {
          "n": 5,
          "min": 1,
          "max": 50
        },
        {
          "n": 2,
          "min": 1,
          "max": 12
        }
      ]
    }
  ]
  // …
}
```

### Lottery ticket packs

A lottery ticket pack is a set of played lottery tickets sent to one or more email addresses. E.g., if you play one ticket of EuroJackpot and one ticket of Lottery 5, and your friend plays one ticket of Lottery 5 and two tickets of Lottery 6 each week, you define two separate lottery ticket packs, which will be sent to you and your friend separately. You can also configure permanent tickets to be played regularly. Permanent tickets must conform to the game definition, and cannot contain duplicate numbers.

Lottery ticket packs can be configured as follows:

```json
{
  // …
  "lottery_ticket_packs": [
    {
      "recipients": [
        {
          "email": "yourname@yourdomain.com",
          "name": "Your Name"
        }
      ],
      "elements": [
        {
          "game": "Lottery 5",
          "number_of_random_tickets": 1,
          "permanent_tickets": [[[3, 27, 42, 54, 87]]]
        },
        {
          "game": "Lottery 6",
          "number_of_random_tickets": 2,
          "permanent_tickets": [
            [[9, 17, 23, 30, 41, 43]],
            [[4, 8, 9, 12, 28, 37]]
          ]
        },
        {
          "game": "EuroJackpot",
          "number_of_random_tickets": 1,
          "permanent_tickets": [
            [
              [2, 5, 24, 39, 41],
              [2, 8]
            ],
            [
              [3, 4, 8, 9, 11],
              [5, 9]
            ]
          ]
        }
      ]
    },
    {
      "recipients": [
        {
          "email": "yourfriendsname@yourfriendsdomain.com",
          "name": "Your Friend’s Name"
        }
      ],
      "elements": [
        {
          "game": "Lottery 5",
          "number_of_random_tickets": 2,
          "permanent_tickets": []
        },
        {
          "game": "Lottery 6",
          "number_of_random_tickets": 1,
          "permanent_tickets": []
        }
      ]
    }
  ]
  // …
}
```

You can send the same lottery ticket pack to multiple recipients with setting the configuration as follows. Please note that the `name` attribute of a recipient will be visible in the email in the following form: "True random lottery numbers for {name}".

```json
{
  // …
  "lottery_ticket_packs": [
    {
      "recipients": [
        {
          "email": "yourname@yourdomain.com",
          "name": "Your Name"
        },
        {
          "email": "yourfriendsname@yourfriendsdomain.com",
          "name": "Your Friend’s Name"
        }
      ],
      "elements": [
        {
          "game": "Lottery 5",
          "number_of_random_tickets": 1,
          "permanent_tickets": [[[3, 27, 42, 54, 87]]]
        },
        {
          "game": "Lottery 6",
          "number_of_random_tickets": 2,
          "permanent_tickets": [
            [[9, 17, 23, 30, 41, 43]],
            [[4, 8, 9, 12, 28, 37]]
          ]
        },
        {
          "game": "EuroJackpot",
          "number_of_random_tickets": 1,
          "permanent_tickets": [
            [
              [2, 5, 24, 39, 41],
              [2, 8]
            ],
            [
              [3, 4, 8, 9, 11],
              [5, 9]
            ]
          ]
        }
      ]
    }
  ]
  // …
}
```
