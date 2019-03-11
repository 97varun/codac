from parsing import parse_input, Grammar, Rule, Parse
from rules import grammar
from inputs import var_ips, init_ips


def score(parse):
    scr = parse.rule.score
    for child in parse.children:
        if isinstance(child, Parse):
            scr += score(child)
    return scr


def score_parses(parses):
    for i in range(len(parses)):
        parses[i].semantics['score'] = score(parses[i])

for ip in var_ips:
    print('INP: %s' % ip)
    parses = parse_input(grammar, ip)

    score_parses(parses)

    parses_sems = [dict(y) for y in set(tuple(sorted(x.semantics.items())) for x in parses)]
    parses_sems.sort(key=lambda x: (len(x), x['score']), reverse=True)
    print(*parses_sems[:15], sep='\n', end='\n\n\n')
