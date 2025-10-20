#!/usr/bin/env python3
import sys
import subprocess
from subprocess import Popen, PIPE

def log(logger_stdin, action, message=""):
    '''Writes a message onto log'''

    if message:
        logger_stdin.write(f"{action} {message}\n")

    else:
        logger_stdin.write(f"{action}\n")

    logger_stdin.flush()

def read_response(proc):
    '''
    Gets response from user and 
        (1) ensures that there is something there
        (2) returns the non-newline version of the user input.
    '''

    line = proc.stdout.readline()

    if not line:
        return None
    
    return line.rstrip("\n")

def select_from_history(history, prompt_msg):
    '''
    Selects an item from history and returns it
    '''

    while True:
        if not history:
            print("History is empty.")
            return None
        
        print("History:")

        for i, item in enumerate(history):
            print(f"{i+1}: {item}")

        print("0: Enter a new string")
        choice = input(prompt_msg).strip()

        if choice == "0":
            return None
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(history):
                return history[idx]
            
        print("Invalid selection, try again.")

def main():
    if len(sys.argv) != 2:
        print("Usage: driver.py <logfile>")
        sys.exit(1)
        
    logfile = sys.argv[1]

    # start logger and encryption subprocesses
    logger = Popen([sys.executable, "logger.py", logfile], stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding="utf8")
    encrypt = Popen([sys.executable, "encrypt.py"], stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding="utf8")

    history = []

    # Log driver start
    log(logger.stdin, "START", "Driver started.")
    print("Driver started. Type a command (password, encrypt, decrypt, history, quit).")

    try:
        while True:
            cmd = input("Command> ").strip().lower()

            if not cmd:
                continue

            log(logger.stdin, "CMD", cmd)

            if cmd == "password":
                sel = select_from_history(history, "Select history number (or 0 for new): ")
                if sel is None:
                    pw = input("Enter password (letters only): ").strip()
                    if not pw.isalpha():
                        print("Error: password must contain only letters.")
                        log(logger.stdin, "ERROR", "Password contains non-letters")
                        continue

                    encrypt.stdin.write(f"PASS {pw}\n")
                    encrypt.stdin.flush()
                    resp = read_response(encrypt)

                    if resp is None:
                        print("Encryption program closed unexpectedly.")
                        log(logger.stdin, "ERROR", "Encryption program closed")
                        break

                    print(resp)
                    log(logger.stdin, "RESULT_ENC", resp)
                else:
                    # use selected history string as passkey
                    pw = sel
                    encrypt.stdin.write(f"PASS {pw}\n")
                    encrypt.stdin.flush()
                    resp = read_response(encrypt)

                    if resp is None:
                        print("Encryption program closed unexpectedly.")
                        log(logger.stdin, "ERROR", "Encryption program closed")
                        break

                    print(resp)
                    log(logger.stdin, "RESULT_ENC", resp)

            elif cmd in ("encrypt", "decrypt"):
                sel = select_from_history(history, "Select history number to use (or 0 for new): ")

                if sel is None:
                    s = input("Enter string (letters only): ").strip()

                    if not s.isalpha():
                        print("Error: input must contain only letters (no spaces or punctuation).")
                        log(logger.stdin, "ERROR", "Non-letter input for encrypt/decrypt")
                        continue

                    s_up = s.upper()
                    history.append(s_up)
                    # send to encryption program
                    action = "ENCRYPT" if cmd == "encrypt" else "DECRYPT"
                    encrypt.stdin.write(f"{action} {s_up}\n")
                    encrypt.stdin.flush()
                    resp = read_response(encrypt)

                    if resp is None:
                        print("Encryption program closed unexpectedly.")
                        log(logger.stdin, "ERROR", "Encryption program closed")
                        break

                    print(resp)
                    log(logger.stdin, "RESULT_ENC", resp)

                    # if success and RESULT <value>, save result into history
                    if resp.startswith("RESULT "):
                        history.append(resp[len("RESULT "):])

                else:
                    s_up = sel
                    action = "ENCRYPT" if cmd == "encrypt" else "DECRYPT"
                    encrypt.stdin.write(f"{action} {s_up}\n")
                    encrypt.stdin.flush()
                    resp = read_response(encrypt)

                    if resp is None:
                        print("Encryption program closed unexpectedly.")
                        log(logger.stdin, "ERROR", "Encryption program closed")
                        break

                    print(resp)
                    log(logger.stdin, "RESULT_ENC", resp)

                    if resp.startswith("RESULT "):
                        history.append(resp[len("RESULT "):])

            elif cmd == "history":
                if not history:
                    print("History empty.")
                else:
                    print("History:")
                    for i, item in enumerate(history):
                        print(f"{i+1}: {item}")

                log(logger.stdin, "RESULT", "Displayed history")

            # Send QUIT to encrypt and logger, log driver exit, then exit.
            elif cmd == "quit":
                encrypt.stdin.write("QUIT\n")
                encrypt.stdin.flush()
                log(logger.stdin, "EXIT", "Driver exiting.")
                logger.stdin.write("QUIT\n")
                logger.stdin.flush()
                print("Exiting.")
                break

            else:
                print("Unknown command. Valid: password, encrypt, decrypt, history, quit")
                log(logger.stdin, "ERROR", "Unknown command")

    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted. Exiting.")
        log(logger.stdin, "EXIT", "Driver interrupted and exiting.")

        try:
            encrypt.stdin.write("QUIT\n"); encrypt.stdin.flush()
            logger.stdin.write("QUIT\n"); logger.stdin.flush()
        except Exception:
            pass

    finally:
        encrypt.wait()
        logger.wait()

if __name__ == "__main__":
    main()
