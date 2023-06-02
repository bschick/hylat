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

from context import hylat
import pytest
import json
import numpy as np



def results_helper(args, results, members_start_with, drop_count):
    members_per_team = [len(members) for members in members_start_with]
    assert drop_count == results['drop_count']
    assert results['player_count'] == sum(members_per_team)

    cats = np.unique(np.hstack(members_start_with))
    if cats[0] != '*':
        assert len(cats) == results['category_count']

    if args.json:
        return results_helper_json(args, results, members_start_with, members_per_team)
    else:
        return results_helper_text(args, results, members_start_with, members_per_team)

def results_helper_json(args, results, members_start_with, members_per_team):
    json_results = json.loads(results['teams'])
    team_count = len(json_results)

    assert team_count == results['team_count']
    assert team_count == len(members_per_team)

    for l, members in enumerate(json_results):
        assert len(members) == members_per_team[l]
        check_members(args, members, members_start_with[l])


def results_helper_text(args, results, members_start_with, members_per_team):
    team_lines = results['teams'].splitlines(keepends=False)
    team_count = len(team_lines)

    assert team_count == results['team_count']
    assert team_count == len(members_per_team)

    for l, line in enumerate(team_lines):
        members = line.split(args.separator)
        assert len(members) == members_per_team[l]
        check_members(args, members, members_start_with[l])


def check_members(args, members, members_start_with):
    split_members = [m.strip().split('_') for m in members]
    fams = np.take(split_members, 2, 1)
    print(fams)

    if not args.oktogether:
        assert len(np.unique(fams, return_counts=True)[1]) == len(members), "family members should not be together on the same team"

    for m, start in enumerate(members_start_with):
        if start != '*':
            print(f'{members[m]} starts with {start}')
            assert members[m].startswith(start), "unexpected members type on team"


