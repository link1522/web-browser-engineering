import socket
import random
import urllib
import urllib.parse

ENTRIES = [
    ("No names. We are nameless!", "cerealkiller"),
    ("HACK THE PLANET!!!", "crashoverride"),
]
SESSION = {}
LOGIN = {"user1": "1234"}

s = socket.socket(
    family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(("", 8000))
s.listen()


def handle_connection(conx):
    req = conx.makefile("b")
    reqline = req.readline().decode("utf8")
    method, url, version = reqline.split(" ", 2)
    assert method in ["GET", "POST"]

    headers = {}
    while True:
        line = req.readline().decode("utf8")
        if line == "\r\n":
            break
        header, value = line.split(":", 1)
        headers[header.casefold()] = value.strip()

    if "content-length" in headers:
        length = int(headers["content-length"])
        body = req.read(length).decode("utf8")
    else:
        body = None

    if "cookie" in headers:
        token = headers["cookie"][len("token=") :]
    else:
        token = str(random.random())[2:]

    session = SESSION.setdefault(token, {})
    status, body = do_request(session, method, url, headers, body)

    response = "HTTP/1.0 {}\r\n".format(status)
    if "cookie" not in headers:
        response += "Set-Cookie: token={}; SameSite=Lax\r\n".format(token)
    if body is not None:
        response += "Content-Length: {}\r\n".format(len(body))
        response += "\r\n" + body

    conx.send(response.encode("utf8"))
    conx.close()


def do_request(session, method, url, headers, body):
    if method == "GET" and url == "/":
        return "200 OK", show_comment(session)
    elif method == "POST" and url == "/":
        params = form_decode(body)
        return do_login(session, params)
    elif method == "GET" and url == "/comment.js":
        with open("comment.js") as f:
            return "200 OK", f.read()
    elif method == "GET" and url == "/comment.css":
        with open("comment.css") as f:
            return "200 OK", f.read()
    elif method == "POST" and url == "/add":
        params = form_decode(body)
        return "200 OK", add_entry(session, params)
    elif method == "GET" and url == "/login":
        return "200 OK", login_form(session)
    else:
        return "404 Not Found", not_found(url, method)


def show_comment(session):
    out = "<!doctype html>"
    out += '<link rel="stylesheet" href="/comment.css">'
    for entry, who in ENTRIES:
        out += f"<p>{entry} \n <i>by {who}</i></p>"

    if "user" in session:
        nonce = str(random.random())[2:]
        session["nonce"] = nonce
        out += f"<h1>Hello, {session["user"]}</h1>"
        out += "<form action=add method=post>"
        out += f'  <input type=hidden name=nonce value="{nonce}">'
        out += "  <p><input name=guest></p>"
        out += "  <strong></strong>"
        out += "  <p><button>Sign the book!</button></p>"
        out += "</form>"
    else:
        out += "<a href=/login>Sign in to write in the guest book</a>"

    out += "<script src=/comment.js></script>"
    return out


def form_decode(body):
    params = {}
    for field in body.split("&"):
        name, value = field.split("=", 1)
        name = urllib.parse.unquote_plus(name)
        value = urllib.parse.unquote_plus(value)
        params[name] = value
    return params


def add_entry(session, params):
    if "nonce" not in session or "nonce" not in params:
        return
    if "user" not in session:
        return
    if "guest" in params and len(params["guest"]) <= 10:
        ENTRIES.append((params["guest"], session["user"]))
    return show_comment(session)


def login_form(session):
    body = "<!doctype html>"
    body += "<form action=/ method=post>"
    body += "  <p>Username: <input name=username /></p>"
    body += "  <p>Password: <input name=password type=password /></p>"
    body += "  <p><button>Log in</button></p>"
    body += "</form>"
    return body


def do_login(session, params):
    username = params.get("username")
    password = params.get("password")

    if username in LOGIN and LOGIN[username] == password:
        session["user"] = username
        return "200 OK", show_comment(session)
    else:
        out = "<!doctype html>"
        out += "<h1>Invalid password for {}</h1>".format(username)
        return "401 Unauthorized", out


def not_found(url, method):
    out = "<!doctype html>"
    out += f"<pre>{method} {url} not found</pre>"
    return out


while True:
    conx, addr = s.accept()
    handle_connection(conx)
