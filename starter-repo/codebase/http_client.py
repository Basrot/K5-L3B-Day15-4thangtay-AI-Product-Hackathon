"""HTTP transport keeps bearer-authenticated requests on the configured URL."""

from urllib.request import HTTPRedirectHandler, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


urlopen = build_opener(NoRedirect).open
