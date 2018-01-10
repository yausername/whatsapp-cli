import click
from click import BadParameter

from feed import PBFeeder
from curses_ui import CursesUI

feeder = None

@click.group(invoke_without_command=True)
@click.option('--token', help='Pushbullet API token', required=True)
@click.pass_context
def cli(ctx, token):
    global feeder
    ctx.obj['token'] = token
    feeder = PBFeeder(token)
    if ctx.invoked_subcommand is None:
        ui = CursesUI(feeder)
        ui.start()

@cli.command()
@click.option('-u', 'user', help='Name of the person/group or 12 digit mobile number. Partial names are allowed', required=True)
@click.option('-m', 'message',  help='Message to be sent', required=True)
@click.pass_context
def send(ctx, user, message):
    """Send message to a person/group"""
    try:
        feeder.post(user, message)
    except ValueError as err:
        raise BadParameter('0 or more than 1 matches for user', ctx)

@cli.command()
@click.option('-u', 'user', help='Name of the person/group. Partial names are allowed', default='all')
@click.pass_context
def read(ctx, user = 'all'):
    """Read messages from a person/group"""
    if user != 'all':
        try:
            res_feed = feeder.get(user)
        except ValueError as err:
            raise BadParameter('0 or more than 1 matches for user', ctx)
    else:
        res_feed = feeder.get()
    for line in res_feed:
        click.echo(line)

@cli.command()
@click.option('-u', 'name', help='Name of the person/group as it appears in your contacts', required=True)
@click.option('-m', 'mobile',  help='12 digit mobile number', required=True)
@click.pass_context
def add(ctx, name, mobile):
    """Add a contact"""
    if mobile.isnumeric() and len(mobile) == 12 and name:  
        feeder.add_user(mobile, name)
    else:
        raise BadParameter('Invalid mobile number or name. Use --help for help', ctx)


@cli.command()
@click.pass_context
def users(ctx):
    """List all contacts"""
    my_list = feeder.users()
    for name in my_list:
        click.echo(name)
