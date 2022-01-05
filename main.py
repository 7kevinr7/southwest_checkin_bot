# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 14:56:52 2021

@author: krose
"""

import src.overseer as overwatch


def main():
    overseer = overwatch.Overseer()
    overseer.start()

if __name__ == '__main__':
    main()