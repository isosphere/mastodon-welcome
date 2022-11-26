Usage:
- Create a user with the Admin role (I suggest using `tootctl` to do this)
- Use [poetry](https://python-poetry.org/) install to create a virtual env and install packages 
- Copy the example `.toml` config file to `config.toml` (or specify another path with `--config` and modify for your purposes
- Feel free to use emojiis in your messages! :star:
- For the first execution you must supply `--email` and `--password` so that a client credential can be created and saved
- You do not need to specify `--email` and `--password` after a succesful first run

If your first run fails for any reason, delete your `database.db` file. Having to create it is 
how we determine if we are doing our first run. If you don't delete it, the bot will welcome all users 
on the server on its first successful run.

Here's an example of it in action: https://oceanplayground.social/@welcome/109305611022115482
