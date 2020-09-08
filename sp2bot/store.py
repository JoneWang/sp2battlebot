#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from sqlalchemy import Column, String, create_engine, Integer, Boolean, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import configs
from sp2bot.models import User, BattlePoll

# Create database
Base = declarative_base()


# Table
class UserTable(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(), unique=True, nullable=True)
    first_name = Column(String(), nullable=False)
    last_name = Column(String(), nullable=True)
    push = Column(Boolean(), default=False)
    iksm_session = Column(String(), nullable=True)
    session_token = Column(String(), nullable=True)
    sp2_principal_id = Column(String(), nullable=True)
    sp2_nickname = Column(String(), nullable=True)
    sp2_style = Column(String(), nullable=True)
    sp2_species = Column(String(), nullable=True)
    battle_poll = Column(Text(), nullable=True)


engine = create_engine(configs.DATABASE_URI)

Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)


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
              )


def select_users_with_principal_ids(principal_ids):
    session = DBSession()
    us = session.query(UserTable) \
        .filter(UserTable.sp2_principal_id.in_(principal_ids)).all()
    session.close()

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
                          ))
    return users


def select_user(user_id):
    session = DBSession()
    result = session.query(UserTable) \
        .filter(UserTable.id == user_id)
    u = result.one() if result.count() > 0 else None
    session.close()
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
                    )
    else:
        return None


def select_all_users():
    session = DBSession()
    us = session.query(UserTable).all()
    session.close()
    users = []
    for u in us:
        users.append(
            User(u.id,
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
                 )
        )

    return users


def update_user(user):
    session = DBSession()
    result = session.query(UserTable) \
        .filter(UserTable.id == user.id)
    u = result.one() if result.count() > 0 else None

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

    session.commit()
    session.close()


def update_battle_poll(battle_poll):
    session = DBSession()
    result = session.query(UserTable) \
        .filter(UserTable.id == battle_poll.id)
    u = result.one() if result.count() > 0 else None

    if u:
        u.push = True
        u.battle_poll = battle_poll.to_json()

    session.commit()
    session.close()


def get_started_push_poll():
    session = DBSession()
    us = session.query(UserTable)\
        .filter(UserTable.push == True).all()
    session.close()

    polls = []
    for u in us:
        poll_dict = json.loads(u.battle_poll)
        poll = BattlePoll.de_json(poll_dict)
        polls.append(poll)

    return polls


def update_push_to_false(user_id):
    session = DBSession()
    result = session.query(UserTable) \
        .filter(UserTable.id == user_id)
    u = result.one() if result.count() > 0 else None

    if u:
        u.push = False

    session.commit()
    session.close()
