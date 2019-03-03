import re

from collections import namedtuple
from copy import deepcopy


PROPS_WEAKNESS = 'weak to (?P<weakness>\w+(, \w+)*)(; )?'
PROPS_IMMUNITY = 'immune to (?P<immunity>\w+(, \w+)*)(; )?'
UNIT_LINE = re.compile(
    '(?P<units>\d+) units each with ' + \
    '(?P<hit_points>\d+) hit points ' + \
    '(\(((%s)|(%s))+\) )?' % (PROPS_WEAKNESS, PROPS_IMMUNITY) + \
    'with an attack that does (?P<attack_power>\d+) (?P<attack_type>\w+) damage ' + \
    'at initiative (?P<initiative>\d+)'
)


class Army:
    def __init__(self, name):
        self.name = name
        self.units = []

    def add_unit(self, unit):
        self.units.append((unit, len(self.units) + 1))

    def boost(self, value):
        for unit, uid in self.units:
            unit.attack_power += value

    def remove_empty(self):
        result = []
        for u, uid in self.units:
            if u.n <= 0:
                continue
            result.append((u, uid))
        self.units = result

    def __bool__(self):
        return len(self.units) > 0

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name and all(u1 == u2 for u1, u2 in zip(self.units, other.units))

    def __str__(self):
        groups = '\n'.join(
            'Group {uid} contains {n} units with hit points {hit_points} '
            'and effective power {ep} and initiative {initiative}'.format(
            uid=uid,
            n=u.n,
            hit_points=u.hit_points,
            ep=u.effective_power,
            initiative=u.initiative
        ) for u, uid in self.units)
        return '%s\n%s' % (self.name, groups)


class Unit:
    def __init__(self, matches, name, i):
        self.name = name
        self.i = i
        self.n = int(matches['units'])
        self.hit_points = int(matches['hit_points'])
        weaknesses = matches['weakness']
        self.weaknesses = set(weaknesses.split(', ')) if weaknesses else set()
        immunities = matches['immunity']
        self.immunities = set(immunities.split(', ')) if immunities else set()
        self.attack_power = int(matches['attack_power'])
        self.attack_type = matches['attack_type']
        self.initiative = int(matches['initiative'])

    def __str__(self):
        return '{n} units ({initiative} initiative) each with {hit_points} hit_points with {attack_power} {attack_type} attack power weak to {weaknesses}, immune to {immunities}'.format(
            n=self.n,
            initiative=self.initiative,
            hit_points=self.hit_points,
            attack_power=self.attack_power,
            attack_type=self.attack_type,
            weaknesses=self.weaknesses,
            immunities=self.immunities
        )

    def __repr__(self):
        return '%s group %d' % (self.name, self.i)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def effective_power(self):
        return self.n * self.attack_power


class Attack(
    namedtuple('Attack',
               [
                   'damage',
                   'au',
                   'aid',
                   'aname',
                   'du',
                   'duid',
                   'dname'
               ]
    )
):
    __slots__ = ()

    def __str__(self):
        return f'{self.aname} group {self.aid} attacks ' + \
        f'{self.dname} group {self.duid} inflicting {self.damage} damage'


def read_input(filename):
    with open(filename) as f:
        content = f.read()
        return _parse_content(content)


def solution1(data, suppress_print=True):
    immune_system, infection = deepcopy(data['immune_system']), deepcopy(data['infection'])
    prev_immune_system = None
    prev_infection = None
    while immune_system and infection:
        if not suppress_print:
            print()
            print(immune_system)
            print(infection)
        attacks = _compute_attacks(immune_system, infection)
        for attack in attacks:
            killed, actual_attack = _apply(attack)
            if killed > 0 and not suppress_print:
                print('%s, killing %d units' % (str(actual_attack), killed))
        immune_system.remove_empty()
        infection.remove_empty()
        if immune_system == prev_immune_system and infection == prev_infection:
            break
        else:
            prev_immune_system, prev_infection = deepcopy(immune_system), deepcopy(infection)
    if immune_system and infection:
        surviving_army = infection
    else:
        surviving_army = immune_system or infection
    if not suppress_print:
        print('%s wins !' % surviving_army.name)
    return sum(unit.n for unit, uid in surviving_army.units), surviving_army.name


