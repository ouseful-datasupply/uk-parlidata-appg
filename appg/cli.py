import appg.webscrape as appg
import click
import sqlite3


@click.command()
@click.option('--dbname', default='appg_data.db',  help='SQLite database name')
def webscrape(dbname):
    click.echo('Using SQLite3 database: {}'.format(dbname))
    conn = sqlite3.connect(dbname)
    appg.scraper(conn=conn, exists='replace')