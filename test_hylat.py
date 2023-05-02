#! /usr/bin/env python3
""" MIT License

Copyright (c) 2023 Brad Schick

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. """

import hylat
import pytest
import json
import numpy as np

class Args:
    # init with default values
    def __init__(self):
        self.oktogether = False
        self.generations = False
        self.size = 2
        self.tries = 10000
        self.inexact = False
        self.verbose = 0
        self.json = False
        self.separator = ' - '


def results_helper(args, results, members_start_with):
    if args.json:
        return results_helper_json(args, results, members_start_with)
    else:
        return results_helper_text(args, results, members_start_with)

def results_helper_json(args, results, members_start_with):
    json_results = json.loads(results)
    team_count = len(json_results)

    members_per_team = [len(members) for members in members_start_with]
    print(f'{len(json_results)} {json_results}')
    assert team_count == len(members_per_team)

    for l, members in enumerate(json_results):
        assert len(members) == members_per_team[l]
        check_members(args, members, members_start_with[l])


def results_helper_text(args, results, members_start_with):
    members_per_team = [len(members) for members in members_start_with]
    team_lines = results.splitlines(keepends=False)
    print(members_per_team)
    assert len(team_lines) == len(members_per_team)

    for l, line in enumerate(team_lines):
        members = line.split(args.separator)
        assert len(members) == members_per_team[l]
        check_members(args, members, members_start_with[l])


def check_members(args, members, members_start_with):
    split_members = [m.strip().split('_') for m in members]
    fams = np.take(split_members, 2, 1)
    print(fams)

    if not args.oktogether:
        assert len(np.unique(fams, return_counts=True)[1]) == len(members), "number of uniques families is < number of members"

    for m, start in enumerate(members_start_with):
        assert members[m].startswith(start)


def test_default():
    args = Args()

    with open('test1.txt', 'r') as people:
        results = hylat.make_teams(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(7)]
    members_start_with += [['Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with)


def test_default_json():
    args = Args()
    args.json = True

    with open('test1.txt', 'r') as people:
        results = hylat.make_teams(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(7)]
    members_start_with += [['Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with)


def test_size3():
    args = Args()
    args.size = 3

    with open('test1.txt', 'r') as people:
        results = hylat.make_teams(args, people.readlines())

    members_start_with = [['Parent', 'Parent', 'Kid'] for _ in range(1)]
    members_start_with += [['Parent', 'Kid', 'Kid'] for _ in range(5)]
    results_helper(args, results, members_start_with)

def test_size6_json():
    # this one can take 100+ tries
    args = Args()
    args.size = 6
    args.json = True

    with open('test1.txt', 'r') as people:
        results = hylat.make_teams(args, people.readlines())

    members_start_with = [['Parent', 'Parent', 'Parent', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    members_start_with += [['Parent', 'Parent', 'Kid', 'Kid', 'Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with)

def test_fail_size_too_big():
    args = Args()
    args.size = 12

    with open('test2.txt', 'r') as people:
        with pytest.raises(ValueError):
            results = hylat.make_teams(args, people.readlines())


def test_size6_gen_oktogether_inexact():
    # this one can take 100+ tries
    args = Args()
    args.size = 6
    args.oktogether = True
    args.generations = True
    args.inexact = True # should do nothing in this test

    with open('test1.txt', 'r') as people:
        results = hylat.make_teams(args, people.readlines())

    members_start_with = [['Kid', 'Kid', 'Kid', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    members_start_with += [['Kid', 'Kid', 'Kid', 'Kid', 'Kid', 'Parent'] for _ in range(1)]
    members_start_with += [['Parent', 'Parent', 'Parent', 'Parent', 'Parent', 'Parent'] for _ in range(1)]
    results_helper(args, results, members_start_with)

    args.inexact = False # should do nothing in this test
    with open('test1.txt', 'r') as people:
        results = hylat.make_teams(args, people.readlines())

    results_helper(args, results, members_start_with)


def test_oktogether():
    args = Args()
    args.oktogether = True

    # test2 cannot produce teams of 2 without oktogether
    with open('test2.txt', 'r') as people:
        results = hylat.make_teams(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(3)]
    results_helper(args, results, members_start_with)


def test_fail_not_oktogether():
    args = Args()
    args.oktogether = False
    args.tries = 1000

    # test2 cannot produce teams of 2 without oktogether
    with open('test2.txt', 'r') as people:
        with pytest.raises(ValueError):
            results = hylat.make_teams(args, people.readlines())


def test_pvk():
    args = Args()
    args.generations = True

    # test2 cannot produce teams of 2 without oktogether
    with open('test1.txt', 'r') as people:
        results = hylat.make_teams(args, people.readlines())

    members_start_with = [['Kid', 'Kid'] for _ in range(5)]
    members_start_with += [['Kid', 'Parent'] for _ in range(1)]
    members_start_with += [['Parent', 'Parent'] for _ in range(3)]
    results_helper(args, results, members_start_with)


def test_inexact():
    args = Args()
    args.size = 4
    args.inexact = True

    # test2 cannot produce teams of 2 without oktogether
    with open('test1.txt', 'r') as people:
        results = hylat.make_teams(args, people.readlines())

    members_start_with = [['Parent', 'Parent', 'Kid', 'Kid'] for _ in range(2)]
    members_start_with += [['Parent', 'Kid', 'Kid'] for _ in range(2)]
    members_start_with += [['Parent', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    results_helper(args, results, members_start_with)


def test_fail_noteven():
    args = Args()
    args.size = 4

    with open('test1.txt', 'r') as people:
        with pytest.raises(ValueError):
            results = hylat.make_teams(args, people.readlines())
