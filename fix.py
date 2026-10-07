"""Extract complete declared flash blocks from a linked RGBDS image."""
import argparse
from pathlib import Path
from tools.payload import extract_image

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('filename', help='linked image filename under bin/')
    args = parser.parse_args()
    path = Path('bin') / args.filename
    path.write_bytes(extract_image(path.read_bytes()))

if __name__ == '__main__':
    main()
