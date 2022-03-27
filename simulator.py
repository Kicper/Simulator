import psycopg2
import argparse
import sys
from datetime import datetime, timedelta
import random


def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


# get user input
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--number_of_records",
                    help="Number of records to generate", type=int, default=20)
parser.add_argument("-u", "--logins_list", nargs='+', help="Name of login")
parser.add_argument("-i", "--items_list", nargs='+', help="Name of item")
parser.add_argument("-b", "--beginning_date",
                    help="Date of beginning", type=datetime.fromisoformat, default=datetime.now())
parser.add_argument("-e", "--ending_date", help="Date of ending",
                    type=datetime.fromisoformat, default=datetime.now() + timedelta(days=5))
args = parser.parse_args()
print(args.number_of_records, args.logins_list,
      args.items_list, args.beginning_date, args.ending_date)


# connect to the db and create the cursor
con = psycopg2.connect(
    host="localhost",
    database="simulator_v1",
    user="postgres",
    password="66kipulet",
    port="5433"
)
cur = con.cursor()


# check if entered values are correct
if args.number_of_records <= 0:
    print("The number of records is incorrect!")
    sys.exit()
else:
    number_of_records = args.number_of_records

if args.ending_date - args.beginning_date <= timedelta(seconds=0):
    print("The date range is incorrect!")
    sys.exit()
else:
    ending_date = args.ending_date
    beginning_date = args.beginning_date

if not args.logins_list:
    cur.execute("SELECT person_id, login FROM person")
    logins_list = cur.fetchall()
elif len(args.logins_list) < 3:
    print("The list of logins must contain at least three logins!")
    sys.exit()
else:
    cur.execute("SELECT person_id, login FROM person")
    rows = cur.fetchall()
    logins_list = []
    for r in rows:
        if r[1] in args.logins_list:
            logins_list.append(r)
    if not logins_list or len(args.logins_list) > len(logins_list):
        print("The list of logins contains nonexisting login name!")
        sys.exit()

if not args.items_list:
    cur.execute("SELECT item_id, name FROM item")
    items_list = cur.fetchall()
else:
    cur.execute("SELECT item_id, name FROM item")
    rows = cur.fetchall()
    items_list = []
    for r in rows:
        if r[1] in args.items_list:
            items_list.append(r)
    if not items_list or len(args.items_list) > len(items_list):
        print("The list of items contains nonexisting item name!")
        sys.exit()


# create auctions
print(logins_list)
print(items_list)
for i in range(number_of_records):
    item = random.randint(0, len(items_list) - 1)
    sql = "INSERT INTO auction_history (item_id) VALUES (%s) RETURNING auction_history_id;"
    data = (str(items_list[item][0]),)
    cur.execute(sql, (data))
    auction_history_id = cur.fetchone()[0]
    con.commit()

    number_of_offer = random.randint(10, 20)
    price = random.randint(50, 100)
    next_date = random_date(
        beginning_date, beginning_date + timedelta(hours=5))

    login = random.randint(0, len(logins_list) - 1)
    person_id = str(logins_list[login][0])
    temp_logins_list = logins_list.copy()
    print(login)
    print("List:")
    print(logins_list)
    print("Temp list:")
    temp_logins_list.pop(login)
    print(temp_logins_list)

    for offer_iter in range(number_of_offer):
        sql = "INSERT INTO offer (date, price, status, person_id, auction_history_id) VALUES (%s,%s,%s,%s,%s) RETURNING offer_id;"
        data = (str(next_date), str(
            price), "not_finished", str(person_id), str(auction_history_id),)
        cur.execute(sql, (data))

        price += random.randint(1, 10)
        next_date = random_date(
            next_date, next_date + timedelta(hours=5))

        while True:
            temp_login = random.randint(0, len(temp_logins_list) - 1)
            if temp_login is not login:
                login = temp_login
                break

        person_id = str(temp_logins_list[login][0])

    sql = "INSERT INTO offer (date, price, status, person_id, auction_history_id) VALUES (%s,%s,%s,%s,%s) RETURNING offer_id;"
    data = (str(next_date), str(
        price), "finished", str(person_id), str(auction_history_id),)
    cur.execute(sql, (data))


con.commit()
cur.close()
con.close()
