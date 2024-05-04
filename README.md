# Crawler Discord Bot

## Environment Variables
To run the Discord bot and configure deployment settings, you need to set the following environment variables:

```env
DISCORD_BOT_TOKEN = "Nzk5Mjgx0NDc2NDU1OTYABS5g.2lmzlZv3vUaKPQi2wI"
DEPLOYMENT_ENV = "prod" # prod | beta
MONGODB_CONNECTION_URL = "mongodb connection url"
```

- `DISCORD_BOT_TOKEN`: Your Discord bot token.
- `DEPLOYMENT_ENV`: The environment where the bot will be deployed, should be either "beta" or "prod".
- `MONGODB_CONNECTION_URL`: Your MongoDB connection URL.



Additionally, you need to create two environment files: `.env.prod` and `.env.beta` under the `config` directory with the following variables:

```env
GUILD_IDS = 250892094615837590
ADMIN_IDS = 249790928704776560, 149890528604796669
```

- `GUILD_IDS`: Comma-separated list of Discord guild (server) IDs where the bot will operate.
- `ADMIN_IDS`: Comma-separated list of Discord user IDs who will have administrative access to the bot.

## Deployment
To deploy the bot, ensure you have set up the environment variables and configured the appropriate environment files (`config/.env.prod` or `config/.env.beta`). Then, follow these steps:

1. Install dependencies: `pip install -r requirements.txt`
2. Run the project: `python main.py`

## Usage
Once the bot is running and connected to Discord, you can interact with it using various commands. These commands can be customized based on your bot's functionality. Users with administrative access can manage the bot's settings and commands.

## Contributing
If you'd like to contribute to the bot's development, feel free to fork this repository, make your changes, and submit a pull request. Please ensure your code follows the project's coding standards and includes appropriate documentation for any new features or changes.

## License
This project is licensed under the [MIT License](LICENSE).
