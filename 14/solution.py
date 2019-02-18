def read_input(filename):
    return 554401


def solution1(n_recipes):
    p0, p1 = 0, 1
    recipe_scores = [3, 7]
    for i in range(n_recipes + 10):
        p0, p1 = _make_new_recipes(p0, p1, recipe_scores, len(recipe_scores))
    result = recipe_scores[n_recipes: n_recipes + 10]
    assert len(result) == 10
    return '%s' % ''.join(str(c) for c in result)


def solution2(n_recipes):
    score_sequence = str(n_recipes)
    p0, p1 = 0, 1
    recipe_scores = [3, 7]
    n = [int(d) for d in score_sequence]
    ln = len(n)
    i = 0
    while True:
        n_recipe_scores = len(recipe_scores)
        if i + ln >= n_recipe_scores:
            p0, p1 = _make_new_recipes(p0, p1, recipe_scores, n_recipe_scores)
            continue
        if recipe_scores[i:i+ln] == n:
            return i
        else:
            i += 1


def _make_new_recipes(p0, p1, recipe_scores, n):
    rs0, rs1 = recipe_scores[p0], recipe_scores[p1]
    s = rs0 + rs1
    if s > 9:
        s1, s2 = divmod(s, 10)
        recipe_scores.append(s1)
        recipe_scores.append(s2)
        n += 2
    else:
        recipe_scores.append(s)
        n += 1
    return (p0 + rs0 + 1) % n, (p1 + rs1 + 1) % n


def test_solution1():
    recipe_scores = [3, 7]
    positions = _make_new_recipes(0, 1, recipe_scores, len(recipe_scores))
    assert [3, 7, 1, 0] == recipe_scores
    assert (0, 1) == positions

    positions = _make_new_recipes(0, 1, recipe_scores, len(recipe_scores))
    assert [3, 7, 1, 0, 1, 0] == recipe_scores
    assert (4, 3) == positions

    assert '0124515891' == solution1(5)
    assert '5158916779' == solution1(9)
    assert '9251071085' == solution1(18)
    assert '5941429882' == solution1(2018)


def test_solution2():
    assert 9 == solution2('51589')
    assert 5 == solution2('01245')
    assert 18 == solution2('92510')
    assert 2018 == solution2('59414')
