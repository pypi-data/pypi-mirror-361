import requests
from lxml import html
import json


def get_tierlist(n: int = 10, lane: str = ''):
    """
    Get the top n champions in the tier list for a specific lane.
    :param n: Number of champions to return.
    :param lane: Lane to filter the tier list by.
    :return: JSON containing rank, champion name, tier and winrate.
    """
    # shortcuts
    if lane == '':
        tierlist = requests.get('https://lolalytics.com/lol/tierlist/')
    elif lane == 'top':
        tierlist = requests.get('https://lolalytics.com/lol/tierlist/?lane=top')
    elif lane in ['jg', 'jng', 'jungle']:
        tierlist = requests.get('https://lolalytics.com/lol/tierlist/?lane=jungle')
    elif lane in ['mid', 'middle']:
        tierlist = requests.get('https://lolalytics.com/lol/tierlist/?lane=middle')
    elif lane in ['bottom', 'bot', 'adc']:
        tierlist = requests.get('https://lolalytics.com/lol/tierlist/?lane=bottom')
    elif lane in ['support', 'sup', 'supp']:
        tierlist = requests.get('https://lolalytics.com/lol/tierlist/?lane=support')
    else:
        raise ValueError("Invalid lane")

    tree = html.fromstring(tierlist.content)
    result = {}

    for i in range(3, n+3):
        rank_xpath = f'/html/body/main/div[6]/div[{i}]/div[1]'
        champion_xpath = f'/html/body/main/div[6]/div[{i}]/div[3]/a'
        tier_xpath = f'/html/body/main/div[6]/div[{i}]/div[4]'
        winrate_xpath = f'/html/body/main/div[6]/div[{i}]/div[6]/div/span[1]'

        rank = tree.xpath(rank_xpath)[0].text_content().strip()
        champion = tree.xpath(champion_xpath)[0].text_content().strip()
        tier = tree.xpath(tier_xpath)[0].text_content().strip()
        winrate = tree.xpath(winrate_xpath)[0].text_content().strip()

        result[i-3] = {
            'rank': rank,
            'champion': champion,
            'tier': tier,
            'winrate': winrate
        }

    return json.dumps(result, indent=4)


def get_counters(n: int = 10, champion: str = ''):
    """
    Get the top n counters for a specific champion.
    :param n: Number of counters to return.
    :param champion: Champion to filter the counters by.
    :return: JSON containing counter champion name and winrate (vs the counter).
    """
    if champion == '':
        raise ValueError("Champion name cannot be empty")

    counters = requests.get(f'https://lolalytics.com/lol/{champion}/counters/')
    tree = html.fromstring(counters.content)
    result = {}

    for i in range(1, n+1):
        champion_xpath = f'/html/body/main/div[6]/div[1]/div[2]/span[{i}]/div[1]/a/div/div[1]'
        winrate_xpath = f'/html/body/main/div[6]/div[1]/div[2]/span[{i}]/div[1]/a/div/div[2]/div'

        champion_name = tree.xpath(champion_xpath)[0].text_content().strip()
        winrate = tree.xpath(winrate_xpath)[0].text_content().strip()

        result[i-1] = {
            'champion': champion_name,
            'winrate': winrate.split('%')[0]
        }

    return json.dumps(result, indent=4)
