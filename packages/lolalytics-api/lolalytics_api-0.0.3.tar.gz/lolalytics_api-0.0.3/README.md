# Unofficial Lolalytics scraper  
[TBA] a lot of things

## Installation  
```bash
pip install lolalytics-api
```

## Functions  
### `get_tierlist`
- `def get_tierlist(n: int = 10, lane: str = '', rank: str = '')`  
*Empty rank is set by default to Emerald+  
*Empty lane is set by default to all lanes  
```json
{
  "0": {
      "rank": "1",
      "champion": "Ahri",
      "tier": "S+",
      "winrate": "52.73"
    },
  "1": {
      "rank": "2",
      "champion": "Yone",
      "tier": "S",
      "winrate": "50.92"
    }
}
```

### `get_counters`
- `def get_counters(n: int = 10, champion: str = '', rank: str = '')`  
*Empty rank is set by default to Emerald+
```json
{
  "0": {
      "champion": "Akali",
      "winrate": "47.91"
    }
}
```

### `display_ranks`
- `def display_ranks(display: bool = True)`  
Display all available ranks and their shortcuts.  
If display is True (default), prints the ranks to the console.  
Otherwise, returns a dict.

### `display_lanes`
- `def display_lanes(display: bool = True)`  
Same as above, but for lanes.
