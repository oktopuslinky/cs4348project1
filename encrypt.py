import sys

def vigenere(text, key, method):
    '''
    Encrypts/decrypts using Vigenere, separates using method
    method values: 0 for encryption, 1 for decryption
    '''

    result_text = []
    key_length = len(key)
    key_index = 0

    for char in text:
        # skip character if space or non-alphabet
        if char == " ":
            result_text.append(" ")
            continue
        if not char.isalpha():
            result_text.append(char)
            continue

        # convert letters to 0–25 range
        char_val = ord(char) - ord('A')
        key_val = ord(key[key_index % key_length]) - ord('A')

        if method == 0: # encryption
            # shift forward for encryption
            result_val = (char_val + key_val) % 26
        else: # decryption
            # shift backward for decryption
            result_val = (char_val - key_val) % 26

        # convert back to letter and append
        result_text.append(chr(result_val + ord('A')))
        key_index += 1

    return "".join(result_text)

def main():
    """
    Reads user inputted commands, processes them, and outputs result.
    Commands:
      - PASS/PASSKEY/PASSWORD <key>
      - ENCRYPT <text>
      - DECRYPT <text>
      - QUIT
    """

    current_key = None

    try:
        while True:
            # read line of input and validate
            line = sys.stdin.readline()

            if not line:
                break
            
            line = line.rstrip("\n")
            if not line:
                continue

            # split input into command and argument
            parts = line.split(None, 1)
            command = parts[0].upper()
            argument = parts[1] if len(parts) > 1 else ""

            # QUIT COMMAND
            if command == "QUIT":
                break # exit program

            # PASS/PASSKEY/PASSWORD COMMAND
            elif command in ("PASS", "PASSKEY", "PASSWORD"):
                # if no key present in command
                if not argument:
                    print("ERROR Password missing")
                    sys.stdout.flush()
                # good case
                else:
                    # process input and set key
                    key_input = argument.strip().upper()
                    if not key_input.isalpha():
                        print("ERROR Password must contain only letters")
                        sys.stdout.flush()
                    else:
                        current_key = key_input
                        print("RESULT")
                        sys.stdout.flush()

            # ENCRYPT COMMAND
            elif command == "ENCRYPT":
                # can't encrypt without key
                if current_key is None:
                    print("ERROR Password not set")
                    sys.stdout.flush()
                else:
                    text_input = argument.strip().upper()

                    # only allow letters and spaces
                    if not all(ch.isalpha() or ch == " " for ch in text_input):
                        print("ERROR Input must contain only letters and spaces")
                        sys.stdout.flush()
                    # good case
                    else:
                        # encrypt and print
                        encrypted_output = vigenere(text_input, current_key, 0)
                        print("RESULT " + encrypted_output)
                        sys.stdout.flush()

            # DECRYPT COMMAND
            elif command == "DECRYPT":
                # can't decrypt without key
                if current_key is None:
                    print("ERROR Password not set")
                    sys.stdout.flush()
                else:
                    text_input = argument.strip().upper()

                    if not all(ch.isalpha() or ch == " " for ch in text_input):
                        print("ERROR Input must contain only letters and spaces")
                        sys.stdout.flush()
                    else:
                        decrypted_output = vigenere(text_input, current_key, 1)
                        print("RESULT " + decrypted_output)
                        sys.stdout.flush()

            # ANY OTHER UNKNOWN COMMAND
            else:
                print("ERROR Unknown command")
                sys.stdout.flush()
    # output error if needed
    except Exception as error:
        print("ERROR " + str(error))
        sys.stdout.flush()


if __name__ == "__main__":
    main()