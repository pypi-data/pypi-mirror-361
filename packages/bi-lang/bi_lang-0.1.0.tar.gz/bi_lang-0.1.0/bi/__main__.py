import sys
from bi import run_file

def main():
    if len(sys.argv) < 2:
        print("Usage: bi <filename.bi>")
        sys.exit(1)
    filename = sys.argv[1]
    run_file(filename)

if __name__ == "__main__":
    main()
