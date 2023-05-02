#! /usr/bin/env python3

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
            family = family.strip()
            if len(family) < 2 or family[0] == '#':
                continue

            pstr, kstr = family.split(':')
            pstr = pstr.strip()
            if pstr:
                ptuples = zip([s.strip() for s in pstr.split(',')], (i for _ in range(999)))
                parents.extend(ptuples)
            kstr = kstr.strip()
            if kstr:
                ktuples = zip([s.strip() for s in kstr.split(',')], (i for _ in range(999)))
                kids.extend(ktuples)
    except Exception as ex:
        usage_error(f'could not read family data. {ex}')


    kid_count = len(kids)
    parent_count = len(parents)

    if args.verbose:
        print(f'{kid_count} kids and {parent_count} parents')

    if kid_count + parent_count < args.size:
        usage_error(f'team size of {args.size} is larger than the total number of people, which is {kid_count + parent_count}')

    num_teams = (kid_count + parent_count) // args.size

    if (kid_count + parent_count) != num_teams * args.size:
        if not args.uneven:
            usage_error(f"cannot create teams of {args.size} with {kid_count + parent_count} people, consider using -u option")
        else:
            num_teams += 1

    retry = True
    count = 0

    # need to make this better than brute force since this can loop forever
    while retry:
        teams = []
        shuffle(parents)
        shuffle(kids)

        if args.generations:
            # put kids first so parent teams are smaller when uneven (due to how np.array_split works)
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
            usage_error(f'did not create valid teams in {count:,} attempts, consider using -o or -t options')


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
    size_msg = "approximately" if args.uneven else "exactly"
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
    parser.add_argument('-t', '--tries', required=False, default=10000, type=int, help='maximum number of attempts to create valid teams before giving up (default is 10,000)')
    parser.add_argument('-u', '--uneven', required=False, action='store_true', help='try to match team sizes, but allow smaller teams or uneven teams')
    parser.add_argument('-v', '--verbose', action="count", help='display more progress information')
    parser.add_argument('-j', '--json', action='store_true', help='output in json')
    parser.add_argument('-p', '--separator', required=False, help="separator between team members in printout (default is ' - ')")
    args = parser.parse_args()

    if args.json and args.separator is not None:
        usage_error('cannot specify seperator for json output')

    if args.separator is None:
        args.separator = ' - '

    try:
        with open(args.family_file, 'r') as people:
            try:
                result = make_teams(args, people.readlines())
            except ValueError as verr:
                print(f'{str(verr)}\n  hylat.py -h for help')
                sys.exit(1)
        print(result)
    except Exception as ex:
#        traceback.print_exc(ex)
        print(f'could not open or load {sys.argv[1]}. {ex}')
        sys.exit(2)
