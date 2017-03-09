import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)

app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'gatoTemp.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('GATOTEMP_SETTINGS', silent=True)


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/fake/<fecha>/<temp1>/<temp2>/<temp3>')
def fake_entry(fecha, temp1, temp2, temp3):
    db = get_db()
    sql1 = 'INSERT INTO tempLog (datetime, temperature_panel, temperature_wea2, temperature_wea3) VALUES ('
    sql2 = ')'
    sql = sql1+'"'+str(fecha)+'","'+str(temp1)+'","'+str(temp2)+'","'+str(temp3)+'"'+sql2
    print sql
    cur = db.execute(sql)
    db.commit()
    return "asd"


@app.route('/')
def show_entries():
    return render_template('main.html')


@app.route('/datos/<panel_id>/<year>/<month>/<day>')
def data_daily(panel_id, year, month, day):
    db = get_db()
    date_1 = "Datetime('%s-%s-%s 00:00:00')" % (year, tabzeroes(month), tabzeroes(day))
    date_2 = "Datetime('%s-%s-%s 23:59:59')" % (year, tabzeroes(month), tabzeroes(day))
    sql = "SELECT panel_id, date_log, temperature FROM tempLog " \
          "WHERE date_log >= %s AND date_log <= %s" % (date_1, date_2)
    res = db.execute(sql)
    tsv = 'id\tdate\ttemperature\n'
    for entry in res:
        tsv += str(entry[0]) + '\t' + str(entry[1]) + '\t' + str(entry[2]) + '\n'
    f = open("/home/tw/PycharmProjects/gatoTemp/static/auxdata.tsv", "w")
    f.write(tsv)
    f.close()
    return app.send_static_file('auxdata.tsv')


def tabzeroes(number):
    if len(number) == 1:
        return '0'+str(number)
    return str(number)


@app.route('/datos/<panel_id>/rango/<year_1>/<month_1>/<day_1>/<year_2>/<month_2>/<day_2>')
def data_time_range(panel_id, year_1, month_1, day_1, year_2, month_2, day_2):
    date_1 = "Datetime('%s-%s-%s 00:00:00')" % (year_1, tabzeroes(month_1), tabzeroes(day_1))
    date_2 = "Datetime('%s-%s-%s 23:59:59')" % (year_2, tabzeroes(month_2), tabzeroes(day_2))
    sql = "SELECT panel_id, date_log, temperature FROM tempLog " \
          "WHERE date_log >= %s AND date_log <= %s" % (date_1, date_2)
    db = get_db()
    res = db.execute(sql)
    tsv = 'id\tdate\ttemperature\n'
    for entry in res:
        tsv += str(entry[0]) + '\t' + str(entry[1]) + '\t' + str(entry[2]) + '\n'

    f = open("/home/tw/PycharmProjects/gatoTemp/static/auxdata.tsv", "w")
    f.write(tsv)
    f.close()
    return app.send_static_file('auxdata.tsv')


@app.route('/auxdata.tsv')
def data_file():
    return app.send_static_file('auxdata.tsv')


@app.route('/data.tsv')
def dataa_file():
    return app.send_static_file('data.tsv')

if __name__ == '__main__':
    app.run()



