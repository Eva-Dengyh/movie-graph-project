import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Search, Sparkles, Network, Compass, Send, ZoomIn, ZoomOut, Crosshair, Film, Users, Link2 } from 'lucide-react';
import './styles.css';

type Kind = 'movie' | 'person' | 'genre';
type Node = { id: string; label: string; kind: Kind; x: number; y: number; sub?: string };
const nodes: Node[] = [
  { id:'dune', label:'DUNE', kind:'movie', x:50, y:51, sub:'2021 · FILM' },
  { id:'villeneuve', label:'Denis Villeneuve', kind:'person', x:23, y:23, sub:'DIRECTOR' },
  { id:'chalamet', label:'Timothée Chalamet', kind:'person', x:78, y:24, sub:'ACTOR' },
  { id:'scifi', label:'SCI-FI', kind:'genre', x:16, y:68 },
  { id:'adventure', label:'ADVENTURE', kind:'genre', x:84, y:69 },
  { id:'blade', label:'Blade Runner 2049', kind:'movie', x:36, y:86 },
  { id:'arrival', label:'Arrival', kind:'movie', x:68, y:86 },
  { id:'rebecca', label:'Rebecca Ferguson', kind:'person', x:43, y:18 },
  { id:'isaac', label:'Oscar Isaac', kind:'person', x:59, y:18 },
];
const edges = [['dune','villeneuve','DIRECTED'],['dune','chalamet','ACTED IN'],['dune','scifi','HAS GENRE'],['dune','adventure','HAS GENRE'],['dune','blade','SAME DIRECTOR'],['dune','arrival','SAME DIRECTOR'],['dune','rebecca','ACTED IN'],['dune','isaac','ACTED IN'],['villeneuve','blade','DIRECTED'],['villeneuve','arrival','DIRECTED']];

