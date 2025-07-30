import os
import logging
import subprocess
from pathlib import Path
from urllib.parse import quote
from urllib.parse import urlparse

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado


logger = logging.getLogger("jupyterlab_ensure_clone")
logger.setLevel(logging.DEBUG)


def git(*args, **kw):
    subprocess.check_call(("git", *args), env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}, **kw)


class RouteHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        data = self.get_json_body()
        repoUrl = data.get("repoUrl")
        if not repoUrl:
            raise tornado.web.HTTPError(400, "repoUrl is required")
        parsedUrl = urlparse(repoUrl)
        if not all((parsedUrl.scheme, parsedUrl.netloc, parsedUrl.path)):
            raise tornado.web.HTTPError(400, "invalid repoUrl")
        username = data.get("username")
        password = data.get("password")
        repoUrlOrig = repoUrl
        if username or password:
            username = quote(username, safe='')
            password = quote(password, safe='')
            repoUrl = f"https://{username}:{password}@{parsedUrl.netloc}{parsedUrl.path}"
        targetDir = data.get("targetDir", parsedUrl.path.rsplit("/", 1)[-1]).removesuffix(".git")
        targetDir = Path(targetDir).expanduser()
        if targetDir.is_dir():
            targetDir = str(targetDir)
            logger.info("targetDir %s exists, attempting git ls-remote...", targetDir)
            try:
                git("-C", targetDir, "ls-remote", "origin", "-q", stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                if repoUrlOrig != repoUrl:
                    logger.info("ls-remote failed, trying again with provided credentials")
                    try:
                        git("-C", targetDir, "remote", "set-url", "origin", repoUrl)
                        git("-C", targetDir, "ls-remote", "origin", "-q", stdout=subprocess.DEVNULL)
                    except subprocess.CalledProcessError:
                        pass  # fall through to failure response below
                    else:
                        logger.info("ls-remote succeeded, removing credentials from origin URL")
                        git("-C", targetDir, "remote", "set-url", "origin", repoUrlOrig)
                        self.set_status(204)
                        return self.finish()
                logger.info("ls-remote failed (expected in the pre-dialog check in the needCredentials case), see output above")
                raise tornado.web.HTTPError(400, reason="Failed to update, maybe due to bad credentials") from None
            logger.info("git ls-remote succeeded")
            self.set_status(204)
            return self.finish()
        targetDir = str(targetDir)
        logger.info("cloning into %s...", targetDir)
        try:
            git("clone", "-q", repoUrl, targetDir)
        except subprocess.CalledProcessError:
            logger.info("clone failed (expected in the pre-dialog check in the needCredentials case), see output above")
            raise tornado.web.HTTPError(400, reason="Failed to clone, maybe due to bad credentials") from None
        else:
            logger.info("cloned into %r", targetDir)
            if repoUrlOrig != repoUrl:
                logger.info("removing credentials from origin URL")
                git("-C", targetDir, "remote", "set-url", "origin", repoUrlOrig)
            self.set_status(204)
            return self.finish()


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "jupyterlab-ensure-clone")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
