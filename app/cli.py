import click
from flask.cli import with_appcontext
from app import db
from app.models.user import User

@click.command('dump-db')
@with_appcontext
def dump_db():
    print("-- Users table dump:")
    users = User.query.all()
    for user in users:
        print(f"INSERT INTO user (id, username, email, password_hash) VALUES ({user.id}, '{user.username}', '{user.email}', '{user.password_hash}');")

def init_app(app):
    app.cli.add_command(dump_db) 