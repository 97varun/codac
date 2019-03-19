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
        return '{{"input": "{0}", "error": "could not parse"}}'.format(transcript)
    parses_sems = [dict(y) for y in set(tuple(sorted(x.semantics.items())) for x in parses)]
    parses_sems.sort(key=lambda x: (len(x), x['score']), reverse=True)

    codes = generate_code(parses_sems[:5])
    uniq_codes = []
    for code in codes:
        if code not in uniq_codes and code is not None:
            uniq_codes.append(code)
    return '{{"input": "{0}", "output": {1}}}'.format(transcript, json.dumps(uniq_codes))


if __name__ == "__main__":
        for ip in func_param_ips:
                print('INP: %s' % ip)
                parses = parse_input(grammar, ip)

                if parses:
                        score_parses(parses)

                parses_sems = [dict(y) for y in set(tuple(sorted(x.semantics.items())) for x in parses)]
                parses_sems.sort(key=lambda x: (len(x), x['score']), reverse=True)
                print(*parses_sems[:5], sep='\n', end='\n\n\n')

                generate_code(parses_sems[:1])