function App(){
  const [selected,setSelected]=useState('dune'); const [query,setQuery]=useState(''); const [zoom,setZoom]=useState(1); const [question,setQuestion]=useState(''); const [sent,setSent]=useState(false);
  const selectedNode = nodes.find(n=>n.id===selected) ?? nodes[0];
  const visible = useMemo(()=>nodes.filter(n=>!query || n.label.toLowerCase().includes(query.toLowerCase())),[query]);
  const connected = (id:string) => edges.some(e=>e[0]===id||e[1]===id);
  return <div className="app">
    <aside className="sidebar"><div className="brand"><span className="brand-mark">✦</span><span>ORBI<span className="gold">T</span></span></div><nav><button className="active"><Network size={17}/><span>Knowledge Graph</span></button><button><Compass size={17}/><span>Explore Movies</span></button><button><Sparkles size={17}/><span>AI Questions</span></button></nav><div className="sync"><b>Knowledge base</b><br/><span className="cyan">●</span> 2,438 nodes synced<br/><small>LAST SYNC / 08:42</small></div></aside>
    <main className="main"><header><div className="crumb">WORKSPACE / <b>Movie Knowledge Graph</b></div><div className="avatar">ED</div></header>
      <section className="hero"><div><div className="eyebrow cyan">● LIVE KNOWLEDGE UNIVERSE</div><h1>See the movies<br/>between <em>the lines.</em></h1><p>Explore stories, people and genres as a living network of connected knowledge.</p></div><div className="search"><Search size={16}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search movies, people or genres..."/><span>⌘ K</span></div></section>
      <section className="stats"><Stat icon={<Film/>} label="MOVIES" value="4,587" change="+12.4%"/><Stat icon={<Users/>} label="PEOPLE" value="22,937" change="+8.7%"/><Stat icon={<Link2/>} label="RELATIONS" value="58.2K" change="+21.1%"/><Stat icon={<Sparkles/>} label="AI QUERIES" value="1,204" change="LIVE"/></section>
      <section className="grid"><article className="panel graph-panel"><div className="panel-head"><div><h2>Relationship graph</h2><small>Focus: <b>{selectedNode.label}</b></small></div><span className="eyebrow">{nodes.length} NODES · {edges.length} EDGES</span></div><div className="graph" style={{'--scale':zoom} as React.CSSProperties}><svg viewBox="0 0 100 100" preserveAspectRatio="none">{edges.map(([a,b,label],i)=>{const na=nodes.find(n=>n.id===a)!;const nb=nodes.find(n=>n.id===b)!;const hot=a===selected||b===selected;return <g key={i}><line className={hot?'edge hot':'edge'} x1={na.x} y1={na.y} x2={nb.x} y2={nb.y}/><text className="edge-label" x={(na.x+nb.x)/2} y={(na.y+nb.y)/2-1}>{hot?label:''}</text></g>})}</svg>{nodes.map(n=><button key={n.id} className={`node ${n.kind} ${n.id===selected?'selected':''} ${query && !visible.includes(n)?'dim':''}`} style={{left:`${n.x}%`,top:`${n.y}%`}} onClick={()=>setSelected(n.id)}><i>{n.kind==='movie'?'✦':n.kind==='person'?'●':'◆'}</i><b>{n.label}</b>{n.sub&&<small>{n.sub}</small>}</button>)}<div className="graph-controls"><button onClick={()=>setZoom(z=>Math.min(1.4,z+.1))}><ZoomIn size={15}/></button><button onClick={()=>setZoom(z=>Math.max(.8,z-.1))}><ZoomOut size={15}/></button><button onClick={()=>{setZoom(1);setSelected('dune')}}><Crosshair size={15}/></button></div><div className="legend"><span><i className="movie-dot"/>Movie</span><span><i className="person-dot"/>Person</span><span><i className="genre-dot"/>Genre</span></div></div></article>
        <aside className="right"><article className="panel detail"><div className="panel-head"><h2>Node detail</h2><span className="eyebrow">SELECTED</span></div><div className="detail-body"><div className="poster"><span>DUNE</span></div><div><small className="eyebrow">FEATURED FILM · 2021</small><h3>{selectedNode.label}</h3><p>{selectedNode.kind==='movie'?'A journey across sand, stars and inherited destiny.':`${selectedNode.kind.toUpperCase()} node connected to ${edges.filter(e=>e.includes(selectedNode.id)).length} relationships.`}</p><div className="chips"><span>SCI-FI</span><span>ADVENTURE</span></div></div></div><div className="facts"><div><small>TYPE</small><b>{selectedNode.kind}</b></div><div><small>CONNECTIONS</small><b>{edges.filter(e=>e.includes(selectedNode.id)).length} edges</b></div><div><small>STATUS</small><b className="cyan">Verified</b></div><div><small>ORIGIN</small><b>Movie DB</b></div></div></article>
        <article className="panel chat"><div className="panel-head"><div><h2>Orbit AI</h2><small>Graph-grounded answers</small></div><span className="pulse"/></div><div className="messages"><div className="bubble">Find the collaboration path between Denis Villeneuve and Timothée Chalamet.</div><div className="bubble ai">They are connected through <b>3 films</b>, including Dune and Dune: Part Two.<div className="sources">#Dune　#Collaboration path</div></div>{sent&&<div className="bubble ai">I mapped the relevant subgraph and highlighted the connected nodes.</div>}</div><form onSubmit={e=>{e.preventDefault();if(question.trim()){setSent(true);setQuestion('')}}}><input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask the graph..."/><button><Send size={15}/></button></form></article></aside>
      </section><section className="panel recommendations"><div className="panel-head"><div><h2>Curated from this graph</h2><small>Agent recommendations based on relationship paths</small></div><button className="link">Refresh ↗</button></div><div className="rec-list"><Rec title="Blade Runner 2049" text="Same director · visual storytelling" score="94%"/><Rec title="Arrival" text="Same director · science fiction" score="89%"/><Rec title="The Northman" text="Epic narrative · visual style" score="82%"/></div></section>
    </main><nav className="mobile-nav"><button className="active"><Network size={18}/>Graph</button><button><Compass size={18}/>Explore</button><button><Sparkles size={18}/>AI</button></nav>
  </div>
}
function Stat({icon,label,value,change}:{icon:React.ReactNode;label:string;value:string;change:string}){return <div className="stat"><div className="stat-top"><span>{icon}</span><small>{label}</small></div><strong>{value}</strong><em>{change}</em></div>}
function Rec({title,text,score}:{title:string;text:string;score:string}){return <div className="rec"><div className="mini-poster"/><div><b>{title}</b><p>{text}</p><em>Match {score}</em></div></div>}
createRoot(document.getElementById('root')!).render(<App/>);
