

import compatibility_check

from btcrecover import btcrpass, success_alert
import sys, multiprocessing

if __name__ == "__main__":
    print()
    print(
        "Starting",
        btcrpass.full_version(),
        file=sys.stderr if any(a.startswith("--listp") for a in sys.argv[1:]) else sys.stdout,
    )  # --listpass

    btcrpass.parse_arguments(sys.argv[1:])
    (password_found, not_found_msg) = btcrpass.main()

    if isinstance(password_found, str):
        success_alert.start_success_beep()
        print("----------------------------------------------------------")

        print()
        btcrpass.safe_print("Password found: '" + password_found + "'")
        if any(ord(c) < 32 or ord(c) > 126 for c in password_found):
            print(
                "HTML Encoded Password:   '"
                + password_found.encode("ascii", "xmlcharrefreplace").decode()
                + "'"
            )
        success_alert.wait_for_user_to_stop()
        retval = 0

    elif not_found_msg:
        print(not_found_msg, file=sys.stderr if btcrpass.args.listpass else sys.stdout)
        success_alert.beep_failure_once()
        retval = 0

    else:
        success_alert.beep_failure_once()
        retval = 1  # An error occurred or Ctrl-C was pressed

    # Wait for any remaining child processes to exit cleanly (to avoid error messages from gc)
    for process in multiprocessing.active_children():
        process.join(1.0)

    success_alert.stop_success_beep()

    sys.exit(retval)
