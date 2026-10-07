"""Legacy bmvj_games/LOAD_FILE uploader; not the current REON admin importer."""
import os
import struct
import subprocess
import argparse
import mysql.connector
import bmvj_compress
from tools.payload import finalize_payload, set_game_id



parser = argparse.ArgumentParser(
                    prog='push.py',
                    description='adds a net-de-get minigame to the reon database')

parser.add_argument('filename')           # positional argument
parser.add_argument('dbuser')             # positional argument
parser.add_argument('dbpass')             # positional argument

args = parser.parse_args()

db = mysql.connector.connect(
  host="localhost",
  user=args.dbuser,
  password=args.dbpass,
  database="db"
)

game_binary = ""
with open("bin/%s" % args.filename, "rb") as game_bin:
	game_binary = game_bin.read()
	
game_binary = finalize_payload(game_binary)
if len(game_binary) > 65535:
    raise ValueError('legacy mode-5 upload supports at most 7 declared flash blocks')
cursor = db.cursor()
cursor.execute("INSERT INTO bmvj_games VALUES(NULL, 0, 0, 0, 0, 0, 0, \"\", \"\", 0, \"\")")

game_id = cursor.lastrowid
# insert game ID into binary
if not 0 <= game_id <= 999:
    db.rollback()
    raise ValueError('Net de Get game IDs must fit Gddd (0..999)')
game_binary = set_game_id(game_binary, f"G{game_id:03d}")

category = game_binary[6]
genre = game_binary[7]
with open("bin/%s.title" % args.filename, "wb") as title:
	t = game_binary[15:36]
	title.write(t[:t.find(b"\x00")])
with open("bin/%s.description" % args.filename, "wb") as description:
	d = game_binary[36:68]
	description.write(d[:d.find(b"\x00")])
with open("bin/%s.compressed" % args.filename, "wb") as compressed:
	compressed.write(bmvj_compress.bmvj_compress(game_binary))
	
subprocess.run(["cp", "./bin/%s.compressed" % args.filename, "/var/lib/mysql/tmp/"], check=True)
subprocess.run(["cp", "./bin/%s.title" % args.filename, "/var/lib/mysql/tmp/"], check=True)
subprocess.run(["cp", "./bin/%s.description" % args.filename, "/var/lib/mysql/tmp/"], check=True)

# TODO: get these from elsewhere i guess...?
level_react = 0
level_smart = 0
level_sense = 0
level_hidden = 0
price = 0

cursor.execute("UPDATE bmvj_games SET genre=%s,category=%s,level_react=%s,level_smart=%s,level_sense=%s,level_hidden=%s,title=LOAD_FILE(%s),description=LOAD_FILE(%s),price=%s,game_binary=LOAD_FILE(%s) WHERE id = %s", 
(genre, category, level_react, level_smart, level_sense, level_hidden, f'/var/lib/mysql/tmp/{args.filename}.title', f'/var/lib/mysql/tmp/{args.filename}.description', price, f'/var/lib/mysql/tmp/{args.filename}.compressed', game_id))
cursor.execute("SELECT OCTET_LENGTH(game_binary), OCTET_LENGTH(title), OCTET_LENGTH(description) FROM bmvj_games WHERE id = %s", (game_id,))
expected_lengths = tuple(os.path.getsize(f"bin/{args.filename}.{suffix}") for suffix in ('compressed', 'title', 'description'))
if cursor.fetchone() != expected_lengths:
    db.rollback()
    raise ValueError('legacy LOAD_FILE upload did not preserve all three files')
db.commit()
