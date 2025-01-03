import socket
import ssl


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
        if not url.endswith("/"):
            url += "/"
        host, path = url.split("/", 1)
        path = "/" + path

        port = 80 if self.scheme == "http" else 443
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        return host, path, port

    def request(self) -> str:
        if self.scheme == "data":
            content = self.path.split(",", 1)[1]
            return content
        elif self.scheme in ["http", "https"]:
            return self._fetchDataFromHttp()
        elif self.scheme == "file":
            return self._fetchDataFromLocal()

    def _fetchDataFromHttp(self) -> str:
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        headers = {
            "Host": self.host,
            "Connection": "close",
            "User-Agent": "MyBrowser/1.0",
        }
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        for header, value in headers.items():
            request += "{}: {}\r\n".format(header, value)
        request += "\r\n"
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

        content = response.read()
        s.close()

        return content

    def _fetchDataFromLocal(self) -> str:
        with open(self.path, "r", encoding="utf8") as file:
            content = file.read()
            return content


def show(body):
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
    print(content)


def load(url: URL):
    body = url.request()
    show(body)


if __name__ == "__main__":
    import sys

    load(URL(sys.argv[1]))
