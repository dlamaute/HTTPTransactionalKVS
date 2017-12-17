import http.server
from starry_hw import HTTPTransactionalRequestHandler

def run(host="", port=4000):
    httpd = http.server.HTTPServer((host, port), HTTPTransactionalRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
