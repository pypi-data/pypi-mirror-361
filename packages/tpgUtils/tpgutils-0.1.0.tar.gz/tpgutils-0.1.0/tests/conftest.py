import pytest
import os
from collections import Counter
from src import config as cfg
from src.card import Card
from src.event import Event

""" Central repository for Pytest fixtures for breakout groups."""

@pytest.fixture(scope='session')
def create_folders(tmp_path_factory):
    """this is a setup/teardown example"""
    # set_up: set paths
    base_dir = tmp_path_factory.mktemp("breakout_groups")
    base_dir = base_dir / "data"
    base_dir.mkdir()
    cfg.datadir = str(base_dir) + os.sep

    # yield, to let all tests within the scope
    yield

    # tear_down: remove test dir & files
    # if os.path.exists(tmp_path_factory):
    #     for pth, dir, files in os.walk(tmp_path_factory):
    #         for d in dir:
    #             for fl in files:
    #                 os.remove(f"{tmp_path_factory}{os.sep}{d}{fl}")
    #         for fl in files:
    #             os.remove(f"{tmp_path_factory}{fl}")
    #     os.rmdir(tmp_path_factory)

@pytest.fixture
def get_config():
    """Parses the configuration file values and returns them in a dict"""
    config = cfg.cp.read_config_file(cfg.config)
    config_values = {}
    config_values['n_attendees'] = config.getint('EVENT','n_attendees')
    config_values['group_size'] = config.getint('EVENT','group_size')
    config_values['n_groups'] = config.getint('EVENT','n_groups')
    config_values['n_sessions'] = config.getint('EVENT','n_sessions')
    return config_values

