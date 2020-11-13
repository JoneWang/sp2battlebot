#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sp2bot.utils.model import Model


class SP2User(Model):

    def __init__(self, unique_id, player, session=None):
        self.unique_id = unique_id
        self.player = player
        self.session = session

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = super(SP2User, cls).de_json(data)
        records = data.get('records')

        user = dict()
        user['unique_id'] = records.get('unique_id')
        user['player'] = SP2Player.de_json(records.get('player'))

        return cls(**user)


class SP2BattleOverview(Model):

    def __init__(self, unique_id, summary, results):
        self.unique_id = unique_id
        self.summary = summary
        self.results = results

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = super(SP2BattleOverview, cls).de_json(data)

        data['summary'] = SP2BattleResultsSummary.de_json(data.get('summary'))
        data['results'] = SP2BattleResult.de_list(data.get('results'))

        return cls(**data)


class SP2BattleResultsSummary(Model):

    def __init__(self,
                 victory_count,
                 defeat_count,
                 victory_rate,
                 kill_count_average,
                 death_count_average,
                 assist_count_average,
                 special_count_average,
                 count
                 ):
        self.victory_count = victory_count
        self.defeat_count = defeat_count
        self.victory_rate = victory_rate
        self.kill_count_average = kill_count_average
        self.death_count_average = death_count_average
        self.assist_count_average = assist_count_average
        self.special_count_average = special_count_average
        self.count = count

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = super(SP2BattleResultsSummary, cls).de_json(data)

        return cls(**data)


class SP2BattleType:
    Regular = 'regular'
    League = 'league'
    Gachi = 'gachi'


class SP2BattleResult(Model):
    class Rule(Model):
        def __init__(self, key, name):
            self.key = key
            self.name = name

        @classmethod
        def de_json(cls, data):
            if not data:
                return None
            data = super(SP2BattleResult.Rule, cls).de_json(data)
            rule = dict()
            for key in data:
                if key in ('key', 'name'):
                    rule[key] = data[key]
            return cls(**rule)

    def __init__(self,
                 battle_number,
                 battle_type,
                 rule,
                 player_result,
                 victory,
                 game_mode=None,
                 my_team_members=None,
                 my_team_percentage=None,
                 my_estimate_league_point=None,
                 other_team_members=None,
                 other_team_percentage=None,
                 other_estimate_league_point=None,
                 estimate_gachi_power=None,
                 ):
        self.battle_number = battle_number
        self.battle_type = battle_type
        self.rule = rule
        self.player_result = player_result
        self.victory = victory
        self.game_mode = game_mode
        self.my_team_members = my_team_members
        self.my_team_percentage = my_team_percentage
        self.my_estimate_league_point = my_estimate_league_point
        self.other_team_members = other_team_members
        self.other_team_percentage = other_team_percentage
        self.other_estimate_league_point = other_estimate_league_point
        self.estimate_gachi_power = estimate_gachi_power

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = super(SP2BattleResult, cls).de_json(data)

        data['victory'] = \
            data.get('my_team_result').get('key') == 'victory'
        data['battle_type'] = data.get('type')

        battle = dict()
        battle['game_mode'] = data["game_mode"]['key']
        for key in data:
            if key in (
                    'battle_number', 'battle_type',
                    'player_result', 'victory',
                    'my_team_members', 'my_team_percentage',
                    'my_estimate_league_point', 'other_team_members',
                    'other_team_percentage', 'other_estimate_league_point',
                    'rule', 'estimate_gachi_power'):
                battle[key] = data[key]

        if data.get("x_power"):
            battle['estimate_gachi_power'] = f"{data['x_power']}\nestimate_x_power: {data['estimate_x_power']}"

        if battle.get('rule'):
            battle['rule'] = SP2BattleResult.Rule.de_json(battle.get('rule'))

        if battle.get('player_result'):
            battle['player_result'] = \
                SP2BattleResultMember.de_json(battle.get('player_result'))

        for k in ['my_team_members', 'other_team_members']:
            if not battle.get(k):
                continue

            team_members = SP2BattleResultMember.de_list(battle.get(k))
            if k == 'my_team_members':
                team_members.append(battle['player_result'])
            if battle.get('battle_type') == 'league':
                team_members.sort(key=lambda x: (x.kill_count, x.kill_count - x.assist_count), reverse=True)
            else:
                team_members.sort(key=lambda x: x.sort_score, reverse=True)
            battle[k] = team_members

        return cls(**battle)

    @classmethod
    def de_list(cls, data):
        if not data:
            return list()

        battles = list()
        for battle in data:
            battles.append(cls.de_json(battle))

        return battles


class SP2BattleResultMember(Model):

    def __init__(self,
                 kill_count,
                 assist_count,
                 death_count,
                 special_count,
                 sort_score,
                 game_paint_point,
                 player
                 ):
        self.kill_count = kill_count
        self.assist_count = assist_count
        self.death_count = death_count
        self.special_count = special_count
        self.sort_score = sort_score
        self.game_paint_point = game_paint_point
        self.player = player

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = super(SP2BattleResultMember, cls).de_json(data)

        data['player'] = SP2Player.de_json(data.get('player'))
        data['kill_count'] = data.get('kill_count') + data.get('assist_count')

        return cls(**data)

    @classmethod
    def de_list(cls, data):
        if not data:
            return list()

        players = list()
        for player in data:
            players.append(cls.de_json(player))

        return players


class SP2PlayerSpecies:
    Octolings = 'octolings'
    Inklings = 'inklings'


class SP2Player(Model):
    class Udemae(Model):
        def __init__(self, name, s_plus_number=None):
            self.name = name
            self.s_plus_number = s_plus_number

        @classmethod
        def de_json(cls, data):
            if not data:
                return None
            data = super(SP2Player.Udemae, cls).de_json(data)

            udemae = dict()
            for key in data:
                if key in ('name', 's_plus_number'):
                    udemae[key] = data[key]
            return cls(**udemae)

    def __init__(self,
                 principal_id,
                 nickname,
                 style,
                 species,
                 weapon=None,
                 udemae=None):
        self.principal_id = principal_id
        self.nickname = nickname
        self.udemae = udemae
        self.style = style
        self.species = species
        self.weapon = weapon

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = super(SP2Player, cls).de_json(data)

        if data.get('player_type'):
            data['style'] = data.get('player_type').get('style')
            data['species'] = data.get('player_type').get('species')

        player = dict()
        for key in data:
            if key in ('principal_id', 'nickname', 'style', 'species'):
                player[key] = data[key]

        player['weapon'] = SP2PlayerWeapon.de_json(data.get('weapon'))
        player['udemae'] = SP2Player.Udemae.de_json(data.get('udemae'))

        return cls(**player)


class SP2PlayerWeapon(Model):
    def __init__(self, name):
        self.name = name

    @classmethod
    def de_json(cls, data):
        if not data:
            return cls('')

        data = super(SP2PlayerWeapon, cls).de_json(data)

        battle = dict()
        for key in data:
            if key in ('name'):
                battle[key] = data[key]

        return cls(**battle)
