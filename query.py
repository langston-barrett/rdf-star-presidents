from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from pathlib import Path
from sys import exit
from time import sleep
from urllib.parse import quote

from requests import get

URL = "https://query.wikidata.org/bigdata/namespace/wdq/sparql?query="


def query_url(query: str) -> str:
    return URL + quote(query)


def run_query(query: str) -> str:
    sleep(1)
    return get(query_url(query), params={"format": "json"}).text


def get_results(query: str) -> list[dict[str, str]]:
    result_text = run_query(query)
    try:
        return [
            {bind: val["value"] for (bind, val) in d.items()}
            for d in loads(result_text)["results"]["bindings"]
        ]
    except JSONDecodeError as e:
        print("Couldn't decode response:")
        print(result_text)
        print(e)
        exit(1)

QUERY0 = """
SELECT DISTINCT ?pres ?presLabel ?start ?end ?ord ?pred ?succ ?vice
WHERE {
  ?pres p:P39 ?statement .
  ?statement ps:P39 wd:Q11696 .
  ?pres wdt:P31 wd:Q5 .

  OPTIONAL { ?statement pq:P580 ?start } .
  OPTIONAL { ?statement pq:P582 ?end } .
  OPTIONAL { ?statement pq:P1545 ?ord } .
  OPTIONAL { ?statement pq:P1365 ?pred } .
  OPTIONAL { ?statement pq:P1366 ?succ } .
  OPTIONAL {
    ?statement pq:P2715 ?election .
    ?vice p:P39 ?viceStatement .
    ?viceStatement ps:P39 wd:Q11699 .
    ?vice wdt:P31 wd:Q5 .
    ?viceStatement pq:P2715 ?election
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
ORDER BY ?ord
"""

VICE = """
SELECT DISTINCT ?item1 ?item1Label ?item2 ?item2Label ?starttime2 ?endtime2 
WHERE {
  ?item1 wdt:P31 wd:Q5 ; p:P39 ?statement1.
  ?statement1 ps:P39 wd:Q11696 ; pq:P580 ?starttime1. OPTIONAL{?statement1 pq:P582 ?endtime1.}
  BIND(IF(!BOUND(?endtime1), NOW(), ?endtime1) AS ?endtime1)
  ?item2 wdt:P31 wd:Q5 ; p:P39 ?statement2.
  ?statement2 ps:P39 wd:Q11699 ; pq:P580 ?starttime2. OPTIONAL{?statement2 pq:P582 ?endtime2.}
  BIND(IF(!BOUND(?endtime2), NOW(), ?endtime2) AS ?endtime2)
  BIND(MIN(?starttime1) AS ?minstarttime1)
  FILTER((?starttime2 < ?minstarttime1 && ?endtime2 >= ?endtime1) || ?starttime2 >= ?starttime1)
  FILTER(?starttime2 < ?endtime1)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} ORDER BY (?starttime1) (?starttime2)   
"""

PARENTS = """
SELECT DISTINCT ?president ?presidentLabel ?father ?fatherLabel ?mother ?motherLabel
WHERE {
  ?president p:P39 ?statement .
  ?statement ps:P39 wd:Q11696 .
  ?president wdt:P31 wd:Q5 .

  OPTIONAL { ?president wdt:P22 ?father } .
  OPTIONAL { ?president wdt:P25 ?mother } .

  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""

if __name__ == "__main__":
    query0_results = Path("raw/query0.json")
    if not query0_results.exists():
        data = get_results(QUERY0)
        assert len(data) == 46
        query0_results.write_text(dumps(data, indent=2))

    vice_results = Path("raw/vice.json")
    if not vice_results.exists():
        data = get_results(VICE)
        assert len(data) == 49
        vice_results.write_text(dumps(data, indent=2))

    parents_results = Path("raw/parents.json")
    if not parents_results.exists():
        data = get_results(PARENTS)
        assert len(data) == 45
        parents_results.write_text(dumps(data, indent=2))
 