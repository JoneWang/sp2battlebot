#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

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

    def __init__(self,
                 battle_number,
                 battle_type,
                 player_result,
                 victory,
                 my_team_members=None,
                 my_team_percentage=None,
                 my_estimate_league_point=None,
                 other_team_members=None,
                 other_team_percentage=None,
                 other_estimate_league_point=None,
                 ):
        self.battle_number = battle_number
        self.battle_type = battle_type
        self.player_result = player_result
        self.victory = victory
        self.my_team_members = my_team_members
        self.my_team_percentage = my_team_percentage
        self.my_estimate_league_point = my_estimate_league_point
        self.other_team_members = other_team_members
        self.other_team_percentage = other_team_percentage
        self.other_estimate_league_point = other_estimate_league_point

    @classmethod
    def de_json(cls, data):
        if not data:
            return None

        data = super(SP2BattleResult, cls).de_json(data)

        data['victory'] = \
            data.get('my_team_result').get('key') == 'victory'
        data['battle_type'] = data.get('type')

        battle = dict()
        for key in data:
            if key in (
                    'battle_number', 'battle_type',
                    'player_result', 'victory',
                    'my_team_members', 'my_team_percentage',
                    'my_estimate_league_point', 'other_team_members',
                    'other_team_percentage', 'other_estimate_league_point'):
                battle[key] = data[key]

        if battle.get('player_result'):
            battle['player_result'] = \
                SP2BattleResultMember.de_json(battle.get('player_result'))

        def member_sort(member):
            return member.sort_score

        def kill_sort(l_member, r_member):
            l_total_kill = l_member.kill_count + l_member.assist_count
            r_total_kill = r_member.kill_count + r_member.assist_count
            if l_total_kill != r_total_kill:
                return l_total_kill - r_total_kill
            elif l_member.assist_count != r_member.assist_count:
                return l_member.assist_count - r_member.assist_count
            elif l_member.death_count != r_member.death_count:
                return l_member.death_count - r_member.death_count
            elif l_member.special_count != r_member.special_count:
                return l_member.special_count - r_member.special_count

        if battle.get('my_team_members'):
            my_team_members = \
                SP2BattleResultMember.de_list(battle.get('my_team_members'))
            my_team_members.append(battle['player_result'])
            if battle.get('battle_type') == 'league':
                my_team_members.sort(key=kill_sort, reverse=True)
            else:
                my_team_members.sort(key=member_sort, reverse=True)
            battle['my_team_members'] = my_team_members

        if battle.get('other_team_members'):
            other_team_members = \
                SP2BattleResultMember.de_list(battle.get('other_team_members'))
            if battle.get('battle_type') == 'league':
                other_team_members.sort(key=kill_sort, reverse=True)
            else:
                other_team_members.sort(key=member_sort, reverse=True)
            battle['other_team_members'] = other_team_members

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

    def __init__(self, principal_id, nickname, style, species, weapon=None):
        self.principal_id = principal_id
        self.nickname = nickname
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

        battle = dict()
        for key in data:
            if key in ('principal_id', 'nickname', 'style', 'species'):
                battle[key] = data[key]

        battle['weapon'] = SP2PlayerWeapon.de_json(data.get('weapon'))

        return cls(**battle)


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
