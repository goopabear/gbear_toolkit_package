# gbear-toolkit

Personal Python toolkit: `DataTable` for loading and validating tabular data, plus folder and project-path helpers.

Requires Python 3.14+.

## Using it in another project

The package is installed as `gbear-toolkit` and imported as `gbear_toolkit`.

### Install from a local folder

Point the other project at this folder. `--editable` means changes you make here show up there immediately, without reinstalling.

With uv (run inside the other project):

```
uv add --editable ../gbear_toolkit_package
```

With pip (inside the other project's virtual environment):

```
pip install -e ../gbear_toolkit_package
```

Replace `../gbear_toolkit_package` with the actual path to this folder (absolute paths work too).

### Install from GitHub

```
uv add git+https://github.com/goopabear/gbear_toolkit_package
```

```
pip install git+https://github.com/goopabear/gbear_toolkit_package
```

Add `@<tag-or-commit>` to the end of the URL to pin a specific version.

### Update

Editable installs from a local folder are always current, so there's nothing to update.

For a GitHub install, pull the latest commit:

```
uv sync --upgrade-package gbear-toolkit
```

```
pip install --force-reinstall git+https://github.com/goopabear/gbear_toolkit_package
```

`--force-reinstall` is needed because pip skips reinstalling when the version number in `pyproject.toml` hasn't changed.

### Import

```python
from gbear_toolkit import DataTable
from gbear_toolkit.folder_ops import create_at, copy, delete
from gbear_toolkit.project_paths import ProjectPaths

d = DataTable()
d.load_csv('C:/path/to/prices.csv', pk='asin')
print(d.headers)
```

### Check that it worked

```
python -c "import gbear_toolkit; print(gbear_toolkit.__file__)"
```

For an editable install, the printed path points into this folder's `src/gbear_toolkit/`.
