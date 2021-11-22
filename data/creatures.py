import json
import sys


ALL_CREATURES = []



if __name__ == "__main__":
    import sys

    for fn in sys.argv[1:]:
        with open(fn, 'r') as f:
            header = True
            for line in f.readlines():
                if header:
                    header = False
                    continue
                print(line.split(";"))