def solution2(data):
    boost = 1
    units = -1
    winner = 'Infection'
    while winner == 'Infection':
        immune_system, infection = deepcopy(data['immune_system']), deepcopy(data['infection'])
        immune_system.boost(boost)
        units, winner = solution1({'immune_system': immune_system, 'infection': infection}, suppress_print=True)
        print('With boost=%d %s wins' % (boost, winner))
        boost *= 2
    min_b, max_b = boost / 4, boost / 2
    boost = round((min_b + max_b) / 2)
    prev_boost = 0
    while True:
        immune_system, infection = deepcopy(data['immune_system']), deepcopy(data['infection'])
        immune_system.boost(boost)
        units, winner = solution1({'immune_system': immune_system, 'infection': infection}, suppress_print=True)
        if abs(prev_boost - boost) == 1 and winner == 'Immune System':
            print('Found minimal boost: %d' % boost)
            break
        prev_boost = boost
        if winner == 'Infection':
            print('With boost=%d %s wins' % (boost, winner))
            min_b = boost
            boost = round((min_b + max_b) / 2)
        else:
            print('With boost=%d %s wins. Decreasing boost' % (boost, winner))
            max_b = boost
            boost = round((min_b + max_b) / 2)
    return units, winner


def _parse_content(content):
    immune_system = infection = army = None
    i = 0
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        if line == 'Immune System:':
            immune_system = army = Army(line[:-1])
            i = 0
        elif line == 'Infection:':
            infection = army = Army(line[:-1])
            i = 0
        else:
            m = re.match(UNIT_LINE, line)
            if not m:
                raise Exception('Invalid input line: %s' % line)
            i += 1
            army.add_unit(Unit(m, army.name, i))
    return {'immune_system': immune_system, 'infection': infection}


def _compute_attacks(immune_system, infection):
    attacks = []
    attacks += _select_attacks(immune_system, infection)
    attacks += _select_attacks(infection, immune_system)
    return sorted(
        attacks,
        key=lambda a: -a.au.initiative
    )


def _select_attacks(attacking_army, defending_army):
    selected_targets = set()
    attacks = []
    for u, uid in sorted(
            attacking_army.units,
            key=lambda t: (-t[0].effective_power, -t[0].initiative)
    ):
        attack = _calculate_attack(u, uid, attacking_army, defending_army, selected_targets)
        if attack:
            attacks.append(attack)
            selected_targets.add(attack.duid)
    return attacks


def _calculate_attack(au, auid, attacking_army, enemy_army, unavailable_targets):
    result = None
    max_damage = 0
    for du, duid in enemy_army.units:
        if duid in unavailable_targets or au.attack_type in du.immunities:
            continue
        damage = au.effective_power
        if au.attack_type in du.weaknesses:
            damage *= 2
        attack = Attack(
            damage,
            au,
            auid,
            attacking_army.name,
            du,
            duid,
            enemy_army.name
        )
        if damage > max_damage:
            result = attack
            max_damage = damage
        elif damage == max_damage:
            if result.du.effective_power < du.effective_power:
                result = attack
            elif result.du.effective_power == du.effective_power and result.du.initiative < du.initiative:
                result = attack
    return result


def _apply(attack):
    damage = attack.au.effective_power
    if damage <= 0:
        #print('No units left in group to perform the attack')
        return 0, attack
    if attack.au.attack_type in attack.du.weaknesses:
        damage *= 2
    killed_units = int(damage / attack.du.hit_points)
    orig_n = attack.du.n
    attack.du.n -= killed_units
    attack = Attack(damage, *attack[1:])
    return killed_units if attack.du.n >= 0 else orig_n, attack


