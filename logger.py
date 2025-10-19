import sys
from datetime import datetime

def timestamped_line(action, message):
    '''Converts into datetime and returns the message'''
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M')} [{action}] {message}"

def main():
    # ensures file usage is correct (2 args)
    if len(sys.argv) != 2:
        print("USAGE: logger.py <logfile>", file=sys.stderr)
        sys.exit(1)

    # fetch log file
    logfile = sys.argv[1]

    # loop to keep file open and continuously feed input to the file until 'QUIT' is inputted
    try:
        with open(logfile, "a", encoding="utf8") as f:
            while True:
                # ensure something was inputted
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.rstrip("\n")

                # log a quit on the file when the user inputs 'QUIT'
                if line == "QUIT":
                    entry = timestamped_line("QUIT", "Logger exiting.")
                    f.write(entry + "\n")
                    f.flush()
                    break
                if not line.strip():
                    continue

                # multiple word inputs are always commands first, so parse that
                parts = line.split(None, 1)
                action = parts[0]
                message = parts[1] if len(parts) > 1 else ""
                entry = timestamped_line(action, message)
                f.write(entry + "\n")
                f.flush()

    # if failure, output error
    except Exception as e:
        print("LOGGER ERROR:", e, file=sys.stderr)
        sys.exit(1)
        
if __name__ == "__main__":
    main()