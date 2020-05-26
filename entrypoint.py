#!/bin/env python3

import os
import sys
import datetime
import logging
import tempfile
import collections

# from action import build
from sphinx.cmd.build import main
from typing import Tuple, List

LineInfo = Tuple[str, int]

class AnnotationLevel:
    NOTICE = "notice"
    WARNING = "warning"
    FAILURE = "failure"


CheckAnnotation = collections.namedtuple(
    "CheckAnnotation", ["path", "start_line", "end_line", "annotation_level", "message"]
)


def annotate(annotation: str, out=sys.stdout):
    level_to_command = {
        AnnotationLevel.WARNING: "warning",
        AnnotationLevel.FAILURE: "error",
    }

    command = level_to_command[annotation.annotation_level]

    print(
        f"::{command} file={annotation.path},line={annotation.start_line}::{annotation.message}",
        file=out
    )




def extract_line_information(line_information: str) -> LineInfo:
    """
    Lines from sphinx log files look like this
        /warnings/index.rst:22: WARNING: Problems with "include" directive path:
        InputError: [Errno 2] No such file or directory: 'I_DONT_EXIST'.
    """
    file_and_line = line_information.split(":")
    # This is a dirty windows specific hack to deal with drive letters in the
    # start of the file-path, i.e D:\
    if len(file_and_line[0]) == 1:
        # If the first component is just one letter, we did an accidental split
        file_and_line[1] = file_and_line[0] + ":" + file_and_line[1]
        # Join the first component back up with the second and discard it.
        file_and_line = file_and_line[1:]

    if len(file_and_line) != 2 and len(file_and_line) != 3:
        raise ValueError("Generic Warning")

    # The case where we have no line number, in this case we return the line
    # number as 1 to mark the whole file.
    if len(file_and_line) == 2:
        line_num = 1
    if len(file_and_line) == 3:
        try:
            line_num = int(file_and_line[1])
        except ValueError:
            raise ValueError("Another Generic Error")

    file_name = os.path.relpath(file_and_line[0])
    return file_name, line_num


if __name__=='__main__':
    logging.debug("[build documentation] Starting documentation-action build.")

    logfile = os.path.join(tempfile.gettempdir(), "sphinx-log")
    if os.path.exists(logfile):
        os.unlink(logfile)

    input = os.environ.get("INPUT_DOCS", 'docs')
    output = os.environ.get("INPUT_DEST", 'build')

    options = f'--keep-going --no-color -a -q -w {logfile} {input} {output}'

    main(options.split(" "))

    with open(logfile) as logs:
        loglines = logs.readlines()
        for i, line in enumerate(loglines):
            if "WARNING" in line:
                location, message = line.split("WARNING:")
                logging.debug(f"{i}: {location} - {message}")

                try:
                    file_name, line_number = extract_line_information(location)
                except ValueError as e:
                    logging.debug(e)
                    continue

                # If this isn't the last line and the next line isn't a warning,
                # treat it as part of this warning message.
                if (i != len(loglines) - 1) and "WARNING" not in loglines[i + 1]:
                    message += loglines[i + 1]

                annotate(
                    CheckAnnotation(
                        path=file_name,
                        message=message.strip(),
                        start_line=line_number,
                        end_line=line_number,
                        annotation_level=AnnotationLevel.WARNING,
                    )
                )