def test_example():
    args = hylat.default_args()
    args.teamsize = 2

    with open('../people.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    team_lines = results['teams'].splitlines(keepends=False)
    team_count = len(team_lines)

    assert team_count == 10
    assert team_count == results['team_count']
    assert results['player_count'] == 20
    assert results['category_count'] == 2
    assert results['drop_count'] == 0


def test_default():
    args = hylat.default_args()
    args.teamsize = 2

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(7)]
    members_start_with += [['Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)

def test_default_extra():
    args = hylat.default_args()
    args.teamsize = 2

    with open('good_testE1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(7)]
    members_start_with += [['Kid', 'Extra'] for _ in range(2)]
    members_start_with += [['Kid', 'Kid'] for _ in range(1)]
    results_helper(args, results, members_start_with, 0)

def test_extra_gen():
    args = hylat.default_args()
    args.teamsize = 2
    args.generations = True

    with open('good_testE1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Parent'] for _ in range(3)]
    members_start_with += [['Parent', 'Kid'] for _ in range(1)]
    members_start_with += [['Kid', 'Kid'] for _ in range(5)]
    members_start_with += [['Extra', 'Extra'] for _ in range(1)]
    results_helper(args, results, members_start_with, 0)


def test_extra_uneven():
    for r in ['closest', 'down']:
        args = hylat.default_args()
        args.teamsize = 2
        args.uneven = True
        args.round = r

        with open('good_testE2.txt', 'r') as people:
            results = hylat.teams_from_list(args, people.readlines())

        members_start_with = [['Parent', 'Kid', 'Kid'] for _ in range(1)]
        members_start_with += [['Parent', 'Kid'] for _ in range(6)]
        members_start_with += [['Kid', 'Extra'] for _ in range(3)]
        results_helper(args, results, members_start_with, 0)

def test_extra_uneven_up():
    args = hylat.default_args()
    args.teamsize = 2
    args.uneven = True
    args.round = 'up'

    with open('good_testE2.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(7)]
    members_start_with += [['Kid', 'Extra'] for _ in range(3)]
    members_start_with += [['Kid'] for _ in range(1)]
    results_helper(args, results, members_start_with, 0)

def test_extra_big():
    args = hylat.default_args()
    args.teamsize = 2

    with open('good_testE3.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['C1', 'C3'] for _ in range(3)]
    members_start_with += [['C1', 'C4'] for _ in range(2)]
    members_start_with += [['C2', 'C4'] for _ in range(3)]
    members_start_with += [['C2', 'C5'] for _ in range(2)]
    members_start_with += [['C3', 'C5'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)

def test_extra_big_gen():
    args = hylat.default_args()
    args.teamsize = 2
    args.generations = True

    with open('good_testE3.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['C1', 'C1'] for _ in range(2)]
    members_start_with += [['C1', 'C2'] for _ in range(1)]
    members_start_with += [['C2', 'C2'] for _ in range(2)]
    members_start_with += [['C3', 'C3'] for _ in range(2)]
    members_start_with += [['C3', 'C4'] for _ in range(1)]
    members_start_with += [['C4', 'C4'] for _ in range(2)]
    members_start_with += [['C5', 'C5'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)


def test_extra_big_tcount3():
    args = hylat.default_args()
    args.teamcount = 3
    args.oktogether = True

    with open('good_testE3.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['C1', 'C2', 'C2', 'C3', 'C3', 'C4', 'C5', 'C5'] for _ in range(1)]
    members_start_with += [['C1', 'C1', 'C2', 'C3', 'C3', 'C4', 'C4', 'C5'] for _ in range(1)]
    members_start_with += [['C1', 'C1', 'C2', 'C2', 'C3', 'C4', 'C4', 'C5'] for _ in range(1)]
    results_helper(args, results, members_start_with, 0)


def test_default_str():
    args = hylat.default_args()
    args.teamsize = 2

    with open('good_test1.txt', 'r') as people:
        content = people.read()

    results = hylat.teams_from_str(args, content)

    members_start_with = [['Parent', 'Kid'] for _ in range(7)]
    members_start_with += [['Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)


def test_default_wrapped_str():
    args = hylat.default_args()
    args.teamsize = 2

    with open('good_test1.txt', 'r') as people:
        content = people.read()

    # wrapped cataches errors and returns them in json (should have none)
    results = hylat.wrapped_teams_from_str(args, content)
    assert results.get('error', None) is None

    members_start_with = [['Parent', 'Kid'] for _ in range(7)]
    members_start_with += [['Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)


def test_default_wrapped_str_error():
    args = hylat.default_args()
    args.teamsize = 4

    with open('good_test1.txt', 'r') as people:
        content = people.read()

    # wrapped cataches errors and returns them in json (should get one)
    results = hylat.wrapped_teams_from_str(args, content)
    assert results['error'].startswith('Cannot create teams of exactly 4')


def test_default_json():
    args = hylat.default_args()
    args.teamsize = 2
    args.json = True

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(7)]
    members_start_with += [['Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)

def test_teamcount3():
    args = hylat.default_args()
    args.teamcount = 3

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Parent', 'Kid', 'Kid', 'Kid', 'Kid'] for _ in range(2)]
    members_start_with += [['Parent', 'Parent', 'Parent', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    results_helper(args, results, members_start_with, 0)

def test_teamcount9():
    args = hylat.default_args()
    args.teamcount = 9

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(7)]
    members_start_with += [['Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)


def test_teamsize3():
    args = hylat.default_args()
    args.teamsize = 3

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid', 'Kid'] for _ in range(5)]
    members_start_with += [['Parent', 'Parent', 'Kid'] for _ in range(1)]
    results_helper(args, results, members_start_with, 0)

def test_teamsize6_json():
    # this one can take 100+ tries
    args = hylat.default_args()
    args.teamsize = 6
    args.json = True

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Parent', 'Kid', 'Kid', 'Kid', 'Kid'] for _ in range(2)]
    members_start_with += [['Parent', 'Parent', 'Parent', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    results_helper(args, results, members_start_with, 0)

def test_kids_only():
    args = hylat.default_args()
    args.teamsize = 2

    with open('good_test4.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Kid', 'Kid'] for _ in range(5)]
    results_helper(args, results, members_start_with, 0)

def test_kids_only2():
    args = hylat.default_args()
    args.teamcount = 3
    args.oktogether = True
    args.uneven = True

    with open('good_test4.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Kid', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    members_start_with += [['Kid', 'Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)

def test_fail_teamsize_too_big():
    args = hylat.default_args()
    args.teamsize = 12
    args.oktogether = True

    with open('good_test2.txt', 'r') as people:
        with pytest.raises(ValueError):
            results = hylat.teams_from_list(args, people.readlines())

def test_fail_teamsize_too_big2():
    args = hylat.default_args()
    args.teamsize = 7
    args.oktogether = True
    args.uneven = True

    with open('good_test2.txt', 'r') as people:
        with pytest.raises(ValueError):
            results = hylat.teams_from_list(args, people.readlines())


def test_fail_teamcount_too_big():
    args = hylat.default_args()
    args.teamcount = 7
    args.oktogether = True
    args.drop = True

    with open('good_test2.txt', 'r') as people:
        with pytest.raises(ValueError):
            results = hylat.teams_from_list(args, people.readlines())


def test_teamsize6_gen_oktogether_uneven():
    # this one can take 100+ tries
    args = hylat.default_args()
    args.teamsize = 6
    args.oktogether = True
    args.generations = True
    args.uneven = True # should do nothing in this test

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Parent', 'Parent', 'Parent', 'Parent', 'Parent'] for _ in range(1)]
    members_start_with += [['Parent', 'Kid', 'Kid', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    members_start_with += [['Kid', 'Kid', 'Kid', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    results_helper(args, results, members_start_with, 0)

    args = hylat.default_args()
    args.teamsize = 6
    args.oktogether = True
    args.generations = True
    args.uneven = False # should do nothing in this test
    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    results_helper(args, results, members_start_with, 0)


def test_oktogether():
    args = hylat.default_args()
    args.teamsize = 2
    args.oktogether = True

    # test2 cannot produce teams of 2 without oktogether
    with open('good_test2.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(3)]
    results_helper(args, results, members_start_with, 0)

def test_oktogether_teamcount():
    args = hylat.default_args()
    args.teamcount = 3
    args.oktogether = True

    # test2 cannot produce teams of 2 without oktogether
    with open('good_test2.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid'] for _ in range(3)]
    results_helper(args, results, members_start_with, 0)

def test_oktogether_teamcount6():
    args = hylat.default_args()
    args.teamcount = 6
    args.oktogether = True

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid', 'Kid'] for _ in range(5)]
    members_start_with += [['Parent', 'Parent', 'Kid'] for _ in range(1)]
    results_helper(args, results, members_start_with, 0)


def test_fail_not_oktogether():
    args = hylat.default_args()
    args.teamsize = 2
    args.oktogether = False
    args.tries = 1000

    # test2 cannot produce teams of 2 without oktogether
    with open('good_test2.txt', 'r') as people:
        with pytest.raises(ValueError):
            results = hylat.teams_from_list(args, people.readlines())


def test_pvk():
    args = hylat.default_args()
    args.teamsize = 2
    args.generations = True

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Parent'] for _ in range(3)]
    members_start_with += [['Parent', 'Kid'] for _ in range(1)]
    members_start_with += [['Kid', 'Kid'] for _ in range(5)]
    results_helper(args, results, members_start_with, 0)

def test_1longcat():
    args = hylat.default_args()
    args.teamsize = 25

    with open('good_test5.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Kid']*25 for _ in range(2)]
    results_helper(args, results, members_start_with, 0)

def test_uneven1():
    for r in ['closest', 'down']:
        args = hylat.default_args()
        args.teamsize = 4
        args.uneven = True

        args.round = r
        with open('good_test1.txt', 'r') as people:
            results = hylat.teams_from_list(args, people.readlines())

        members_start_with = [['Parent', 'Parent', 'Kid', 'Kid', 'Kid'] for _ in range(2)]
        members_start_with += [['Parent', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
        members_start_with += [['Parent', 'Parent', 'Kid', 'Kid'] for _ in range(1)]
        results_helper(args, results, members_start_with, 0)

    args = hylat.default_args()
    args.teamsize = 4
    args.uneven = True
    args.round = 'up'
    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    members_start_with += [['Parent', 'Parent', 'Kid', 'Kid'] for _ in range(2)]
    members_start_with += [['Parent', 'Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)

def test_uneven2():
    args = hylat.default_args()
    args.teamsize = 4
    args.uneven = True
    args.round = 'up'

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['Parent', 'Kid', 'Kid', 'Kid'] for _ in range(1)]
    members_start_with += [['Parent', 'Parent', 'Kid', 'Kid'] for _ in range(2)]
    members_start_with += [['Parent', 'Kid', 'Kid'] for _ in range(2)]
    results_helper(args, results, members_start_with, 0)

def test_drop():
    args = hylat.default_args()
    args.teamsize = 4
    args.drop = True
    
    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    # since drops are random, cannot predict exect output
    members_start_with = [['*', '*', '*', '*'] for _ in range(4)]
    results_helper(args, results, members_start_with, 2)

def test_small_drop():
    args = hylat.default_args()
    args.teamcount = 2
    args.drop = True

    with open('good_test3.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['*'] for _ in range(2)]
    results_helper(args, results, members_start_with, 1)


def test_drop_teamcount():
    args = hylat.default_args()
    args.teamcount = 4
    args.drop = True

    with open('good_test1.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    # since drops are random, cannot predict exect output
    members_start_with = [['*', '*', '*', '*'] for _ in range(4)]
    results_helper(args, results, members_start_with, 2)

def test_fail_noteven():
    args = hylat.default_args()
    args.teamsize = 4

    with open('good_test1.txt', 'r') as people:
        with pytest.raises(ValueError):
            results = hylat.teams_from_list(args, people.readlines())


def test_fail_input():
    for fname in ('bad_test4.txt', 'bad_test6.txt'):
        do_fail_input(fname)


def do_fail_input(file_name):
    args = hylat.default_args()
    args.teamsize = 2
    args.uneven = True

    with open(file_name, 'r') as people:
        with pytest.raises(ValueError):
            results = hylat.teams_from_list(args, people.readlines())

def test_test_fail():
    args = hylat.default_args()
    args.teamsize = 2

    with open('bad_test3.txt', 'r') as people:
        results = hylat.teams_from_list(args, people.readlines())

    members_start_with = [['*', '*'] for _ in range(3)]
    # should detect family members gether on same team (see bad_test3.txt comment)
    with pytest.raises(AssertionError):
        results_helper(args, results, members_start_with, 2)


def test_fail_binary():
    args = hylat.default_args()
    args.teamsize = 2
    args.uneven = True
    args.oktogether = True

    with open('bad_test5.txt', 'rb') as people:
        with pytest.raises(ValueError):
            results = hylat.teams_from_list(args, people.read())
