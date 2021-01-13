#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime as dt
from telegram.utils.helpers import escape_markdown

from sp2bot import store
from sp2bot.splatoon2models import SP2BattleResult, SP2BattleType, \
    SP2PlayerSpecies


class MessageType:
    Markdown = "Markdown"
    HTML = "HTML"


class Message:

    def __init__(self, context):
        self.context = context

    def login_url(self, url):
        text = '1.Navigate to this URL in your *desktop* browser:\n'
        text += f'[Click here to open the URL]({url})\n\n'
        text += '2.Log in, *right click* the "Select this account" button, *copy the link address*, and type /settoken `[link_address]`.'

        return text, MessageType.Markdown

    @property
    def generate_iksm_wait(self):
        text = 'Please wait a moment...'
        return text

    def iksm_session(self, iksm_session):
        text = f'{iksm_session}'
        return text

    @property
    def splatoon_connect_error(self):
        text = 'Error from Nintendo server, please try again later.'
        return text

    @property
    def session_invalid(self):
        text = 'The `token` is invalid.\n'
        if self.context.chat.type != 'private':
            text += 'To reset, send /gettoken to ' \
                    f'@{self.context.bot_user.username}. '
        else:
            text += 'To reset, type /gettoken.'

        return text, MessageType.Markdown

    @property
    def setsession_must_private_message(self):
        return f'Command /settoken must send to @{self.context.bot_user.username}.'

    @property
    def setsession_error(self):
        return 'Type error.\n' \
               'Please type /settoken `[link_address]`.', MessageType.Markdown

    @property
    def setsession_set_success(self):
        return "Oh~ Nice to meet you.\n" \
               "Now you'll know me with /help."

    @property
    def setsession_update_success(self):
        return 'Success! You set a new token.'

    @property
    def setsession_set_fail(self):
        return 'The `token` is invalid.', MessageType.Markdown

    @property
    def setsession_invalid(self):
        return 'The `token` is invalid.', MessageType.Markdown

    @property
    def not_found_battle(self):
        return 'Not found battle.'

    @property
    def last_command_error(self):
        return 'Command error.\n' \
               'Type `/last [0~49]` or `/last`.'

    @property
    def started(self):
        return f'@{self.context.bot_user.username} started.\n ' \
               'To stop, type /stoppush.'

    @property
    def already_started(self):
        return f'@{self.context.bot_user.username} already started.'

    @property
    def stopped(self):
        return f'@{self.context.bot_user.username} stopped.\n ' \
               'To restart, type /startpush.'

    @property
    def already_stopped(self):
        return f'@{self.context.bot_user.username} already stopped.'

    @property
    def have_not_start_push(self):
        return "You haven't started push.\n" \
               'To start, type /startpush'

    @property
    def reset_push_success(self):
        return 'Push statistics reset succeeded.'

    @property
    def push_here(self):
        return 'The battle info will be push here.\n' \
               'To stop, type /stoppush.'

    @property
    def help(self):
        return """
/start - Start here.
/gettoken - Get token.
/settoken - Set token.
/last - Last battle info.
/last50 - Show overview for last 50 battle.
/startpush - Startup battle push.
/stoppush - Stop battle push.
/me - Get user.
/help - Show help.
"""

    @property
    def start(self):
        return """
Welcome to Splatoon2 Battle Bot.
At first you must to use /gettoken to set token.

More commands type /help.
"""

    @staticmethod
    def rank_changed(rule_name, nickname, old_rank, new_rank):
        nickname = nickname.replace('`', '`\``')
        old_rank_s_plus_number = old_rank.s_plus_number if old_rank.s_plus_number else ''
        new_rank_s_plus_number = new_rank.s_plus_number if new_rank.s_plus_number else ''

        ranks = ['C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+', 'S', 'S+', 'X']
        old_level = ranks.index(old_rank.name)
        new_level = ranks.index(new_rank.name)

        change = 'RankUp'
        change_icon = '⬆️'
        if old_level > new_level or \
                (old_level == new_level and old_rank_s_plus_number > new_rank_s_plus_number):
            change = 'RankDown'
            change_icon = '⬇️'

        return f'{change_icon} #{change} *{nickname}* `{rule_name}` ' \
               f'{old_rank.name}{old_rank_s_plus_number} -> ' \
               f'{new_rank.name}{new_rank_s_plus_number}'

    def last50_overview(self, battle_overview):
        battles = battle_overview.results
        summary = battle_overview.summary

        lines = list()

        display_name = self.context.user.display_name
        lines.append(
            f'Last 50 Battle For {escape_markdown(display_name, version=2)}')

        lines.append(
            '*▸* `V/D: `*{0}/{1}*`({2:.0f}%)`'.format(summary.victory_count,
                                                      summary.defeat_count,
                                                      summary.victory_rate * 100))

        lines.append('*▸* `AVG: `*{0:.1f}*`({1:.1f})k `*{2:.1f}*`d {3:.1f}sp`'
                     .format(summary.kill_count_average,
                             summary.assist_count_average,
                             summary.death_count_average,
                             summary.special_count_average))

        line = ''
        for i in range(50):
            if i < len(battles):
                line += "🤪" if battles[i].victory else "👿"
            else:
                line += "🐦"

            if (i + 1) % 10 == 0:
                lines.append(line)
                line = ''

        return '\n'.join(lines), MessageType.Markdown

    def last_battle(self, battle):
        return _battle_result_msg(battle, self.context.user.sp2_user)

    @staticmethod
    def user_info(info):
        record = info["records"]
        player = info["records"]["player"]
        rank = str(player["player_rank"])
        if player.get("star_rank"):
            rank = f'(⭐️{player["star_rank"]}) ' + rank

        lp = record["league_stats"]["pair"]
        lt = record["league_stats"]["team"]
        lines = [
            f'`{player["nickname"]}, {rank}`',
            f'*真格段位：* 区 `{player["udemae_zones"]["name"]}` | 塔 `{player["udemae_tower"]["name"]}` | 鱼 `{player["udemae_rainmaker"]["name"]}` | 蛤 `{player["udemae_clam"]["name"]}`',
            f'*最近场数：* {record["recent_win_count"]}/{record["recent_lose_count"]}',
            f'*最近掉线：* {record["recent_disconnect_count"]}',
            f'*所有记录：* {record["win_count"] + record["lose_count"]} | {record["win_count"]}/{record["lose_count"]}',
            f'*双排记录：* {player["max_league_point_pair"]}',
            f'*▸* 🥇 `{lp["gold_count"]}`  🥈 `{lp["silver_count"]}`  🥉 `{lp["bronze_count"]}`  无 `{lp["no_medal_count"]}`  共 `{sum(lp.values())}`',
            f'*四排记录：* {player["max_league_point_team"]}',
            f'*▸* 🥇 `{lt["gold_count"]}`  🥈 `{lt["silver_count"]}`  🥉 `{lt["bronze_count"]}`  无 `{lt["no_medal_count"]}`  共 `{sum(lt.values())}`',
            f'*首次游戏：* {dt.utcfromtimestamp(record["start_time"]):%Y-%m-%d %H:%M:%S} (UTC)',
            f'*最近游玩：* {dt.utcfromtimestamp(record["update_time"]):%Y-%m-%d %H:%M:%S (UTC)}'
        ]
        return '\n'.join(lines), MessageType.Markdown

    @staticmethod
    def push_battle(battle, battle_poll):
        return _battle_result_msg(battle, battle_poll.user.sp2_user, battle_poll)


