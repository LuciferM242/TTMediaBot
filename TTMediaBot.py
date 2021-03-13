import click

from bot import Bot
import utils


@click.command()
@click.option("-c", help="config file", default="config.ini")
@click.option("--devices", is_flag=True)
def cli(c="config.ini", devices=False):
    if devices:
        utils.echo_devices()
    else:
        bot = Bot(c)
        bot.run()



if __name__ == "__main__":
    cli()
