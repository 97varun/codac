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


def get_action(transcript, file, line):
    parses = parse_input(grammar, transcript)
    if parses:
        score_parses(parses)
    else:
        return json.dumps({'input': transcript, 'error': 'could not parse'})
    parses.sort(key=lambda x: (len(x.semantics), x.semantics['score']),
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
    # print(*uniq_sems[:5], sep='\n', end='\n\n\n')

    codes = generate_code(uniq_sems[:1], file, line)
    codes.insert(0, {'input': transcript})
    return json.dumps(codes)


if __name__ == "__main__":
    ips = [
        arr_ips, cond_ips, exp_ips, func_ips, func_param_ips,  # [0 - 4]
        func_call_ips, f_c_printf_ips, f_c_scanf_ips, init_ips,  # [5 - 8]
        loop_ips, loop_init_ips, loop_cond_ips, loop_update_ips,  # [9 - 12]
        nav_ips, pack_ips, ptr_ips, ptr_init_ips, ptr_ips_1,  # [13 - 17]
        return_stmt_ips, var_ips, array_index_ips  # [18 - 20]
    ]

    ips_not_implemented = [struct_ips, additional_ips]

    for ip in ips[1]:
        print('INP: %s' % ip)
        action = get_action(ip, 'hello.c', 2)
        print(action)
