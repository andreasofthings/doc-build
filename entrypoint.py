#!/bin/env python3

import sys
import datetime


if __name__=='__main__':
    hello = sys.argv[1]
    time = datetime.datetime.now()
    print(f"Hello {hello}")
    print(f"::set-output name=time::{time}")
