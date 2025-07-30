import json
import requests
from lxml import html
from lolalytics_api.errors import InvalidLane, InvalidRank


def display_ranks(display: bool = True):
    """
    Display all available ranks and their shortcuts.
    :param display: If True (default), prints the ranks to the console. Otherwise, returns a dict.
    :return: None or dict of ranks if display is False.
    """
    rank_mappings = {
            '': '',
            'challenger': 'challenger',
            'chall': 'challenger',
            'c': 'challenger',
            'grandmaster_plus': 'grandmaster_plus',
            'grandmaster+': 'grandmaster_plus',
            'gm+': 'grandmaster_plus',
            'grandmaster': 'grandmaster',
            'grandm': 'grandmaster',
            'gm': 'grandmaster',
            'master_plus': 'master_plus',
            'master+': 'master_plus',
            'mast+': 'master_plus',
            'm+': 'master_plus',
            'master': 'master',
            'mast': 'master',
            'm': 'master',
            'diamond_plus': 'diamond_plus',
            'diamond+': 'diamond_plus',
            'diam+': 'diamond_plus',
            'dia+': 'diamond_plus',
            'd+': 'diamond_plus',
            'diamond': 'diamond',
            'diam': 'diamond',
            'dia': 'diamond',
            'd': 'diamond',
            'emerald': 'emerald',
            'eme': 'emerald',
            'em': 'emerald',
            'e': 'emerald',
            'platinum+': 'platinum_plus',
            'plat+': 'platinum_plus',
            'pl+': 'platinum_plus',
            'p+': 'platinum_plus',
            'platinum': 'platinum',
            'plat': 'platinum',
            'pl': 'platinum',
            'p': 'platinum',
            'gold_plus': 'gold_plus',
            'gold+': 'gold_plus',
            'g+': 'gold_plus',
            'gold': 'gold',
            'g': 'gold',
            'silver': 'silver',
            'silv': 'silver',
            's': 'silver',
            'bronze': 'bronze',
            'br': 'bronze',
            'b': 'bronze',
            'iron': 'iron',
            'i': 'iron',
            'unranked': 'unranked',
            'unrank': 'unranked',
            'unr': 'unranked',
            'un': 'unranked',
            'none': 'unranked',
            'null': 'unranked',
            '-': 'unranked',
            'all': 'all',
            '1trick': '1trick',
            '1-trick': '1trick',
            '1trickpony': '1trick',
            'onetrickpony': '1trick',
            'onetrick': '1trick',
        }
    if display:
        print("Available ranks and their shortcuts:")
        for rank, shortcut in rank_mappings.items():
            print(f"{rank}: {shortcut}")
    else:
        return rank_mappings


def display_lanes(display: bool = True):
    """
    Display all available lanes and their shortcuts.
    :param display: If True (default), prints the lanes to the console. Otherwise, returns a dict.
    :return: None or dict of lanes if display is False.
    """
    lane_mappings = {
        '': '',
        'top': 'top',
        'jg': 'jungle',
        'jng': 'jungle',
        'jungle': 'jungle',
        'mid': 'middle',
        'middle': 'middle',
        'bottom': 'bottom',
        'bot': 'bottom',
        'adc': 'bottom',
        'support': 'support',
        'supp': 'support',
        'sup': 'support'
    }
    if display:
        print("Available lanes and their shortcuts:")
        for lane, shortcut in lane_mappings.items():
            print(f"{lane}: {shortcut}")
    else:
        return lane_mappings


def _sort_by_rank(link: str, rank: str):
    """
    Update the link to sort by a specific rank.
    :param link: url to the page to sort.
    :param rank: sort by rank (see ``display_ranks()``).
    :return: new link with the rank filter applied.
    """
    rank_mappings = display_ranks(display=False)
    try:
        mapped_rank = rank_mappings[rank.lower()]
    except KeyError:
        raise InvalidRank(rank)

    if '?' in link:
        return f'{link}&tier={mapped_rank}'
    else:
        return f'{link}?tier={mapped_rank}'


def get_tierlist(n: int = 10, lane: str = '', rank: str = ''):
    """
    Get the top n champions in the tier list for a specific lane.
    :param n: number of champions to return.
    :param lane: lane to filter the tier list by (see ``display_lanes()``).
    :param rank: sort by rank (see ``display_ranks()``).
    :return: JSON containing rank, champion name, tier and winrate.
    """
    lane_mappings = display_lanes(display=False)
    try:
        mapped_lane = lane_mappings[lane.lower()]
    except KeyError:
        raise InvalidLane(lane)

    base_url = 'https://lolalytics.com/lol/tierlist/'
    if mapped_lane:
        tierlist = f'{base_url}?lane={mapped_lane}'
    else:
        tierlist = base_url

    if rank:
        tierlist = _sort_by_rank(tierlist, rank)

    tierlist_html = requests.get(tierlist)
    tree = html.fromstring(tierlist_html.content)
    result = {}

    for i in range(3, n + 3):
        rank_xpath = f'/html/body/main/div[6]/div[{i}]/div[1]'
        champion_xpath = f'/html/body/main/div[6]/div[{i}]/div[3]/a'
        tier_xpath = f'/html/body/main/div[6]/div[{i}]/div[4]'
        winrate_xpath = f'/html/body/main/div[6]/div[{i}]/div[6]/div/span[1]'

        rank = tree.xpath(rank_xpath)[0].text_content().strip()
        champion = tree.xpath(champion_xpath)[0].text_content().strip()
        tier = tree.xpath(tier_xpath)[0].text_content().strip()
        winrate = tree.xpath(winrate_xpath)[0].text_content().strip()

        result[i - 3] = {
            'rank': rank,
            'champion': champion,
            'tier': tier,
            'winrate': winrate
        }

    return json.dumps(result, indent=4)


def get_counters(n: int = 10, champion: str = '', rank: str = ''):
    """
    Get the top n counters for a specific champion.
    :param n: number of counters to return.
    :param champion: champion to filter the counters by.
    :param rank: sort by rank (see ``display_ranks()``).
    :return: JSON containing counter champion name and winrate (vs the counter).
    """
    if champion == '':
        raise ValueError("Champion name cannot be empty")

    counters = f'https://lolalytics.com/lol/{champion}/counters/'
    if rank:
        counters = _sort_by_rank(counters, rank)

    counters_html = requests.get(counters)
    tree = html.fromstring(counters_html.content)
    result = {}

    for i in range(1, n + 1):
        champion_xpath = f'/html/body/main/div[6]/div[1]/div[2]/span[{i}]/div[1]/a/div/div[1]'
        winrate_xpath = f'/html/body/main/div[6]/div[1]/div[2]/span[{i}]/div[1]/a/div/div[2]/div'

        champion_name = tree.xpath(champion_xpath)[0].text_content().strip()
        winrate = tree.xpath(winrate_xpath)[0].text_content().strip()

        result[i - 1] = {
            'champion': champion_name,
            'winrate': winrate.split('%')[0]
        }

    return json.dumps(result, indent=4)
