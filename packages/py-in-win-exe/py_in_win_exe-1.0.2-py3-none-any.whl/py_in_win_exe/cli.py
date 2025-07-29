import argparse
from .compiler import compile_script

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("script", help="Python script to compile")
    parser.add_argument("--output", "-o", default="output")
    parser.add_argument("--icon", "-i", default=None)
    parser.add_argument("--no-console", action="store_true")
    args = parser.parse_args()
    
    compile_script(
        args.script,
        args.output,
        args.icon,
        not args.no_console
    )