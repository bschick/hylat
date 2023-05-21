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
from random import shuffle, randrange
from math import floor, ceil

def lp(msg):
    print(msg)

def teams_from_str(args, lines):
    return teams_from_list(args, lines.split('\n'))

# normalize_args function must be called first
def teams_from_list(args, lines):

    assert args.teamsize >= 0
    assert args.teamcount >= 0

    if args.verbose:
        dump_plan(args)
        lp(f'\n~~~~ Distributing ~~~~')

    parents = []
    kids = []

    if args.round == 'closest':
        rounder = round
    elif args.round == 'down':
        rounder = floor
    else:
        rounder = ceil

    try:
        for i, family in enumerate(lines):
            if not isinstance(family, str):
                raise ValueError('Contains unreadable characters')
            family = family.strip()
            if len(family) < 2 or family[0] == '#':
                continue

            categories = family.split(':')
            cat_count = len(categories)

            if cat_count == 1:
                pstr, kstr = '', family
            elif cat_count == 2:
                pstr, kstr = categories
            else:
                raise ValueError(f'Line {i+1} has {cat_count} ":" separators, each line must have one or none')

            pstr = pstr.strip()
            if pstr:
                # iter(lambda:i, -1) is an iterator that returns i forever when i >= 0
                ptuples = zip([s.strip() for s in pstr.split(',') if s.strip()], iter(lambda:i, -1))
                parents.extend(ptuples)
            kstr = kstr.strip()
            if kstr:
                ktuples = zip([s.strip() for s in kstr.split(',') if s.strip()], iter(lambda:i, -1))
                kids.extend(ktuples)
    except ValueError as verr:
        usage_error(f'Could not read family data. {verr}')
    except Exception as ex:
        usage_error(f'Could not read family data.')


    kid_count = len(kids)
    parent_count = len(parents)
    people_count = kid_count + parent_count

    if args.verbose:
        lp(f'{people_count} people: {kid_count} kids and {parent_count} parents')

    # common error checking
    if args.teamsize > 0 and args.teamsize > people_count:
        usage_error(f'Team size of {args.teamsize} is larger than the total number of people, which is {people_count}')

    if args.teamcount > 0 and args.teamcount > people_count:
        usage_error(f'Team count of {args.teamcount} is larger than the total number of people, which is {people_count}')

    drop_count = 0
    if args.uneven:
        if args.teamsize > 0:
            # could add params that specify rounding direction (this uses python's banker rounding)
            team_count = rounder(people_count / args.teamsize)
        else:
            assert args.teamcount > 0
            team_count = args.teamcount
    elif args.drop:
        if args.teamsize > 0:
            team_count = people_count // args.teamsize
            team_size = args.teamsize
        else:
            assert args.teamcount > 0
            team_count = args.teamcount
            team_size = people_count // team_count

        drop_count = people_count - (team_size * team_count)
    else:
        if args.teamsize > 0:
            if people_count % args.teamsize > 0:
                usage_error(f"Cannot create teams of exactly {args.teamsize} from {people_count} people, consider using --uneven or --drop option")
            team_count = people_count // args.teamsize
        else:
            assert args.teamcount > 0
            if people_count % args.teamcount > 0:
                usage_error(f"Cannot create {args.teamcount} even teams from {people_count} people, consider using --uneven or --drop option")
            team_count = args.teamcount

    if team_count == 1:
        usage_error('Inputs would result in only 1 team')


    # Needed because during drop parents or kids can be empty, and the dimensions get lost
    parents = np.array(parents).reshape((-1,2))
    kids = np.array(kids).reshape((-1,2))

    # make copies for redropping (below)
    parents_orig = parents.copy()
    kids_orig = kids.copy()

    # can end up dropping people that make it impossible to create valid teams, so retry
    # the drop every 10% of the retry count
    drop_step = min(ceil(args.tries / 10), 100)
    retry = True
    count = 0
    teams = []
    rng = np.random.default_rng()

    # need to make this better than brute force someday
    while retry:

        if drop_count and count % drop_step == 0:
            parents, kids = do_drop(parents_orig, kids_orig, drop_count, args.verbose)

        teams = []
        rng.shuffle(parents)
        rng.shuffle(kids)

        if args.generations:
            # put kids first so parent teams are smaller when uneven (due to how np.array_split works)
            merged = np.concatenate((kids, parents))
            teams = np.array_split(merged, team_count)
        else:
            psplit = np.array_split(parents, team_count)
            ksplit = np.array_split(kids, team_count)
            ksplit.reverse()
            for i in range(team_count):
                team = np.concatenate((psplit[i], ksplit[i]))
                teams.append(team)

        retry = False
        if not args.oktogether: 
            for t in teams:
                fams = np.take(t, 1, 1)
                if len(np.unique(fams, return_counts=True)[1]) != len(t):                
                    count += 1
                    retry = True
                    if args.verbose > 1:
                        lp(f'try {count:,} failed due to conflict {list(np.take(t, 0, 1))}')
                    break

        if count == args.tries:
            usage_error(f'Did not create valid teams in {count:,} attempts, consider using --oktogether or --tries options')


    if args.verbose:
        lp(f'\n~~~~ Results ({team_count} team{"s" if team_count > 1 else ""}). Took {count+1} tries~~~~')

    # take doesn't work with inhomogeneous shape arrays, so loop
    out_teams = []
    for t in teams:
        out_teams.append(np.take(t, 0, 1))

    # Result is a dict, the teams value it either a plain string of team of a json string
    result = { 'team_count' : team_count, 'player_count': people_count - drop_count, 'drop_count': drop_count }
    if args.json:
        result['teams'] = json.dumps([t.tolist() for t in out_teams])
    else:
        team_list = []
        for t in out_teams:
            team_list.append(args.separator.join(t))
        result['teams'] = '\n'.join(team_list)

    return result