def _battle_result_msg(battle, sp2_user, battle_poll=None):
    lines = list()

    if battle_poll:
        if battle.victory:
            lines.append('我们赢啦！')
        else:
            lines.append('呜呜呜~输了不好意思见人了~')

        victory_rate = 0
        if battle_poll.game_count > 0:
            victory_rate = battle_poll.game_victory_count / battle_poll.game_count * 100

        victory_count = battle_poll.game_victory_count
        defeat_count = battle_poll.game_count - battle_poll.game_victory_count

        battle_stat = f'`当前胜率{victory_rate:.0f}% 胜{victory_count} 负{defeat_count}`'
        lines.append(battle_stat)

    else:
        lines.append(f"Battle ID:{battle.battle_number}")

    rule_info = ''
    if battle.battle_type == SP2BattleType.Gachi:
        power = f'  Power: {battle.estimate_gachi_power}' if battle.estimate_gachi_power else ''
        rule_info = f'`{battle.rule.name}:{battle.player_result.player.udemae.name}{power}`'
    elif battle.battle_type == SP2BattleType.League:
        max_league_point = ''
        if battle.max_league_point > 0:
            max_league_point = f'\nmax_league_point: {battle.max_league_point}'
        rule_info = f'`{battle.rule.name}, {battle.game_mode}{max_league_point}`'
    if rule_info:
        lines.append(rule_info)

    my_team_is_top = battle.victory

    my_or_other_members = [battle.my_team_members, battle.other_team_members]

    lines.append(_battle_team_title(my_team_is_top, battle))
    lines.append(_battle_result_member(sp2_user, my_or_other_members[not my_team_is_top]))

    lines.append(_battle_team_title(not my_team_is_top, battle))
    lines.append(_battle_result_member(sp2_user, my_or_other_members[my_team_is_top]))

    return '\n'.join(lines), MessageType.Markdown


def _battle_team_title(my_team: bool, battle: SP2BattleResult):
    if my_team:
        team_title = 'VICTORY' if battle.victory else 'DEFEAT'
    else:
        team_title = 'DEFEAT' if battle.victory else 'VICTORY'

    point = ' '
    if battle.battle_type == SP2BattleType.Regular:
        point = ' {:.1f}'.format([battle.my_team_percentage,
                                  battle.other_team_percentage]
                                 [not my_team])
    elif battle.battle_type == SP2BattleType.League:
        point = ' {}'.format([battle.my_estimate_league_point,
                              battle.other_estimate_league_point]
                             [not my_team])

    return f'{team_title} {battle.battle_type}{point}：'


def _battle_result_member(self_sp2_user, members):
    def format_member(member):
        escaped_nickname = member.player.nickname.replace('`', '`\``')
        nickname = f'`{escaped_nickname}`'

        # If self
        if self_sp2_user and member.player.principal_id == self_sp2_user.principal_id:
            nickname = f'{nickname} 👨🏻‍✈️'

        # turf_war don't have udemae info
        if member.player.udemae and member.player.udemae.name:
            return '`{:<2}|{:>2} {:>2}+{}k` `{:>2}d {}sp `{}' \
                .format(member.player.udemae.name, member.kill_count,
                        member.kill_count - member.assist_count,
                        member.assist_count,
                        member.death_count,
                        member.special_count,
                        nickname)

        avatar = '🐙' if member.player.species == SP2PlayerSpecies.Octolings else '🦑'

        return '{}`{:>2}({})k` `{:>2}d {}sp` {}' \
            .format(avatar,
                    member.kill_count,
                    member.assist_count,
                    member.death_count,
                    member.special_count,
                    nickname)

    return '\n'.join(map(format_member, members))
