import sys
from moody.core import run_moodylang, interactive_interpreter

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "-i":
        interactive_interpreter()
        sys.exit(0)

    debug_mode = False
    if "-d" in sys.argv:
        debug_mode = True
        sys.argv.remove("-d")

    if len(sys.argv) != 2 or not sys.argv[1].endswith(".moody"):
        print("Usage: moodylang <file.moody> [-d] | moodylang -i")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        code = f.readlines()
    result = run_moodylang(code, debug=debug_mode)
    print(result)
