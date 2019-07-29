import click
import yaml
import yamlordereddictloader
import os
from datetime import datetime, timedelta


def echo(msg):
    """Just a wrapper to enable overloading and mocking"""
    click.echo(msg)


def echo_success(msg):
    echo(click.style(msg, fg='green'))


def echo_error(msg):
    echo(click.style(msg, fg='red'))


def echo_skip(msg):
    echo(click.style(msg, fg='cyan'))


def update_yaml(file_name, content):
    """This function is used to update the yaml file"""
    if file_name and content is not None:
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                yaml_dict = yaml.load(f) or {}
        else:
            yaml_dict = {}
        yaml_dict.update(content)
        with open(file_name, 'w') as f:
            yaml.dump(yaml_dict, f)
    else:
        echo_error("Failed to Set Configs !")


def get_yaml_data(file_name):
    with open(file_name) as f:
        yaml_data = yaml.load(f, Loader=yamlordereddictloader.Loader)
        return yaml_data


def configure_interval(interval):
    until = " --until {}".format(datetime.today().strftime('%Y-%m-%d'))
    since = ""
    today = datetime.today()
    if interval == 'week':
        week_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        since = " --since {}".format(week_date)
    else:
        week_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        since = " --since {}".format(week_date)
    return "{}{}".format(since, until)