def do_drop(parents, kids, drop_count, verbose):
    parent_count = len(parents)
    kid_count = len(kids)
    people_count = parent_count + kid_count
    if drop_count > 0:
        if verbose:
            lp(f'(re)dropping {drop_count} {"people" if drop_count > 1 else "person"}')
        for i in range(drop_count):
            drop = randrange(0, people_count)
            people_count -= 1
            if drop > kid_count -1:
                parents = np.delete(parents, drop - kid_count, 0)
                parent_count -= 1
            else:
                kids = np.delete(kids, drop, 0)
                kid_count -= 1

        if verbose:
            lp(f'{people_count} people remaining: {kid_count} kids and {parent_count} parents')

    return (parents, kids)

def usage_error(msg):
    raise ValueError(msg)


def dump_plan(args):
    lp(f'~~~~ Plan ~~~~')
    if args.teamsize > 0:
        size_msg = "about" if args.uneven else "exactly"
        lp(f'team sizes of {size_msg} {args.teamsize:,}')
    else:
        lp(f'team count of {args.teamcount:,}')

    if args.drop:
        lp(f'drop extra people to make even teams')

    if args.teamsize > 0 and args.uneven:
        lp(f'round number of teams {"to " + args.round if args.round == "closest" else args.round}')

    gen_msg = "compete" if args.generations else "mixed"
    lp(f'parents and kids {gen_msg}')

    if not args.oktogether and args.verbose > 1:
        lp(f'maximum of {args.tries:,} tries to create valid teams')

    if args.verbose > 1:
        if args.json:
            lp(f'json output')
        else:
            lp(f'plain text output with "{args.separator}" separator')

# Note that this modified the passed in arg object
def normalize_args(args):
    if args.json and args.separator is not None:
        usage_error('Cannot specify seperator for json output')

    if (args.teamcount < 2 and args.teamcount != -999) or (args.teamsize < 2 and args.teamsize != -999):
        usage_error(f'Team size and count must be greater than 1')

    if args.teamcount > 0 and args.teamsize > 0:
        usage_error('Cannot specify both team size and count')

    if args.teamcount == -999:
        args.teamcount = 0
        if args.teamsize == -999:
            args.teamsize = 2
    if args.teamsize == -999:
        args.teamsize = 0

    if args.teamcount == 0 and args.teamsize == 0:
        args.teamsize = 2;

    if args.drop and args.uneven:
        usage_error('Can only specify --uneven or --drop, not both')

    if not args.separator:
        args.separator = ' - '

    if args.round != 'closest' and args.uneven != True and args.teamsize:
        usage_error('Rounding option only applies when used with --uneven and --teamsize')

class Args:
    # init with default values
    def __init__(self):
        self.oktogether = False
        self.generations = False
        self.teamsize = -999
        self.teamcount = -999
        self.tries = 10000
        self.uneven = False
        self.drop = False
        self.round = 'closest'
        self.verbose = 0
        self.json = False
        self.separator = None

def default_args():
    return Args()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create teams from a file listing families of parents and kids (or other people groupings)')
    parser.add_argument('family_file', type=str, help='file containing list of families')
    parser.add_argument('-o', '--oktogether', required=False, action='store_true', help='allow familes to be on the same team')
    parser.add_argument('-g', '--generations', required=False, action='store_true', help='try to create teams of the same generation (parents v kids)')
    parser.add_argument('-s', '--teamsize', required=False, default=-999, type=int, help='size of each team, must be more than 1 (default is 2)')
    parser.add_argument('-c', '--teamcount', required=False, default=-999, type=int, help='number of teams, must be more than 1')
    parser.add_argument('-t', '--tries', required=False, default=10000, type=int, help='maximum number of attempts to create valid teams (default is 10,000)')
    parser.add_argument('-d', '--drop', action='store_true', default=False, help='drop random extra people if teams are not even')
    parser.add_argument('-u', '--uneven', required=False, action='store_true', help='try to match team size, but allow uneven team sizes')
    parser.add_argument('-j', '--json', action='store_true', default=False, help='output in json')
    parser.add_argument('-r', '--round', default='closest', type=str, choices=['closest','down','up'], help='used with --uneven and --teamsize to round resulting number of teams down, up, or to closest even number (default is \'closest\')')
    parser.add_argument('-p', '--separator', required=False, help="separator between team members in printout (default is ' - ')")
    parser.add_argument('-v', '--verbose', action="count", default=0, help='display more progress information')
    args = parser.parse_args()

    try:
        with open(args.family_file, 'r') as people:
            try:
                normalize_args(args)
                result = teams_from_list(args, people.readlines())
                lp(result['teams'])
            except UnicodeDecodeError as uerr:
                lp(f'Could not read "{args.family_file}". Contains unreadable characters\n  hylat.py -h for help')
                sys.exit(1)
            except ValueError as verr:
#                traceback.print_exc()
                lp(f'{str(verr)}\n  hylat.py -h for help')
                sys.exit(1)
    except Exception as ex:
#        traceback.print_exc()
        lp(f'Could not open or load "{args.family_file}". {ex}')
        sys.exit(2)
