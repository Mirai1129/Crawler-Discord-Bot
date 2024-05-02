import threading
import os


def run_discord_bot():
    os.system('cd Bot && python bot.py')


def run_flask_app():
    os.system('cd Router && python router.py')


if __name__ == '__main__':
    run_discord_bot_process = threading.Thread(target=run_discord_bot)
    run_flask_app_process = threading.Thread(target=run_flask_app)
    run_discord_bot_process.start()
    run_flask_app_process.start()
    run_discord_bot_process.join()
    run_flask_app_process.join()
    print('Bot process terminated.')
