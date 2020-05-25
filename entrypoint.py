#!/bin/env python3

import os
import sys
import datetime
import logging
import tempfile
import collections

# from action import build
from sphinx.cmd.build import main



class AnnotationLevel:
    # Notices are not currently supported.
    # NOTICE = "notice"
    WARNING = "warning"
    FAILURE = "failure"


CheckAnnotation = collections.namedtuple(
    "CheckAnnotation", ["path", "start_line", "end_line", "annotation_level", "message"]
)


def output(annotation, where_to_print=sys.stdout):
    level_to_command = {
        AnnotationLevel.WARNING: "warning",
        AnnotationLevel.FAILURE: "error",
    }

    command = level_to_command[annotation.annotation_level]

    print(
        "::{command} file={file},line={line}::{message}".format(
            command=command,
            file=annotation.path,
            line=annotation.start_line,
            message=annotation.message,
        ),
        file=where_to_print,
    )




def extract_line_information(line_information):
    r"""Lines from sphinx log files look like this
        C:\Users\ammar\workspace\sphinx-action\tests\test_projects\warnings\index.rst:22: WARNING: Problems with "include" directive path:
        InputError: [Errno 2] No such file or directory: 'I_DONT_EXIST'.
        /home/users/ammar/workspace/sphix-action/tests/test_projects/warnings/index.rst:22: WARNING: Problems with "include" directive path:
        InputError: [Errno 2] No such file or directory: 'I_DONT_EXIST'.
        /home/users/ammar/workspace/sphix-action/tests/test_projects/warnings/index.rst: Something went wrong with this whole ifle
    This method is responsible for parsing out the line number and file name from these lines.
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
        return None
    # The case where we have no line number, in this case we return the line
    # number as 1 to mark the whole file.
    if len(file_and_line) == 2:
        line_num = 1
    if len(file_and_line) == 3:
        try:
            line_num = int(file_and_line[1])
        except ValueError:
            return None

    file_name = os.path.relpath(file_and_line[0])
    return file_name, line_num

def parse_sphinx_warnings_log(logfile):
    """Parses a sphinx file containing warnings and errors into a list of
    status_check.CheckAnnotation objects.
    Inputs look like this:
        /warnings_and_errors/index.rst:19: WARNING: Error in "code-block" directive:
            maximum 1 argument(s) allowed, 2 supplied.
    """
    annotations = []
    with open(logfile) as logs:
        for i, line in enumerate(logs.readlines()):
            if "WARNING" not in line:
                continue

            warning_tokens = line.split("WARNING:")

            if len(warning_tokens) != 2:
                continue
            file_and_line, message = warning_tokens

            file_and_line = extract_line_information(file_and_line)
            if not file_and_line:
                continue
            file_name, line_number = file_and_line

            warning_message = message
            # If this isn't the last line and the next line isn't a warning,
            # treat it as part of this warning message.
            if (i != len(logs) - 1) and "WARNING" not in logs[i + 1]:
                warning_message += logs[i + 1]
            warning_message = warning_message.strip()

            annotations.append(
                CheckAnnotation(
                    path=file_name,
                    message=warning_message,
                    start_line=line_number,
                    end_line=line_number,
                    annotation_level=AnnotationLevel.WARNING,
                )
            )

        return annotations



if __name__=='__main__':
    time = datetime.datetime.now()

    logging.debug("[build documentation] Starting documentation-action build.")

    log_file = os.path.join(tempfile.gettempdir(), "sphinx-log")
    if os.path.exists(log_file):
        os.unlink(log_file)

    input = os.environ.get("INPUT_DOCS", 'docs')
    output = os.environ.get("INPUT_DEST", 'build')

    sphinx_options = f'--keep-going --no-color -a -w {log_file} {input} {output}'
    main(sphinx_options.split(" "))
    for annotation in parse_sphinx_warnings_log(log_file):
        output(annotation)
    print(f"::set-output name=time::{time}")
