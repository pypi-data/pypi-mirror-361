import click
import json
from . import displayJSON, displayXML

@click.command()
@click.argument('file', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('out', type=click.Path(exists=True, file_okay=True, dir_okay=False), default=None, required=False)
def main(file, out=None):
    from pathlib import Path
    file = Path(file)
    if file.suffix == ".json":
        with open(file) as f:
            _ = json.load(f)
            res = displayJSON(_, display=False)
    elif file.suffix == ".xml":
        with open(file) as f:
            _ = f.read()
            res = displayXML(_, display=False)
    else:
        raise ValueError(f"Unsupported file type {file.suffix}. Please provide a .json or .xml file.")
    if out is not None:
        with open(out, 'w') as f:
            f.write(res)
    else:
        print(res)

if __name__ == "__main__":
    main()
