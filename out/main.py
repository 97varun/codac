from parsing import parse_input, Grammar, Rule, Parse
from rules import grammar
from inputs import *
from exec import generate_code
from copy import deepcopy
import json
import sys


def score(parse):
    scr = parse.rule.score
    for child in parse.children:
        if isinstance(child, Parse):
            scr += score(child)
    return scr


def score_parses(parses):
    for i in range(len(parses)):
        parses[i].semantics['score'] = score(parses[i])


def get_uniq_sems(transcript):
    parses = parse_input(grammar, transcript)
    if parses:
        score_parses(parses)
    else:
        return json.dumps({'input': transcript, 'error': 'Could not generate parse of the input'})
    parses.sort(key=lambda x: (x.semantics['score']),
                reverse=True)

    uniq_sems = []
    seen_sems = set()
    for parse in parses:
        sem_wo_score = deepcopy(parse.semantics)
        del sem_wo_score['score']
        sem_wo_score = tuple(sorted(sem_wo_score.items()))
        if sem_wo_score not in seen_sems:
            seen_sems.add(sem_wo_score)
            uniq_sems.append(parse.semantics)

    # post process semantics
    for i in range(len(uniq_sems)):
        if 'request' in uniq_sems[i] and\
           uniq_sems[i]['request'] == 'declare' and\
           'construct' not in uniq_sems[i]:
            uniq_sems[i]['construct'] = 'variable'

    return uniq_sems[:5]


def get_action(transcript, file, line):
    uniq_sems = get_uniq_sems(transcript)
    codes = generate_code(uniq_sems[:1], file, line)
    codes.insert(0, {'input': transcript})
    return json.dumps(codes)


if __name__ == "__main__":
    ips = [
        arr_ips, cond_ips, exp_ips, func_ips, func_param_ips,     # [0 - 4]
        # func_call_ips, f_c_printf_ips, f_c_scanf_ips,           # [5 - 7]
        init_ips, loop_ips, loop_init_ips, loop_cond_ips,         # [8 - 11]
        loop_update_ips, nav_ips, pack_ips, ptr_ips,              # [12 - 15]
        return_stmt_ips, var_ips, if_ips, array_index_ips         # [16 - 19]
    ]

    ips_not_implemented = [struct_ips, additional_ips]

    success = True
    num_fail = 0
    for ip in [item for sublist in ips[:18] for item in sublist]:
        uniq_sems = get_uniq_sems(ip[0])

        if isinstance(uniq_sems, str):
            print(ip)
            print(uniq_sems)
            continue

        sems_wo_score = deepcopy(uniq_sems[:1])
        found = False
        for i in range(len(sems_wo_score)):
            del sems_wo_score[i]['score']
            if sems_wo_score[i] == ip[1]:
                found = True
                break

        if not found:
            success = False
            num_fail += 1
            print('INP: %s' % ip)
            print(
                'TEST FAILED',
                'Actual: %s' % sems_wo_score[0],
                'Expected: %s' % ip[1], sep='\n'
            )

            print(*uniq_sems, sep='\n', end='\n\n\n')
        action = get_action(ip[0], 'hello.c', 2)
        print(action)
    print('%d tests failed' % num_fail)
    print('Testing', 'Successful' if success else 'Failed')
