"""
numbers.py

TeamTalk bot that retrieves facts from the Numbers API.
It lacks some more advanced features that one would expect from this sort of
thing e.g. rate limiting and threading, but should serve as a basic example
upon which something better could be built."""

# A part of PyTeamTalk
# author: Carter Temm
# License: MIT


import requests
import teamtalk


# Extremely thin wrapper here
endpoint_url = "http://numbersapi.com/"


def make_request(*args):
	path = endpoint_url + "/".join(args)
	try:
		r = requests.get(path)
		r.raise_for_status()
	except Exception as exc:
		return str(exc)
	else:
		return r.text


def trivia(number=None):
	if not number:
		number = "random"
	elif number != "random" and not number.isdigit():
		return "Numbers must be digits"
	return make_request(number, "trivia")


def math(number=None):
	if not number:
		number = "random"
	elif number != "random" and not number.isdigit():
		return "Numbers must be digits"
	return make_request(number, "math")


def date(number=None):
	if not number:
		number = "random"
	elif number != "random" and number.count("/") != 1:
		return "Dates must be in M/D format"
	return make_request(number, "date")


def year(number=None):
	if not number:
		number = "random"
	elif not number != "random" and not number.isdigit():
		return "Numbers must be digits"
	return make_request(number, "year")


def help():
	return """Valid keywords: trivia, math, date or year followed by a number\rNumbers can be integers (duh), dates (month/day), or random for anything. if none is provided, random is assumed."""


t = teamtalk.TeamTalkServer()


@t.subscribe("messagedeliver")
def message(server, params):
	if params["type"] == teamtalk.USER_MSG:
		content = params["content"].strip().lower().split(" ")
		source = t.get_user(params["srcuserid"])
		if content[0] == "trivia":
			func = trivia
		elif content[0] == "math":
			func = math
		elif content[0] == "date":
			func = date
		elif content[0] == "year":
			func = year
		else:
			server.user_message(source, help())
			return
		server.user_message(source, func(*content[1:]))


if __name__ == "__main__":
	t.set_connection_info("example.com", 10333)
	t.connect()
	t.login("number bot", "admin", "password", "TeamTalkBotClient")
	t.handle_messages(1)
