from pathlib import Path
import glob

import toml
import flask

cfg = toml.load(Path("config.toml"))
app = flask.Flask("wildcards-web")

def showallwildcards():
    finalmsg = ""
    for path in cfg['files']["wildcard_folders"]:
        finalmsg += f"<b>{path}</b><br>"
        for fname in glob.glob(f"{path}/*.txt"):
            finalmsg += f"<a href={fname.replace(f'{path}/', '').removesuffix('.txt')}>{fname}</a><br>"
    return finalmsg


def getwildcard(fname) -> str|None:
    for possible_path in cfg['files']["wildcard_folders"]:
        if Path(f"{possible_path}/{fname}.txt").is_file():
            return f"{possible_path}/{fname}.txt"
    return None

def getfilecontent(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

@app.route("/")
def index():
    return "cheese"

@app.route("/<path:path>")
def getcont(path: str):
    if path == "wildcards" and cfg['privacy']["enable_folder_listing"]:
        return showallwildcards()
    if path == "/favicon.ico":
        #404
        return flask.Response(status=404)
    path = path.replace(".txt", "")
    if "." in path or "/" in path and not cfg['privacy']['subfolders']:
        #403
        return flask.Response(status=403)
    if not path.startswith("__") or not path.endswith("__") and not cfg["privacy"]['subfolders']:
        if not cfg['privacy']["arbitrary_access"]:
            #403
            return flask.Response(status=403)
    path = getwildcard(path)
    if path is not None:
        return getfilecontent(path)
    #404
    return flask.Response(status=404)

if __name__ == "__main__":
    app.run(port=cfg["server"]["port"])