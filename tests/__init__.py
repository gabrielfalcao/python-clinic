# -*- coding: utf-8 -*-

import sure  # noqa
import click


def ignore(func):
    func.__test__ = False
    click.echo(" ... ".join([
        click.style(func.__doc__ or func.__name__, fg='yellow'),
        click.style('ignored', fg='cyan')
    ]))

    return func
