#!/usr/bin/env python3

import re

def main():
    n = int(input())
    p = ['16', '06', '90', '80']
    if n > 4:
        print('Glupenky Pierre')
    else:
        print(' '.join(p[:n]))


if __name__ == '__main__':
    main()
