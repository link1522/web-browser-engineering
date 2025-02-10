import socket
import ssl
import config


class URL:
    def __init__(self, url: str):
        if url.startswith("data:"):
            self.scheme, self.path = url.split(":", 1)
            return

        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]

        if self.scheme in ["http", "https"]:
            self.host, self.path, self.port = self._parse_host_path_port(url)
        elif self.scheme == "file":
            self.path = url

    def _parse_host_path_port(self, url: str) -> tuple[str, str]:
        if not "/" in url:
            url += "/"
        host, path = url.split("/", 1)
        path = "/" + path

        port = 80 if self.scheme == "http" else 443
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        return host, path, port

    def request(self, referer, payload=None) -> str:
        if self.scheme == "data":
            content = self.path.split(",", 1)[1]
            return content
        elif self.scheme in ["http", "https"]:
            return self._fetchDataFromHttp(referer, payload)
        elif self.scheme == "file":
            return self._fetchDataFromLocal()

    def _fetchDataFromHttp(self, referer, payload=None) -> str:
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        method = "POST" if payload else "GET"

        headers = {
            "Host": self.host,
            "Connection": "close",
            "User-Agent": "MyBrowser/1.0",
        }
        request = "{} {} HTTP/1.0\r\n".format(method, self.path)

        if payload:
            headers["Content-Length"] = len(payload.encode("utf8"))

        if self.host in config.COOKIE_JAR:
            cookie, params = config.COOKIE_JAR[self.host]
            allow_cookie = True
            if referer and params.get("samesite", "none") == "lax":
                if method != "GET":
                    allow_cookie = self.host == referer.host
            if allow_cookie:
                headers["Cookie"] = cookie

        for header, value in headers.items():
            request += "{}: {}\r\n".format(header, value)
        request += "\r\n"
        if payload:
            request += payload
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        if "set-cookie" in response_headers:
            cookie = response_headers["set-cookie"]
            params = {}
            if ";" in cookie:
                cookie, rest = cookie.split(";", 1)
                for param in rest.split(";"):
                    if "=" in param:
                        param, value = param.split("=", 1)
                    else:
                        value = True
                    params[param.strip().casefold()] = value.casefold()

            config.COOKIE_JAR[self.host] = (cookie, params)

        content = response.read()
        s.close()

        return content

    def _fetchDataFromLocal(self) -> str:
        with open(self.path, "r", encoding="utf8") as file:
            content = file.read()
            return content

    def resolve(self, url):
        if "://" in url:
            return URL(url)
        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url
        if url.startswith("//"):
            return URL(self.scheme + ":" + url)
        elif self.scheme == "file":
            return URL(self.scheme + "://" + url)
        else:
            return URL(self.scheme + "://" + self.host + ":" + str(self.port) + url)

    def origin(self):
        return self.scheme + "://" + self.host + ":" + str(self.port)

    def __str__(self):
        if self.scheme == "file":
            return "file://" + self.path

        port_part = ":" + str(self.port)
        if self.scheme == "https" and self.port == 443:
            port_part = ""
        if self.scheme == "http" and self.port == 80:
            port_part = ""
        return self.scheme + "://" + self.host + port_part + self.path


def lex(body):
    in_tag = False
    content = ""

    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            content += c

    content = content.replace("&lt;", "<").replace("&gt;", ">")
    return content


def load(url: URL):
    body = url.request()
    lex(body)


if __name__ == "__main__":
    import sys

    load(URL(sys.argv[1]))
