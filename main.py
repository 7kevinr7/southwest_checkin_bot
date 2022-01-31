"""
This module contains the entry point for the bot
"""

import src.overseer as overwatch


def main():
    overseer = overwatch.Overseer()
    overseer.start()

if __name__ == '__main__':
    main()