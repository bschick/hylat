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

import sys
import argparse
import json
import numpy as np
import traceback
from random import shuffle


def make_teams(args, lines):

    if args.verbose:
        dump_plan(args)
        print(f'\n~~~~ Distributing ~~~~')

    parents = []
    kids = []

    try:
        for i, family in enumerate(lines):
            if not isinstance(family, str):
                raise ValueError('Contains unreadable characters')
            family = family.strip()
            if len(family) < 2 or family[0] == '#':
                continue

            try:
                pstr, kstr = family.split(':')
            except:
                raise ValueError(f'Line {i+1} has {family.count(":")} ":" separators, each line must have one')

            pstr = pstr.strip()
            if pstr:
                # iter(lambda:i, -1) is an iterator that returns i forever when i > 0
                ptuples = zip([s.strip() for s in pstr.split(',')], iter(lambda:i, -1))
                parents.extend(ptuples)
            kstr = kstr.strip()
            if kstr:
                ktuples = zip([s.strip() for s in kstr.split(',')], iter(lambda:i, -1))
                kids.extend(ktuples)
    except ValueError as verr:
        usage_error(f'Could not read family data. {verr}')
    except Exception as ex:
        usage_error(f'Could not read family data.')


    kid_count = len(kids)
    parent_count = len(parents)

    if args.verbose:
        print(f'{kid_count} kids and {parent_count} parents')

    if kid_count + parent_count < args.size:
        usage_error(f'Team size of {args.size} is larger than the total number of people, which is {kid_count + parent_count}')

    num_teams = (kid_count + parent_count) // args.size

    if (kid_count + parent_count) != num_teams * args.size:
        if not args.inexact:
            usage_error(f"Cannot create teams of {args.size} with {kid_count + parent_count} people, consider using -u option")
        else:
            num_teams += 1

    retry = True
    count = 0
    teams = []

    # need to make this better than brute force someday
    while retry:
        teams = []
        shuffle(parents)
        shuffle(kids)

        if args.generations:
            # put kids first so parent teams are smaller when inexact (due to how np.array_split works)
            merged = kids + parents
            teams = np.array_split(merged, num_teams)
        else:
            psplit = np.array_split(parents, num_teams)
            ksplit = np.array_split(kids, num_teams)
            ksplit.reverse()
            for i in range(num_teams):
                teams.append(np.concatenate([psplit[i], ksplit[i]]))

        retry = False
        if not args.oktogether: 
            for t in teams:
                fams = np.take(t, 1, 1)
                if len(np.unique(fams, return_counts=True)[1]) != len(t):                
                    count += 1
                    retry = True
                    if args.verbose > 1:
                        print(f'try {count:,} failed due to conflict {list(np.take(t, 0, 1))}')
                    break
        
        if count == args.tries:
            usage_error(f'Did not create valid teams in {count:,} attempts, consider using -o or -t options')


    if args.verbose:
        print(f'\n~~~~ Results ({num_teams} team{"s" if num_teams > 1 else ""})~~~~')

    # take doesn't work with inhomogeneous shape arrays, so loop
    out_teams = []
    for t in teams:
        out_teams.append(np.take(t, 0, 1))

    if args.json:
        return json.dumps([t.tolist() for t in out_teams]) 
    else:
        result = []
        for t in out_teams:
            result.append(args.separator.join(t))
        return '\n'.join(result)


def usage_error(msg):
    raise ValueError(msg)


def dump_plan(args):
    print(f'~~~~ Plan ~~~~')
    size_msg = "approximately" if args.inexact else "exactly"
    print(f'team sizes of {size_msg} {args.size:,}')

    together_msg = "allowed together" if args.oktogether else "kept apart"
    print(f'family memebers {together_msg}')

    gen_msg = "compete" if args.generations else "mixed"
    print(f'parents and kids {gen_msg}')

    if not args.oktogether and args.verbose > 1:
        print(f'maximum of {args.tries:,} tries to create valid teams')

    if args.verbose > 1:
        if args.json:
            print(f'json output')
        else:
            print(f'plain text output with "{args.separator}" separator')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create teams from a file listing families of parents and kids (or other people groupings)')
    parser.add_argument('family_file', type=str, help='file containing list of families')
    parser.add_argument('-o', '--oktogether', required=False, action='store_true', help='do not force family members to be on different teams')
    parser.add_argument('-g', '--generations', required=False, action='store_true', help='try to create teams of the same generation (parents v kids)')
    parser.add_argument('-s', '--size', required=False, default=2, type=int, help='team size (default is 2)')
    parser.add_argument('-t', '--tries', required=False, default=10000, type=int, help='maximum number of attempts to create valid teams (default is 10,000)')
    parser.add_argument('-i', '--inexact', required=False, action='store_true', help='try to match team size, but allow smaller or uneven team sizes')
    parser.add_argument('-v', '--verbose', action="count", default=0, help='display more progress information')
    parser.add_argument('-j', '--json', action='store_true', help='output in json')
    parser.add_argument('-p', '--separator', required=False, help="separator between team members in printout (default is ' - ')")
    args = parser.parse_args()

    if args.json and args.separator is not None:
        usage_error('Cannot specify seperator for json output')

    if args.separator is None:
        args.separator = ' - '

    try:
        with open(args.family_file, 'r') as people:
            try:
                result = make_teams(args, people.readlines())
                print(result)
            except UnicodeDecodeError as uerr:
                print(f'Could not open or load. Contains unreadable characters\n  hylat.py -h for help')
                sys.exit(1)
            except ValueError as verr:
#                traceback.print_exc()
                print(f'{str(verr)}\n  hylat.py -h for help')
                sys.exit(1)
    except Exception as ex:
#        traceback.print_exc()
        print(f'Could not open or load "{args.family_file}". {ex}')
        sys.exit(2)
