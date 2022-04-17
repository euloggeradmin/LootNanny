# LootNanny
 

## How to build from source

1. Install Python: [At Microsoft](https://docs.microsoft.com/en-us/windows/python/beginners#install-python)
2. Run the following commands to setup your python environment

```
cd $PATH_YOU_DOWNLOADED_THIS_REPO
python -m pip install -r requirements.txt
pyinstaller.exe LootNanny.spec
```

This will generate the latest release executable in the dist/ folder.

## Additional Notes / known bugs

* If building with a **Virtual Environment**, ensure your `env\Lib\site-packages` directory is on your `PYTHONPATH` environment variable

* If you encounter `PermissionError: [WinError 5] Access is denied` errors when building via `pyinstaller`, build using an elevated command prompt ( Run as Administrator )

## LootNanny Setup Instructions
[Click here for a quick setup guide](docs/SETUP.MD)