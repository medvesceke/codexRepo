#!/usr/bin/env python3
"""A small Slovenian contact form that appends submissions to data.txt."""

import csv
import html
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs


FORM_PAGE = """<!doctype html>
<html lang="sl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vnos podatkov</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, sans-serif; }
    body { margin: 0; padding: 2rem 1rem; background: #f3f6fb; color: #1f2937; }
    main { max-width: 30rem; margin: 3rem auto; padding: 2rem; background: white;
      border-radius: 1rem; box-shadow: 0 0.5rem 2rem #1f29371a; }
    h1 { margin-top: 0; }
    label { display: block; margin: 1rem 0 0.35rem; font-weight: 600; }
    input { box-sizing: border-box; width: 100%; padding: 0.75rem; border: 1px solid #9ca3af;
      border-radius: 0.4rem; font: inherit; }
    button { margin-top: 1.5rem; padding: 0.75rem 1rem; border: 0; border-radius: 0.4rem;
      background: #2458c6; color: white; font: inherit; font-weight: 600; cursor: pointer; }
    .message { padding: 0.75rem; border-radius: 0.4rem; background: #ecfdf5; }
    .error { background: #fef2f2; }
  </style>
</head>
<body>
  <main>
    <h1>Vnos podatkov</h1>
    __MESSAGE__
    <form action="/submit" method="post">
      <label for="ime">Ime</label>
      <input id="ime" name="ime" autocomplete="given-name" maxlength="100" required>
      <label for="priimek">Priimek</label>
      <input id="priimek" name="priimek" autocomplete="family-name" maxlength="100" required>
      <label for="email">E-pošta</label>
      <input id="email" name="email" type="email" autocomplete="email" maxlength="254" required>
      <button type="submit">Shrani</button>
    </form>
  </main>
</body>
</html>
"""


def render_page(message="", error=False):
    message_html = ""
    if message:
        css_class = "message error" if error else "message"
        message_html = f'<p class="{css_class}" role="status">{html.escape(message)}</p>'
    return FORM_PAGE.replace("__MESSAGE__", message_html).encode("utf-8")


class FormHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        body = render_page()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/submit":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400, "Neveljavna dolžina zahteve.")
            return
        if length < 1 or length > 10_000:
            self.send_error(400, "Neveljavna dolžina zahteve.")
            return

        fields = parse_qs(self.rfile.read(length).decode("utf-8", errors="replace"))
        ime = fields.get("ime", [""])[0].strip()
        priimek = fields.get("priimek", [""])[0].strip()
        email = fields.get("email", [""])[0].strip()
        if not ime or not priimek or len(ime) > 100 or len(priimek) > 100:
            self.respond(400, "Vnesite ime in priimek (največ 100 znakov).", error=True)
            return
        if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            self.respond(400, "Vnesite veljaven e-poštni naslov.", error=True)
            return

        data_path = Path.cwd() / "data.txt"
        write_header = not data_path.exists() or data_path.stat().st_size == 0
        with data_path.open("a", encoding="utf-8", newline="") as data_file:
            writer = csv.writer(data_file)
            if write_header:
                writer.writerow(["ime", "priimek", "email"])
            writer.writerow([ime, priimek, email])
        self.respond(200, "Podatki so shranjeni.")

    def respond(self, status, message, error=False):
        body = render_page(message, error=error)
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        # Keep submitted values out of the server log.
        super().log_message(format_string, *args)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), FormHandler)
    print("Obrazec je na voljo na http://127.0.0.1:8000", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStrežnik ustavljen.")
    finally:
        server.server_close()
