import sys

from discord import Client, Message
import re
from itertools import zip_longest
from functools import partial

PAIGE_ID = "587299790900166669"
PAIGE_CHANNEL = "622489632239648789"
TOKEN = 'NjI4MTcxNDM3NzA5OTgzNzY0.XZOMNQ.HnIgv3NXPyJJhGXqe3Mv9fdTXTY'

cuties = [PAIGE_ID]

last_message = None

client = Client()


def parse_file(p):
	responses = {}
	with open(p) as f:
		for line in f:
			try:
				(key, value) = line.split('|')
				responses[key] = value.strip()
			except Exception:
				print("Warning, ill-formatted line:", line, file=sys.stderr)
	return responses


def grouper(iterable, n, fillvalue=None):
	"Collect data into fixed-length chunks or blocks"
	# grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
	args = [iter(iterable)] * n
	return zip_longest(fillvalue=fillvalue, *args)


def handle_paige(message: Message, content: str):
	if message is not None:
		author_id = str(message.author.id)
		channel_id = str(message.channel.id)
		if (channel_id != PAIGE_CHANNEL) and (author_id is not None) and (author_id not in cuties):
			return

	if "paige" in content.lower():
		return

	return "Hi " + content + ", I'm paigebot"


def from_file(path, default, message: Message, content: str):
	responses = parse_file(path)

	res = responses.get(content.lower())
	if res is None:
		res = default

	return res


def handle_source(message: Message, content: str):
	with open(__file__, "rb") as f:
		full_code = f.read().decode("utf-8").replace(TOKEN, "<REDACTED>")

		return ["`" + "``python\n" + "".join(x) + "``" + "`" for x in grouper(full_code, 1940, "")]


def handle_hebrew(message: Message, content: str):
	return "בקטנה"


def dad_me(message: Message, content: str):
	author_id = str(message.author.id)
	if author_id in cuties:
		return "Already in cuties!"

	cuties.append(author_id)
	print("cuties: ", cuties)
	return "u r dadded"


def undad_me(message: Message, content: str):
	author_id = str(message.author.id)
	if author_id not in cuties:
		return "Not in cuties!"

	cuties.remove(author_id)
	print("cuties: ", cuties)
	return "u r undadded"

def dad_this(message: Message, content: str):
	global last_message
	if last_message is None:
		return "can't dad this"

	return decode_message(last_message, True)

def punlist(message: Message, content: str):
	puns = parse_file("puns.txt")
	return '\n'.join(f"{name} - {pun}" for (name, pun) in puns.items())

def static(s: str, message: Message, content: str):
	return s

regexes = [
	("^(i'?m|i am) (?P<content>.*)", handle_paige),
	("^paigebot dad me", dad_me),
	("^paigebot punlist", punlist),
	("^paigebot undad me", undad_me),
	("^paigebot dad this", dad_this),
	("^paigebot pun (?P<content>.*)", partial(from_file, "puns.txt", "no puns given")),
	("^paigebot source", handle_source),
	("^paigebot (?P<content>.*)", partial(from_file, "commands.txt", "no puns given")),
	(r".*\b:?(goose|geese|honk):?\b.*", partial(static, "honk")),
	(".*(hj[öo]nk|hönk).*", partial(static, "hjönk")),
	(".*הונק.*", partial(static, "הונק")),
	("פייג'בוט את יודעת עברית?", handle_hebrew)
]


@client.event
async def on_message(message: Message):
	if message.author == client.user:
		return

	res = decode_message(message)

	if res is None:
		global last_message
		last_message = message
		return

	print(f"sending {res} ({len(res)})")

	if isinstance(res, str):
		await message.channel.send(res)
	else:
		for r in res:
			await message.channel.send(r)
	return


def decode_message(message, ignore_message = False):
	res = None
	content = message.clean_content

	for (regex, handler) in regexes:
		match = re.match(regex, content, re.IGNORECASE)
		if not match:
			continue
		res = handler(None if ignore_message else message, match.groupdict().get("content"))
		break
	return res


@client.event
async def on_ready():
	print("Logged in as " + client.user.name + " (" + str(client.user.id) + ")")


client.run(TOKEN)
