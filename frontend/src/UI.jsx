import React, {useState, useEffect} from 'react';

export function Icon({name, size=20, ...props}) {
  const paths = {
    ball:<><circle cx="12" cy="12" r="9"/><path d="m12 7 4 3-1.5 5h-5L8 10zM12 3v4m9 3-5 0m2 10-3.5-5M6 20l3.5-5M3 10h5"/></>,
    search:<><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></>,
    arrow:<path d="M5 12h14m-6-6 6 6-6 6"/>,
    back:<path d="M19 12H5m6-6-6 6 6 6"/>,
    chart:<><path d="M4 4v16h16M8 15v-4m5 4V7m5 8V4"/></>,
    clock:<><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    info:<><circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v1"/></>,
    calendar:<><rect x="4" y="5" width="16" height="16" rx="3"/><path d="M8 3v4m8-4v4M4 11h16m-11 4h2m3 0h2"/></>,
    shield:<><path d="m12 3 8 3v6c0 4-5 8-8 9-3-1-8-5-8-9V6z"/><path d="m8 12 3 3 5-6"/></>,
    chevron:<path d="m9 5 7 7-7 7"/>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.chart}</svg>;
}
export function Crest({team}) {
  const [failed,setFailed]=useState(false);
  useEffect(()=>setFailed(false),[team?.crest]);
  const name=team?.name || 'Time';
  return typeof team?.crest==='string' && /^https:\/\//i.test(team.crest) && !failed
    ? <img className="crest" src={team.crest} alt="" loading="lazy" referrerPolicy="no-referrer" onError={()=>setFailed(true)}/>
    : <span className="crest crest-fallback" aria-hidden="true">{name.split(' ').filter(Boolean).slice(0,2).map(w=>w[0]).join('').toUpperCase()}</span>;
}
export function Brand(){return <span className="brand"><span className="brand-mark"><Icon name="chart" size={23}/></span><span>bet<span className="brand-light">analytics</span><small>FUTEBOL EM PERSPECTIVA</small></span></span>;}
