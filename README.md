# lottery-random

`lottery-random` is a true random lottery ticket generator with the help of the random.org API. It emails you true random numbers for the configured lottery ticket packs via SendGrid in the following format:

---

**True random lottery numbers for John Smith**

True random lottery numbers for John Smith

Lottery 5: (2–5–26–43–87)<br>
Lottery 6: (4–7–18–32–38–39), (1–2–13–27–37–40)<br>
EuroJackpot: (15–20–23–28–44 | 1–8)<br>

Timestamp: 2019/05/09 03:25:32 (UTC)

This email was sent you by Jane Smith (jane@smith.com) using https://github.com/luczsoma/lottery-random.

---

## Requirements

- Python >=3
- [pipenv](https://github.com/pypa/pipenv)
- An API key for the [random.org API](https://api.random.org)\*
- An API key for the [SendGrid](https://sendgrid.com) API

\*Please note that you are not allowed to use an API key with neither Developer nor Non-Profit API key licenses: visit https://api.random.org/pricing for details.

## Usage

Clone the repository:

```
git clone https://github.com/luczsoma/lottery-random.git
```

Install all dependencies:

```
pipenv sync
```

Clone the example configuration file into your config file:

```
cp config.example.json config.json
```

After filling the config file with your desired configuration, you are ready to go. Run the following command to send randomly filled lottery tickets to the given email addresses:

```
pipenv run python lottery-random.py
```

## Running lottery-random periodically

There are quite a few methods to run `lottery-random` periodically. E.g. if you have an always-on server anywhere on the internet you can add an entry to your user's crontab file. Enter:

```
crontab -e
```

Then enter the following:

```
0 0 * * 0 pipenv run python lottery-random.py
```

This will run lottery-random every Sunday at midnight (according to your server's time zone).

## Configuration options

You can see the JSON schema of the `config.json` file defined in `config.schema.json`. Your `config.json` file must comply with the provided schema.

### API key for the random.org API

Provide your random.org API key in the `random_org_api_key` field:

```
{
  // …
  "random_org_api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  // …
}
```

Please note that you are not allowed to use an API key with neither Developer nor Non-Profit API key licenses: visit https://api.random.org/pricing for details.

### API key for the SendGrid API

Provide your SendGrid API key in the `sendgrid_api_key` field:

```
{
  // …
  "sendgrid_api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  // …
}
```

### Email sender name and address

Provide the name and the email address of the email sender in the `email_from` field. Please note that the `email_from` attribute values will be visible in the email in the following form: "This email was sent you by {email_from.name} ({email_from.value}) using https://github.com/luczsoma/lottery-random.".

```
{
  // …
  "email_from": {
    "email": "yourserver@yourdomain.com",
    "name": "Your Name"
  },
  // …
}
```

**Don't send email from domains you don't control!** See: https://sendgrid.com/blog/dont-send-email-from-domains-you-dont-control/.

### Lottery game definitions

A lottery game definition is the description of a particular lottery game: it defines how a valid ticket looks like.

E.g. a EuroJackpot ticket consists of two sets of numbers:

- 5 numbers from the [1–50] interval,
- 2 numbers from the [1-10] interval.

This can be configured as follows:

```
{
  // …
  "lottery_game_definitions": [
    {
      "game_name": "EuroJackpot",
      "drawing_sets": [
        {
          "n": 5,
          "min": 1,
          "max": 50
        },
        {
          "n": 2,
          "min": 1,
          "max": 10
        }
      ]
    }
  ],
  // …
}
```

### Lottery ticket packs

A lottery ticket pack is a set of played lottery tickets sent to one or more email addresses. E.g. if you play 1 ticket of EuroJackpot and 1 ticket of Lottery 5, and your brother plays 1 ticket of Lottery 5 and 2 tickets of Lottery 6 each week, you define two separate lottery ticket packs, which will be sent to you and your brother separately:

```
{
  // …
  "lottery_ticket_packs": [
    {
      "email_to": [
        {
          "email": "yourname@yourdomain.com",
          "name": "Your Name"
        }
      ],
      "elements": [
        {
          "game_name": "Lottery 5",
          "number_of_tickets": 1
        },
        {
          "game_name": "Lottery 6",
          "number_of_tickets": 2
        },
        {
          "game_name": "EuroJackpot",
          "number_of_tickets": 1
        }
      ]
    },
    {
      "email_to": [
        {
          "email": "yourbrothersname@example.com",
          "name": "Your Brother's Name"
        }
      ],
      "elements": [
        {
          "game_name": "Lottery 5",
          "number_of_tickets": 2
        },
        {
          "game_name": "Lottery 6",
          "number_of_tickets": 1
        }
      ]
    }
  ],
  // …
}
```

You can send the same lottery ticket pack to multiple addresses with setting the configuration as follows. Please note that the `email_to.name` attribute will be visible in the email in the following form: "True random lottery numbers for {email_to.name}".

```
{
  // …
  "lottery_ticket_packs": [
    {
      "email_to": [
        {
          "email": "yourname@yourdomain.com",
          "name": "Your Name"
        },
        {
          "email": "yourbrothersname@example.com",
          "name": "Your Brother's Name"
        }
      ],
      "elements": [
        {
          "game_name": "Lottery 5",
          "number_of_tickets": 1
        },
        {
          "game_name": "Lottery 6",
          "number_of_tickets": 2
        },
        {
          "game_name": "EuroJackpot",
          "number_of_tickets": 1
        }
      ]
    }
  ],
  // …
}
```
