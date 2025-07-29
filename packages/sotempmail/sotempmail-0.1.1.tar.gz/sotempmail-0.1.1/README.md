# sotempmail

A simple Python async wrapper for the [tempmail.so](https://rapidapi.com/tempmailso-tempmailso-default/api/tempmail-so) API.

## Features
- Create and delete temporary inboxes
- List available domains
- List inboxes and emails
- Retrieve and delete emails

## Requirements
- Python 3.9+
- [aiohttp](https://docs.aiohttp.org/) (installed automatically)

## Installation

Install from PyPI:

```bash
pip install sotempmail
```

Or with Poetry:

```bash
poetry add sotempmail
```

Or with Pipenv:

```bash
pipenv install sotempmail
```

## Usage

You need a RapidAPI key and a Bearer token from tempmail.so. See [tempmail.so docs](https://rapidapi.com/tempmailso-tempmailso-default/api/tempmail-so) for details.

```python
import asyncio
from sotempmail import TempMailSo

async def main():
    api_key = "<YOUR_RAPIDAPI_KEY>"
    bearer = "<YOUR_BEARER_TOKEN>"
    tm = TempMailSo(api_key, bearer)

    # List available domains
    domains = await tm.list_domains()
    print("Domains:", domains)

    # Create an inbox
    inbox_id = await tm.create_inbox(name="myinbox", domain=domains[0], lifespan=60)
    print("Created inbox:", inbox_id)

    # List inboxes
    inboxes = await tm.list_inboxes()
    print("Inboxes:", inboxes)

    # List emails in inbox
    emails = await tm.list_emails(inbox_id)
    print("Emails:", emails)

    # If emails exist, retrieve the first one
    if emails:
        email_id = emails[0]["_id"]
        email = await tm.retrieve_email(inbox_id, email_id)
        print("Email:", email)

        # Delete the email
        await tm.delete_email(inbox_id, email_id)
        print("Email deleted.")

    # Delete the inbox
    await tm.delete_inbox(inbox_id)
    print("Inbox deleted.")

asyncio.run(main())
```

## Links
- [PyPI](https://pypi.org/project/sotempmail/)
- [GitHub](https://github.com/jbsanf/sotempmail)

## License
MIT
