# -*- coding: utf-8 -*-
import os
import click
from python_clinic import application
from python_clinic import conf


ansi = lambda *args, **kw: click.style(bold=True, *args, **kw)


BANNER = "\n".join([

    ansi('Loaded settings from: {}'.format(os.path.abspath(conf.determine_config_path())),
         fg='yellow'),

    ansi('Python Clinic v{}'.format(application.version),
         fg='green'),
])


def should_echo():
    return not os.getenv('__PYTHON_CLINIC_DEBUG_INIT')


def debug_init():
    os.environ['__PYTHON_CLINIC_DEBUG_INIT'] = '1'


def echo(*args, **kw):
    if should_echo():
        click.echo(*args, **kw)


@click.group()
def entrypoint():
    pass


@click.command(name='version')
def show_version():
    click.echo(BANNER)


@click.command(name='web')
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=3000)
@click.option('--debug', is_flag=True)
def run_webserver(host, port, debug):
    echo(' | '.join([BANNER, ansi('Web Server', fg='blue')]))
    if debug:
        debug_init()

    application.run(
        port=port,
        host=host,
        debug=debug,
    )


entrypoint.add_command(show_version)
entrypoint.add_command(run_webserver)


if __name__ == '__main__':
    entrypoint()
