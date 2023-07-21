from pathlib import Path
import random

from flask import Response
import flask

from config import get_config


app = flask.Flask("wildcards-web")

config = get_config()
work_dir = Path(__file__).absolute()


@app.route("/wildcards")
def list_all_wildcards():
    all_wildcards = ["<h1>All Wildcards</h1>"]
    folder: Path
    for folder in config.files.wildcard_folders:
        try:
            all_wildcards.append(f"<h2>/{folder.relative_to(work_dir)}</h2>")
        except ValueError:
            all_wildcards.append(f"<h2>/{folder}</h2>")
        file: Path
        for file in folder.glob("*.txt"):
            all_wildcards.append(f'<a href="/{folder.name}/{file.name}">{file.stem}</a><br>')
    return Response("\n".join(all_wildcards), mimetype="text/html")


def get_random_from_dir(place: str) -> str|None:
    try:
        with open(place, "r", encoding='utf-8') as f:
            return random.choice(f.readlines()).strip()
    except FileNotFoundError: #pathlib considers `.__foo__` as `__foo__`, so we get the exception
        #404
        return Response(status=404)

@app.route("/<folder>/<path:subpath>")
def get_wildcard(folder: str, subpath: Path) -> str | None:
    subpath = Path(subpath)
    if subpath.suffix != ".txt" and config.privacy.arbitrary_files is False:
        return Response(status=403)
    # check if the folder is in the list of wildcard folders
    folder = next((x for x in config.files.wildcard_folders if x.name == folder), None)
    if folder is not None:
        # folder is on the list, send the file
        return get_random_from_dir(Path(folder, subpath))
    elif config.privacy.path_traversal is True:
        # path traversal is enabled, resolve the file path anyway
        return get_random_from_dir(work_dir.joinpath(folder, subpath).absolute())
    else:
        # path traversal is disabled and folder not on list, return 404
        return Response(status=404)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    tempmsg = f"{path} is empty or not a valid path."
    if config.privacy.enable_folder_listing is True:
        tempmsg += " Try <a href='/wildcards'>/wildcards</a>."
    return tempmsg


if __name__ == "__main__":
    app.run(
        host=config.server.bind,
        port=config.server.port
    )
