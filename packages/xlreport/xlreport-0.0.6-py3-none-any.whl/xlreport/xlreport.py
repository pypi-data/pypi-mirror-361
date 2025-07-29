#!/usr/bin/python
# coding=utf-8'
#
# Copyright (c)  Tomasz Sługocki ts.kontakt@gmail.com
# This code is licensed under Apache 2.0
import os
import re
import subprocess
import sys
from itertools import zip_longest
from math import log

import xlsxwriter as xls

HEADER_FONT_NAME = "Times"
GEN_FONT_NAME = "Arial"
FONT_SIZE = 9
WRAP_FONT_SIZE = 9
TITLE_RANGE = "B1:E1"
HEADER_BG_COLOR = "#D4D0C8"
HEADER_FONT_COLOR = "#003366"
NUM_FORMAT = "0.00;[RED]-0.00"
TITLE_BG = "#F1F1F1"


def ensure_unicode(input_value):
    if "bytes" in repr(type(input_value)):
        return input_value.decode("utf8")
    return input_value


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def is_nested(inlist):
    first = None
    nested = True
    try:
        first = next(i for i in inlist)
        print(first)
    except TypeError:
        nested = False
    if 'str' in repr(type(first)):
        nested = False
    else:
        try:
            next(i for i in first)
        except TypeError:
            nested = False
    return nested


class Exfile:

    def __init__(self, filename):
        assert ".xlsx" in filename
        filename.upper()
        self.workbook = xls.Workbook(filename)

        file_path = (filename if os.sep in filename else os.path.join(os.getcwd(), filename))
        self.file_path = file_path

    @staticmethod
    def calculate_column_width(text_length):
        # Adjust column width based on header  text length
        extra_width = text_length / 10 + 10 if text_length > 20 else 0

        if text_length <= 3:
            return 3
        return (((51.16 * log(text_length) - 38.395) * 0.85) / 10 + (log(text_length) * 2) +
                extra_width)

    def write(self, data_list, title, worksheet_name=None, wrap=False):
        datatype = repr(type(data_list)).lower()
        print(datatype)
        assert re.search("list|dict_values|dataframe|array|tuple|set", datatype)

        if "dataframe" in datatype:
            new_list = [["idx"] + list(data_list.columns)]
            new_list.extend(data_list.to_records())
            data_list = new_list
        else:
            if not is_nested(data_list):
                data_list = ['h'] + list(zip_longest(data_list, fillvalue=[]))

        title.upper()
        if worksheet_name:
            worksheet_name.upper()
        # global configs

        worksheet = self.workbook.add_worksheet(ensure_unicode(worksheet_name))
        number_format = "#,##0;[Red]-#,##0"
        start_row = 4
        start_column = 1

        merge_format = self.workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "fg_color": TITLE_BG,
            "text_wrap": True,
            "font_name": HEADER_FONT_NAME,
            "font_size": 12,
        })

        worksheet.merge_range(TITLE_RANGE, ensure_unicode(title), merge_format)

        header_format = self.workbook.add_format()
        header_format.set_bold()
        header_format.set_font_color(HEADER_FONT_COLOR)
        header_format.set_font_size(9)
        header_format.set_bg_color(HEADER_BG_COLOR)
        header_format.set_indent(1)

        cell_format = self.workbook.add_format({
            "font_name": GEN_FONT_NAME,
            "font_size": FONT_SIZE,
            "num_format": number_format,
        })

        decimal_format = self.workbook.add_format({
            "font_size": FONT_SIZE,
            "num_format": NUM_FORMAT
        })

        long_text_format = self.workbook.add_format({
            "text_wrap": True,
            "font_size": WRAP_FONT_SIZE
        })
        long_text_format.set_align("vcenter")

        for column_index, header_value in enumerate(data_list[0]):
            text_length = len(repr(header_value))
            column_width = self.calculate_column_width(text_length)
            worksheet.set_column(start_column + column_index, start_column + column_index,
                                 column_width)

        worksheet.freeze_panes(start_row, 0)

        for column_index, header_value in enumerate(data_list[0]):
            if "str" in repr(type(header_value)):
                header_value = ensure_unicode(header_value)

            worksheet.write(
                start_row - 1,
                start_column + column_index,
                str(header_value).strip(),
                header_format,
            )

        for row_index, row_data in enumerate(data_list[1:]):
            current_row = start_row + row_index
            for column_index, cell_value in enumerate(row_data):
                if "str" in repr(type(cell_value)):
                    try:
                        cell_value = ensure_unicode(cell_value)
                    except UnicodeDecodeError:
                        print("! decode error")
                        print([cell_value])

                    if wrap:
                        worksheet.write(
                            current_row,
                            start_column + column_index,
                            cell_value,
                            long_text_format,
                        )
                    else:
                        worksheet.write(
                            current_row,
                            start_column + column_index,
                            cell_value,
                            cell_format,
                        )
                else:
                    try:
                        if abs(cell_value) < 20.0 and int(cell_value) != round(cell_value, 2):
                            worksheet.write(
                                current_row,
                                start_column + column_index,
                                cell_value,
                                decimal_format,
                            )
                        else:
                            worksheet.write(
                                current_row,
                                start_column + column_index,
                                cell_value,
                                cell_format,
                            )
                    except TypeError:
                        cell_value = " " + str(repr(cell_value))[:200]
                        worksheet.write(
                            current_row,
                            start_column + column_index,
                            cell_value,
                            cell_format,
                        )
        return worksheet

    def add_links(self):
        start_column = 6
        start_row = 0
        worksheets = self.workbook.worksheets()

        inactive_format = self.workbook.add_format({
            "font_color": "gray",
            "bold": 0,
            "underline": 1,
            # "font_size": 10,
        })

        for source_sheet in worksheets:
            link_index = 0
            for target_sheet in worksheets:
                if target_sheet.name == source_sheet.name:
                    source_sheet.write_url(
                        start_row,
                        start_column + link_index,
                        f"internal:'{target_sheet.name}'!A1",
                        inactive_format,
                        string=target_sheet.name,
                    )
                else:
                    source_sheet.write_url(
                        start_row,
                        start_column + link_index,
                        f"internal:'{target_sheet.name}'!A1",
                        string=target_sheet.name,
                    )
                link_index += 1

    def save(self, start=True):
        try:
            self.workbook.close()
            if start:
                open_file(self.file_path)

        except BaseException:
            print(sys.exc_info())
            if "denied" in repr(sys.exc_info()):
                print("! Cannot write file - permission error")
                self.workbook.close()
        finally:
            pass


