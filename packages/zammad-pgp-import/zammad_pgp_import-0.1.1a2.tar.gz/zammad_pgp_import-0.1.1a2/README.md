# Zammad PGP import webhook

### TLDR:
This is a Zammad webhook that gets triggered for each new incoming ticket. It automatically imports PGP keys attached to the ticket or found on a keyserver.

### The problem it solves
Zammad supports PGP encryption. The current workflow of importing PGP keys is suboptimal. Agents need special admin privileges to import PGP keys. This webhook automatically imports PGP keys when some checks are completed.

### How does it work?
1) Zammad gets a new ticket
2) It sends you a webhook
3) This projects runs the backend of the webhook. There are two supported scenarios:
    - The email/ticket has a PGP key attached. If sender's email matches with the one of the PGP key => use Zammad API to import PGP key
    - If the email is PGP-encrypted: Use a keyserver to find a valid PGP

### How to use it?
It's based on python and poetry.

```
poetry install

```


### Configuration




https://docs.zammad.org/en/latest/api/intro.html

