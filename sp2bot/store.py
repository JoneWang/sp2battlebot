#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from pony.orm import *

from sp2bot.models import User, BattlePoll

# Create database
db = Database()


# Table
class UserTable(db.Entity):
    id = PrimaryKey(int)
    username = Optional(str, unique=True, nullable=True)
    first_name = Required(str)
    last_name = Optional(str, nullable=True)
    push = Required(bool, default=0)
    iksm_session = Optional(str, nullable=True)
    session_token = Optional(str, nullable=True)
    sp2_principal_id = Optional(str, nullable=True)
    sp2_nickname = Optional(str, nullable=True)
    sp2_style = Optional(str, nullable=True)
    sp2_species = Optional(str, nullable=True)
    sp2_player_json = Optional(LongStr, nullable=True)
    battle_poll = Optional(LongStr, nullable=True)


# Bind
db.bind(provider='sqlite', filename='sp2bot.sqlite', create_db=True)

# Create table
db.generate_mapping(create_tables=True)

# Debug mode
set_sql_debug(True)


@db_session
def insert_user(user):
    UserTable(id=user.id,
              username=user.username,
              first_name=user.first_name,
              last_name=user.last_name,
              push=user.push,
              iksm_session=user.iksm_session,
              session_token=user.session_token,
              sp2_principal_id=user.sp2_user.principal_id,
              sp2_nickname=user.sp2_user.nickname,
              sp2_style=user.sp2_user.style,
              sp2_species=user.sp2_user.species,
              sp2_player_json=user.sp2_user.json,
              )


@db_session
def select_users_with_principal_ids(principal_ids):
    us = select(
        u for u in UserTable if u.sp2_principal_id in principal_ids)

    users = []
    for u in us:
        users.append(User(u.id,
                          u.first_name,
                          username=u.username,
                          last_name=u.last_name,
                          push=u.push,
                          iksm_session=u.iksm_session,
                          session_token=u.session_token,
                          sp2_principal_id=u.sp2_principal_id,
                          sp2_nickname=u.sp2_nickname,
                          sp2_style=u.sp2_style,
                          sp2_species=u.sp2_species,
                          # sp2_player_json=u.sp2_player_json
                          ))
    return users


@db_session
def select_user(user_id):
    u = select(u for u in UserTable if u.id == user_id).first()
    if u:
        return User(u.id,
                    u.first_name,
                    username=u.username,
                    last_name=u.last_name,
                    push=u.push,
                    iksm_session=u.iksm_session,
                    session_token=u.session_token,
                    sp2_principal_id=u.sp2_principal_id,
                    sp2_nickname=u.sp2_nickname,
                    sp2_style=u.sp2_style,
                    sp2_species=u.sp2_species,
                    # sp2_player_json=u.sp2_player_json
                    )
    else:
        return None


@db_session
def update_user(user):
    u = select(u for u in UserTable if u.id == user.id).first()

    if u:
        u.username = user.username
        u.first_name = user.first_name
        u.last_name = user.last_name
        u.iksm_session = user.iksm_session
        u.session_token = user.session_token
        u.sp2_principal_id = user.sp2_user.principal_id
        u.sp2_nickname = user.sp2_user.nickname
        u.sp2_style = user.sp2_user.style
        u.sp2_species = user.sp2_user.species
        u.sp2_player_json = user.sp2_user.json


@db_session
def update_battle_poll(battle_poll):
    u = select(u for u in UserTable if u.id == battle_poll.user.id).first()

    if u:
        u.push = True
        u.battle_poll = battle_poll.to_json()


@db_session
def get_started_push_poll():
    us = select(u for u in UserTable if u.push)

    polls = []
    for u in us:
        poll_dict = json.loads(u.battle_poll)
        poll = BattlePoll.de_json(poll_dict)
        polls.append(poll)

    return polls


@db_session
def get_started_push_poll_by_user_id(user_id):
    u = select(u for u in UserTable if u.id == user_id).first()
    poll_dict = json.loads(u.battle_poll)
    return BattlePoll.de_json(poll_dict)


@db_session
def update_push_to_false(user_id):
    u = select(u for u in UserTable if u.id == user_id).first()

    if u:
        u.push = False


@db_session
def reset_push_last_message_id(user_id):
    u = select(u for u in UserTable if u.id == user_id).first()

    if u:
        poll_dict = json.loads(u.battle_poll)
        poll = BattlePoll.de_json(poll_dict)
        poll.last_message_id = None
        u.battle_poll = poll.to_json()
