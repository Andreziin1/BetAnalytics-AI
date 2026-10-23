"""Validação real, consumindo até 5 chamadas externas. Execute na raiz."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
from datetime import datetime, timezone
from backend.config import Settings
from backend.api.football_api import FootballClient, ProviderError, DEFAULT_COMPETITIONS
from backend.analytics.team_analysis import analyze_team, analyze_head_to_head, parse_date

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--competition',choices=DEFAULT_COMPETITIONS,default='PL')
    args=parser.parse_args()
    client=FootballClient(Settings.from_env())
    try:
        now=datetime.now(timezone.utc)
        listing=client.upcoming(7,(args.competition,),now)
        result={'competition':args.competition,'matches_found':len(listing['matches']),'checked_at':now.isoformat()}
        if listing['matches']:
            mid=listing['matches'][0]['id'];match=client.get(f'/matches/{mid}');cutoff=min(now,parse_date(match['utcDate']))
            result['match_id']=mid;result['sections']={}
            for side,key in [('home','homeTeam'),('away','awayTeam')]:
                team=match[key]
                try:
                    rows=client.team_history(team['id'],cutoff)['matches']
                    analysis=analyze_team(team['id'],team['name'],rows,cutoff=cutoff,exclude_id=mid)
                    result['sections'][side]={'sample':analysis['matches_analyzed'],'complete':analysis['sample_complete']}
                except ProviderError as exc:result['sections'][side]={'error':exc.code}
            try:
                rows=client.h2h(mid)['matches'];h=analyze_head_to_head(rows,match['homeTeam']['id'],match['awayTeam']['id'],cutoff=cutoff,exclude_id=mid)
                result['sections']['h2h']={'sample':h['matches_analyzed'],'complete':h['sample_complete']}
            except ProviderError as exc:result['sections']['h2h']={'error':exc.code}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return int(any('error' in s for s in result.get('sections',{}).values()))
    except ProviderError as exc:
        print(json.dumps({'error':exc.code,'message':exc.message},ensure_ascii=False));return 1
    finally:client.close()
if __name__=='__main__':raise SystemExit(main())
