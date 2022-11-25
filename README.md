Usage:
- Create a user with the Admin role
- In this new user create a new application under the Development tab with `write:statuses` and `admin:read:accounts` access.
- Keep note of the application name you used - this is your client_id for the config file later
- Create a virtual env and install packages using [poetry](https://python-poetry.org/) install
- Copy the example `.toml` config file to `config.toml` (or specify another path with `--config` and modify for your purposes
- For the first execution you have to supply `--username` and `--password` so that a client credential can be created and saved
- *THIS WILL WELCOME ALL USERS ON YOUR SERVER WHEN IT STARTS FRESH* - this will hopefully be corrected in an update soon
