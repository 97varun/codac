from parsing import parse_input, Grammar, Rule, Parse
from rules import grammar
from inputs import *
from executor import generate_code
import json


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


def get_action(transcript):
    parses = parse_input(grammar, transcript)
    if parses:
        score_parses(parses)
    else:
        return json.dumps({'input': transcript, 'error': 'could not parse'})
    parses_sems = [dict(y) for y in set(tuple(sorted(x.semantics.items())) for x in parses)]
    parses_sems.sort(key=lambda x: (len(x), x['score']), reverse=True)

    codes = generate_code(parses_sems[:5])
    uniq_codes = []
    for code in codes:
        if code not in uniq_codes and code is not None:
            uniq_codes.append(code)
    return json.dumps({'input': transcript, 'output': uniq_codes})


if __name__ == "__main__":
        ips = [arr_ips, cond_ips, exp_ips, func_ips, func_param_ips,    #[0-4]
               func_call_ips, init_ips, loop_ips, loop_init_ips, loop_cond_ips, #[5-9]
               loop_update_ips, pack_ips, ptr_ips, ptr_init_ips, ptr_ips_1, return_stmt_ips, var_ips ]  #[10-16]

        ips_not_implemented = [struct_ips, nav_ips]

        for ip in ips[15]:
                print('INP: %s' % ip)
                parses = parse_input(grammar, ip)

                if parses:
                        score_parses(parses)

                parses_sems = [dict(y) for y in set(tuple(sorted(x.semantics.items())) for x in parses)]
                parses_sems.sort(key=lambda x: (len(x), x['score']), reverse=True)
                print(*parses_sems[:5], sep='\n', end='\n\n\n')

                generate_code(parses_sems[:1])