def test_read_input():
    line = '3472 units each with ' \
           '9606 hit points ' \
           'with an attack that does 26 cold damage ' \
           'at initiative 14'
    unit = Unit(re.match(UNIT_LINE, line), '', 0)
    assert 3472 == unit.n
    assert 9606 == unit.hit_points
    assert 26 == unit.attack_power
    assert 'cold' == unit.attack_type
    assert 14 == unit.initiative
    assert set() == unit.weaknesses
    assert set() == unit.immunities

    line = '303 units each with ' \
           '10428 hit points ' \
           'with an attack that does 328 radiation damage ' \
           'at initiative 13'
    unit = Unit(re.match(UNIT_LINE, line), '', 0)
    assert 303 == unit.n
    assert 10428 == unit.hit_points
    assert 328 == unit.attack_power
    assert 'radiation' == unit.attack_type
    assert 13 == unit.initiative
    assert set() == unit.weaknesses
    assert set() == unit.immunities

    line = '5525 units each with ' \
           '14091 hit points ' \
           '(weak to cold) ' \
           'with an attack that does 4 bludgeoning damage ' \
           'at initiative 18'
    unit = Unit(re.match(UNIT_LINE, line), '', 0)
    assert 5525 == unit.n
    assert 14091 == unit.hit_points
    assert 4 == unit.attack_power
    assert 'bludgeoning' == unit.attack_type
    assert 18 == unit.initiative
    assert {'cold'} == unit.weaknesses
    assert set() == unit.immunities

    line = '2455 units each with ' \
           '6330 hit points ' \
           '(immune to slashing, radiation) ' \
           'with an attack that does 20 bludgeoning damage ' \
           'at initiative 20'

    unit = Unit(re.match(UNIT_LINE, line), '', 0)
    assert 2455 == unit.n
    assert 6330 == unit.hit_points
    assert 20 == unit.attack_power
    assert 'bludgeoning' == unit.attack_type
    assert 20 == unit.initiative
    assert {'slashing', 'radiation'} == unit.immunities
    assert set() == unit.weaknesses

    line = '1734 units each with ' \
           '30384 hit points ' \
           '(weak to cold, bludgeoning) ' \
           'with an attack that does 34 cold damage ' \
           'at initiative 4'
    unit = Unit(re.match(UNIT_LINE, line), '', 0)
    assert 1734 == unit.n
    assert 30384 == unit.hit_points
    assert 34 == unit.attack_power
    assert 'cold' == unit.attack_type
    assert 4 == unit.initiative
    assert {'cold', 'bludgeoning'} == unit.weaknesses
    assert set() == unit.immunities

    line = '9278 units each with ' \
           '9654 hit points ' \
           '(weak to slashing; immune to radiation) ' \
           'with an attack that does 10 radiation damage ' \
           'at initiative 9'

    unit = Unit(re.match(UNIT_LINE, line), '', 0)
    assert 9278 == unit.n
    assert 9654 == unit.hit_points
    assert 10 == unit.attack_power
    assert 'radiation' == unit.attack_type
    assert 9 == unit.initiative
    assert {'radiation'} == unit.immunities
    assert {'slashing'} == unit.weaknesses

    line = '2667 units each with ' \
           '9631 hit points ' \
           '(immune to cold; weak to radiation) ' \
           'with an attack that does 33 radiation damage ' \
           'at initiative 3'

    unit = Unit(re.match(UNIT_LINE, line), '', 0)
    assert 2667 == unit.n
    assert 9631 == unit.hit_points
    assert 33 == unit.attack_power
    assert 'radiation' == unit.attack_type
    assert 3 == unit.initiative
    assert {'cold'} == unit.immunities
    assert {'radiation'} == unit.weaknesses

    line = '8739 units each with ' \
           '43560 hit points ' \
           '(weak to bludgeoning; immune to radiation, slashing) ' \
           'with an attack that does 9 cold damage ' \
           'at initiative 1'
    unit = Unit(re.match(UNIT_LINE, line), '', 0)
    assert 8739 == unit.n
    assert 43560 == unit.hit_points
    assert 9 == unit.attack_power
    assert 'cold' == unit.attack_type
    assert 1 == unit.initiative
    assert {'radiation', 'slashing'} == unit.immunities
    assert {'bludgeoning'} == unit.weaknesses

    content = """Immune System:
17 units each with 5390 hit points (weak to radiation, bludgeoning) with an attack that does 4507 fire damage at initiative 2
989 units each with 1274 hit points (immune to fire; weak to bludgeoning, slashing) with an attack that does 25 slashing damage at initiative 3

Infection:
801 units each with 4706 hit points (weak to radiation) with an attack that does 116 bludgeoning damage at initiative 1
4485 units each with 2961 hit points (immune to radiation; weak to fire, cold) with an attack that does 12 slashing damage at initiative 4"""

    data = _parse_content(content)
    immune_system, infection = data['immune_system'], data['infection']
    assert 'Immune System' == immune_system.name
    assert 2 == len(immune_system.units)
    assert 17, 1 == immune_system.units[0].n
    assert 989, 2 == immune_system.units[1].n

    assert 'Infection' == infection.name
    assert 2 == len(infection.units)
    assert 801, 1 == infection.units[0].n
    assert 4485, 2 == infection.units[1].n


def test_solution1():
    content = """Immune System:
17 units each with 5390 hit points (weak to radiation, bludgeoning) with an attack that does 4507 fire damage at initiative 2
989 units each with 1274 hit points (immune to fire; weak to bludgeoning, slashing) with an attack that does 25 slashing damage at initiative 3

Infection:
801 units each with 4706 hit points (weak to radiation) with an attack that does 116 bludgeoning damage at initiative 1
4485 units each with 2961 hit points (immune to radiation; weak to fire, cold) with an attack that does 12 slashing damage at initiative 4"""

    data = _parse_content(content)
    immune_system, infection = data['immune_system'], data['infection']

    in1, in1_id = infection.units[0]
    in2, in2_id = infection.units[1]
    im1, im1_id = immune_system.units[0]
    im2, im2_id = immune_system.units[1]
    attack = _calculate_attack(in1, in1_id, infection, immune_system, set())
    assert Attack(
                   185832,
                   in1,
                   in1_id,
                   infection.name,
                   im1,
                   im1_id,
                   immune_system.name
               ) == attack, attack

    attacks = _calculate_attack(in2, in2_id, infection, immune_system, set())
    assert Attack(
                   107640,
                   in2,
                   in2_id,
                   infection.name,
                   im2,
                   im2_id,
                   immune_system.name
               ) == attacks, attacks

    result = solution1(data)
    assert (5216, 'Infection') == result, result