@pytest.fixture
def config_event_defaults():
    """set cfg variables to EVENT values"""
    cfg.event_title = "Pytest Run title"
    cfg.event_subtitle = "Pytest Run subtitle"
    cfg.event_date = "yyyy/mm/dd - yyyy/mm/dd"
    cfg.n_attendees = 11
    cfg.n_groups = 3
    cfg.orig_n_groups = cfg.n_groups
    cfg.group_size = 3
    cfg.n_sessions = 4
    cfg.n_extra_cards = 2
    cfg.attendees_list = cfg.cp.gen_attendees_list()
    cfg.group_labels = []
    cfg.group_labels.append(["group1","group2","group3","group4","group5"])
    cfg.group_labels.append(["blue","red","green","yellow","pink"])
    cfg.group_labels.append(["Portales","Santa Fe","Taos","Chama","Cuba"])
    cfg.group_labels.append(["Elbert","Massive","Harvard","Blanca","La Plata"])
    cfg.session_labels = ['Fri 9:00pm', 'Sat 9:00', 'Sat 11:00am', 'Session 04']
    cfg.sys_group_algorithm = 'sessions_random'
    cfg.sys_group_algorithm_class = 'SessionsRandom'
    cfg.sys_algorithm_compare = ['sessions_random','SessionsRandom','sessions_random_interactions','SessionsRandomInteractions']

    """

    0:  ['0:4', '1:1', '2:0', '3:2', '4:0', '5:2', '6:2', '7:1', '8:0', '9:2', '10:0']
    1:  ['0:1', '1:4', '2:2', '3:1', '4:1', '5:1', '6:0', '7:3', '8:0', '9:1', '10:0']
    2:  ['0:0', '1:2', '2:4', '3:0', '4:3', '5:1', '6:1', '7:1', '8:2', '9:0', '10:1']
    3:  ['0:2', '1:1', '2:0', '3:4', '4:0', '5:2', '6:1', '7:1', '8:0', '9:4', '10:1']
    4:  ['0:0', '1:1', '2:3', '3:0', '4:4', '5:1', '6:2', '7:0', '8:3', '9:0', '10:2']
    5:  ['0:2', '1:1', '2:1', '3:2', '4:1', '5:4', '6:1', '7:0', '8:0', '9:2', '10:1']
    6:  ['0:2', '1:0', '2:1', '3:1', '4:2', '5:1', '6:4', '7:0', '8:2', '9:1', '10:1']
    7:  ['0:1', '1:3', '2:1', '3:1', '4:0', '5:0', '6:0', '7:4', '8:1', '9:1', '10:1']
    8:  ['0:0', '1:0', '2:2', '3:0', '4:3', '5:0', '6:2', '7:1', '8:4', '9:0', '10:3']
    9:  ['0:2', '1:1', '2:0', '3:4', '4:0', '5:2', '6:1', '7:1', '8:0', '9:4', '10:1']
    10:  ['0:0', '1:0', '2:1', '3:1', '4:2', '5:1', '6:1', '7:1', '8:3', '9:1', '10:4']
    Session 00 -  [[1, 7, 9, 3], [0, 5, 6], [2, 4, 8, 10]]
    Session 01 - [[7, 8, 10], [3, 6, 9, 0], [1, 4, 5, 2]]
    Session 02 - [[3, 5, 9, 0], [1, 2, 7], [4, 6, 8, 10]]
    Session 03 - [[2, 4, 6, 8], [0, 1, 7], [3, 5, 9, 10]]
    """
    cfg.all_card_interactions = {
        0: Counter({0:0, 1:1, 2:0, 3:2, 4:0, 5:2, 6:2, 7:1, 8:0, 9:2, 10:0}),
        1: Counter({0:1, 1:0, 2:2, 3:1, 4:1, 5:1, 6:0, 7:3, 8:0, 9:1, 10:0}),
        2: Counter({0:0, 1:2, 2:0, 3:0, 4:3, 5:1, 6:1, 7:1, 8:2, 9:0, 10:1}),
        3: Counter({0:2, 1:1, 2:0, 3:0, 4:0, 5:2, 6:1, 7:1, 8:0, 9:4, 10:1}),
        4: Counter({0:0, 1:1, 2:3, 3:0, 4:0, 5:1, 6:2, 7:0, 8:3, 9:0, 10:2}),
        5: Counter({0:2, 1:1, 2:1, 3:2, 4:1, 5:0, 6:1, 7:0, 8:0, 9:2, 10:1}),
        6: Counter({0:2, 1:0, 2:1, 3:1, 4:2, 5:1, 6:0, 7:0, 8:2, 9:1, 10:1}),
        7: Counter({0:1, 1:3, 2:1, 3:1, 4:0, 5:0, 6:0, 7:0, 8:1, 9:1, 10:1}),
        8: Counter({0:0, 1:0, 2:2, 3:0, 4:3, 5:0, 6:2, 7:1, 8:0, 9:0, 10:3}),
        9: Counter({0:2, 1:1, 2:0, 3:4, 4:0, 5:2, 6:1, 7:1, 8:0, 9:0, 10:1}),
       10: Counter({0:0, 1:0, 2:1, 3:1, 4:2, 5:1, 6:1, 7:1, 8:3, 9:1, 10:0}),
        }

    cfg.sessions = {
        0 : [[1, 7, 9, 3], [0, 5, 6], [2, 4, 8, 10]],
        1 : [[7, 8, 10], [3, 6, 9, 0], [1, 4, 5, 2]],
        2 : [[3, 5, 9, 0], [1, 2, 7], [4, 6, 8, 10]],
        3 : [[2, 4, 6, 8], [0, 1, 7], [3, 5, 9, 10]],
        }

    sess_lables = [
        ['group2', 'red', 'Portales', 'Massive'],
        ['group1', 'green', 'Santa Fe', 'Massive'],
        ['group3', 'green', 'Santa Fe', 'Elbert'],
        ['group1', 'red', 'Portales', 'Harvard'],
        ['group3', 'green', 'Taos', 'Elbert'],
        ['group2', 'green', 'Portales', 'Harvard'],
        ['group2', 'red', 'Taos', 'Elbert'],
        ['group1', 'blue', 'Santa Fe', 'Massive'],
        ['group3', 'blue', 'Taos', 'Elbert'],
        ['group1', 'red', 'Portales', 'Harvard'],
        ['group3', 'blue', 'Taos', 'Harvard'],
        ]
    # all_cards is a list of all card objects
    cfg.all_cards = []
    for i in range(cfg.n_attendees):
        card = Card(i)
        card.card_interactions = cfg.all_card_interactions[i]
        card.group_labels = sess_lables[i]
        cfg.all_cards.append(card)

    return cfg

@pytest.fixture
def get_random_seed():
    return 3331

@pytest.fixture
def event_cards(config_event_defaults, get_random_seed):
    event = Event(seed=get_random_seed)
    event.run()
    n_attendees = cfg.n_attendees
    n_groups = cfg.n_groups

    return event.all_cards

