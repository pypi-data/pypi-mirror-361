"""
Time tracking app. Originally inspired from https://textual.textualize.io/tutorial/
"""

import logging

from chronotui.app import StopwatchApp


def main():
    logging.basicConfig(
        level=logging.INFO,
        filename="chronotui.log",
    )
    app = StopwatchApp()
    app.title = "ChronoTUI"
    app.sub_title = "Track your time with style"
    app.run()


if __name__ == "__main__":
    main()