def to_file(xls_name, inlist, header_list=None, title="Title", shname="sheet1", wrap=False):
    assert "str" in repr(type(xls_name))
    exfile = Exfile(xls_name)
    if header_list:
        assert header_list.extend
        if hasattr(inlist, "to_records"):
            inlist = list(inlist.to_records())
        if hasattr(inlist, "tolist"):
            inlist = inlist.tolist()

        inlist.insert(0, header_list)
    exfile.write(inlist, title, shname, wrap=wrap)
    try:
        exfile.save()
    except:
        error_str = repr(sys.exc_info()).lower()
        if "permission" in error_str:
            print("!-File probably opened", error_str)
            sys.exit()


def generate_random_data(num_rows=10):
    import random
    import string
    from datetime import datetime, timedelta

    unicode_ranges = [
        (0x0020, 0x007E),  # Basic Latin (printable ASCII)
        (0x00A0, 0x00FF),  # Latin-1 Supplement (e.g., accented characters)
        (0x0100, 0x017F),  # Latin Extended-A (more European characters)
        # (0x0370, 0x03FF),  # Greek and Coptic
    ]

    def gen_datetime(min_year=1900, max_year=datetime.now().year):
        # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
        start = datetime(min_year, 1, 1, 00, 00, 00)
        years = max_year - min_year + 1
        end = start + timedelta(days=365 * years)
        return start + (end - start) * random.random()

    def get_random_unicode_char():
        """Get a random Unicode character from various language ranges."""
        range_start, range_end = random.choice(unicode_ranges)
        code_point = random.randint(range_start, range_end)
        try:
            return chr(code_point)
        except ValueError:
            return chr(random.randint(0x00C0, 0x00FF))

    header = ["col1", "col2", "col3", "col4", "col5", "col6"]

    result = [header]
    for _ in range(num_rows):
        row = [
            random.choice(string.ascii_letters),
            random.randint(100, 100000),
            random.uniform(-1, 1),
            get_random_unicode_char(),
            random.choice([True, False]),
            str(gen_datetime()),
        ]
        result.append(row)

    return result


def test_numpy():
    from numpy.random import default_rng
    arr = default_rng(42).random((100, 4))
    header = ["col1", "col2", "col3", "col4"]
    to_file("test.xlsx", arr, header, title="Test numpy")


def test_df():
    import numpy as np
    import pandas as pd

    df = pd.DataFrame({
        "col1": ["A", "A", False, np.nan, "D", "C"],
        "col2": [2, 1, 9, -8, 7, -4],
        "col3": [-0.8, 1, 9, 4, 2, 3],
        "col4": ["a", "B", "c", "D", True, "F"],
    })
    df = list(range(100))
    to_file("testdf.xlsx", df, title="Test dataframe")


def test_1d():
    r = list(range(100))
    to_file("simplelist.xlsx", r, title="Simple list")


if __name__ == "__main__":
    test_df()
