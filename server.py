from pathlib import Path

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
        all_wildcards.append(f"<h2>/{folder.relative_to(work_dir)}</h2>")
        file: Path
        for file in folder.glob("*.txt"):
            all_wildcards.append(f'<a href="/{folder.name}/{file.name}">{file.stem}</a><br>')
    return Response("\n".join(all_wildcards), mimetype="text/html")


@app.route("/<folder>/<path:subpath>")
def get_wildcard(folder: str, subpath: Path) -> str | None:
    subpath = Path(subpath)
    if subpath.suffix != ".txt" and config.privacy.arbitrary_files is False:
        return Response(status=403)
    # check if the folder is in the list of wildcard folders
    folder = next((x for x in config.files.wildcard_folders if x.name == folder), None)

    if folder is not None:
        # folder is on the list, send the file
        return flask.send_from_directory(folder, subpath)
    elif config.privacy.path_traversal is True:
        # path traversal is enabled, resolve the file path anyway
        return flask.send_file(work_dir.joinpath(folder, subpath).absolute())
    else:
        # path traversal is disabled and folder not on list, return 404
        return Response(status=404)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return f"{path} is empty or not a valid path. Try <a href='/wildcards'>/wildcards</a>."


if __name__ == "__main__":
    app.run(
        host=config.server.bind,
        port=config.server.port,
    )
