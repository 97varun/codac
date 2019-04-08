from parsing import parse_input, Grammar, Rule, Parse
from rules import grammar
from inputs import *
from exec import generate_code
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
        # print(parses[i], parses[i].semantics['score'])


def get_action(transcript, file, line):
    parses = parse_input(grammar, transcript)
    if parses:
        score_parses(parses)
    else:
        return json.dumps({'input': transcript, 'error': 'could not parse'})
    parses_sems = [dict(y) for y in set(tuple(sorted(x.semantics.items()))
                   for x in parses)]
    parses_sems.sort(key=lambda x: (len(x), x['score']), reverse=True)

    codes = generate_code(parses_sems[:5], file, line)
    uniq_codes = []
    uniq_ops = []
    for code in codes:
        if code['output'] not in uniq_ops:
            uniq_ops.append(code['output'])
            uniq_codes.append(code)
    uniq_codes.insert(0, {'input': transcript})
    return json.dumps(uniq_codes)


if __name__ == "__main__":
    ips = [arr_ips, cond_ips, exp_ips, func_ips, func_param_ips, func_call_ips,  # [0-5]
           f_c_printf_ips, f_c_scanf_ips, init_ips, loop_ips, loop_init_ips,     # [6-10]
           loop_cond_ips, loop_update_ips, nav_ips, pack_ips, ptr_ips,           # [11-15]
           ptr_init_ips, ptr_ips_1, return_stmt_ips, var_ips]                    # [16-19]

    ips_not_implemented = [struct_ips, additional_ips]

    for ip in ips[3]:
        print('INP: %s' % ip)
        parses = parse_input(grammar, ip)

        if parses:
                score_parses(parses)

        parses_sems = [dict(y) for y in set(tuple(sorted(x.semantics.items())) for x in parses)]
        parses_sems.sort(key=lambda x: (len(x), x['score']), reverse=True)
        print(*parses_sems[:5], sep='\n', end='\n\n\n')

        codes = generate_code(parses_sems[:1], 'hello.c', 2)
        print(codes)
