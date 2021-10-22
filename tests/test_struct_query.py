#######################################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#######################################################################################

# This file provides unit tests for the "query()" method which allows safely digging
# into an arbitrarily nested structure of python lists and dictionaries (as one might have
# after converting JSON to python lists/dicts)
#
# To run this test, execute it from the parent directory where your lambda code under test resides:
#   python -m pytest tests/*.py
#
# References:
#   https://docs.pytest.org/en/stable/index.html

import json
import sys

import pytest

sys.path.append("code")
from structure import query


class TestStructQuery():
    def test_simple(self):
        assert(query({"1" : 'a', "2" : 'b'}, ".1") == 'a')
    def test_default(self):
        assert(query({"1" : 'a', "2" : 'b'}, ".ZZZ") == None)
    def test_new_default(self):
        assert(query({"1" : 'a', "2" : 'b'}, ".ZZZ", 'new default') == 'new default')
    def test_deeper_new_default(self):
        struct = {"1" : {'a':'42'}, "2" : 'b'}
        assert(query(struct, ".1.a", ) == '42')
        assert(query(struct, ".1.ZZZ") == None)
    def test_list_ok_0(self):
        assert(query(['zero', 'one'], "[0]") == 'zero')
    def test_dict_ok_0(self):
        struct = {"first_key" : {'nested_key' : '42'}, "second_key" : [ 10, 20, 30 ] }
        assert query(struct, ".first_key.nested_key" ) == '42'
        assert query(struct, ".second_key[2]" ) == 30
    def test_dict_ok_1(self):
        assert(query({"1" : ['zero', 'one']}, ".1[0]") == 'zero')
    def test_dict_ok_2(self):
        assert(query({"1" : ['zero', 'one']}, ".1[1]") == 'one')
    def test_dict_ok_3(self):
        assert(query({"1" : 'one'}, ".1") == 'one')
    def test_dict_ok_4(self):
        assert(query({"1" : 'one'}, ".1") == 'one')
    def test_dict_ok_5(self):
        assert(query({1 : 'one_as_int'}, ".1") == 'one_as_int')
    def test_list_bad_index(self):
        assert(query({"1" : ['zero', 'one']}, ".1[2]") == None)
    def test_empty_search_string(self):
        with pytest.raises(ValueError):
            res = query({"1" : 'a'}, "")
    def test_list_bad_negative_index_1(self):
        with pytest.raises(ValueError):
            res = query(['zero', 'one'], "[-1]")
    def test_list_bad_negative_index_2(self):
        with pytest.raises(ValueError):
            res = query({"1" : ['zero', 'one']}, ".1[-1]")
    def test_bad_nonlist_argument(self):
        with pytest.raises(TypeError):
            res = query({}, ["bad 2nd argument... should be a string type"])
