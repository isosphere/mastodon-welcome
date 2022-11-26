Usage:
- Create a user with the Admin role
- Create a virtual env and install packages using [poetry](https://python-poetry.org/) install
- Copy the example `.toml` config file to `config.toml` (or specify another path with `--config` and modify for your purposes
- For the first execution you have to supply `--email` and `--password` so that a client credential can be created and saved
- You do not need to specify `--email` and `--password` after a succesful first run

If your first run fails for any reason, delete your `database.db` file. Having to create it is 
how we determine if we are doing our first run. If you don't delete it, the bot will welcome all users 
on the server on its first successful run.