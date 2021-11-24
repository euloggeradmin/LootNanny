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