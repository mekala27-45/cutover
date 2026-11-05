"use client";
import {useEffect,useState} from "react";
type Criterion={id:string;sentence:string;verdict:string;reason:string;threshold:number};
type Manifest={criteria:Criterion[];arms:{arm:string;status:string}[];limitations:string[];status:string;manifest_digest:string};
type Decision={action:string;reason:string;queue:string;scores:Record<string,number>};
type Receipt={receipt_id:string;release:string;mode:string;model_ready:boolean;decision:Decision};
const statement="cutover is a portfolio demonstration. Its customer is fictional, and public NHTSA vehicle complaints stand in for that customer inbox. It is not affiliated with NHTSA or any vehicle maker, it makes no safety determination, and it is not for safety, legal or regulatory use. It never closes a complaint: it routes one to a team or sends it to a person. Its costs are shadow prices from public list prices.";
const nav=[["verdict","The verdict"],["criteria","Criteria"],["discovery","Discovery"],["arms","Arms"],["cascade","Cascade"],["safety","Safety"],["shadow","Shadow"],["canary","Canary"],["handover","Handover"],["cost","Cost"],["try","Try triage"],["data","Data"],["report","Report"]];
const copy:Record<string,[string,string,string]>={
 verdict:["Evidence before rollout.","A complaint can reach a team or a person. Every release must earn its place.","Public complaint data cannot establish performance in a real customer inbox."],
 criteria:["The contract comes first.","Frozen criteria, a named owner and the evidence behind each verdict.","A registered criterion is a commitment to measure. It is not a passing result."],
 discovery:["Read the inbox.","Temporal source coverage, component labels and the limits of filed reports.","Owner-filed labels can be incomplete or inconsistent. They are not engineering judgments."],
 arms:["Five ways to triage.","The floor, encoder, prompted small model, recorded incumbent and cascade are reported separately.","A software test is not model performance. Every model arm needs its own execution evidence."],
 cascade:["Escalate the uncertainty.","A safety guard runs before routing. Unsure live cases reach a person.","The live API never calls the recorded incumbent. It cannot inherit that arm's measured performance."],
 safety:["Give the difficult case to a person.","Safety keywords override a confident routing prediction.","The guard is not a safety determination, and absence of a keyword cannot establish safety."],
 shadow:["Watch the newest months.","Time-ordered replay and delayed-label monitoring belong beside the headline scores.","A replay is not live customer traffic. Drift evidence applies only to the measured window."],
 canary:["A way back, before go-live.","Stable assignment, an independent kill switch and rollback by artifact digest.","Passing synthetic monitor tests does not establish that real bad model releases are detected."],
 handover:["Leave a system someone can run.","The contract, evidence, runbook and open risks travel together.","This fictional engagement does not include interviews with real analysts or an operational on-call team."],
 cost:["Show the quality bill.","Cost comparisons must use measured compute and a dated price book.","Shadow prices and analyst minutes are estimates. No savings claim is established yet."],
 try:["Triage one complaint.","Use an authored test narrative to inspect the current API state.","The current service is a guard-only demonstration until a checked model is promoted."],
 data:["Know what crossed the boundary.","Personal fields are dropped before writing. Public results contain aggregates only.","Bounded data processing and privacy tests do not certify the source's labels or completeness."],
 report:["The cutover briefing.","Read the current evidence and remaining release requirements.","The project remains in development while any mandatory evidence is missing."]
};
async function readJson(url:string,init?:RequestInit){
 let last:Response|undefined;
 for(let attempt=0;attempt<2;attempt++){
   last=await fetch(url,{...init,signal:AbortSignal.timeout(15000)});
   if(last.ok)return last.json();
   if(last.status!==503)break;
 }
 throw new Error(last?.status===503?"The service is unavailable. No triage was confirmed.":last?.status===429?"The hourly request budget has been reached.":"The request could not be completed.");
}
export default function Sheet({section}:{section:string}){
 const [manifest,setManifest]=useState<Manifest|null>(null);
 const [loadError,setLoadError]=useState("");
 const [dark,setDark]=useState(false);
 const [text,setText]=useState("Smoke came from the engine while the vehicle was being driven.");
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 const [receipt,setReceipt]=useState<Receipt|null>(null);
 const [showSource,setShowSource]=useState(false);
 const [apiStatus,setApiStatus]=useState("Checking API");
 const api=process.env.NEXT_PUBLIC_API_URL||"";
 useEffect(()=>{readJson("/cutover/manifest.json").then(setManifest).catch(()=>setLoadError("Evidence could not be loaded. Reload to retry."));},[]);
 useEffect(()=>{document.documentElement.dataset.theme=dark?"dark":"light";},[dark]);
 useEffect(()=>{if(!api){setApiStatus("API connection pending");return;}readJson(api+"/health").then(v=>setApiStatus(v.model_ready?"Model ready":"Guard only")).catch(()=>setApiStatus("API unavailable"));},[api]);
 async function submit(){
  setBusy(true);setError("");setReceipt(null);
  try{if(!api)throw new Error("The API connection is not configured.");
      setReceipt(await readJson(api+"/v1/triage",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({narrative:text})}));}
  catch(e){setError(e instanceof Error?e.message:"Request failed.");}finally{setBusy(false);}
 }
 const [title,subtitle,pushback]=copy[section]||copy.verdict;
 return <div className="shell">
  <a href="#main" className="skip">Skip to content</a>
  <header><a className="brand" href="/cutover/"><span className="brandMark">C</span> CUTOVER <span className="edition">FIELD NOTES / 23</span></a><div className="headerRight"><span className="status"><i/>{apiStatus}</span><button onClick={()=>setDark(!dark)} aria-label={dark?"Switch to light theme":"Switch to dark theme"}>{dark?"Light mode":"Dark mode"}</button></div></header>
  <div className="workspace"><aside><p className="eyebrow">ENGAGEMENT RUN SHEET</p><nav aria-label="Main navigation">{nav.map(([key,label],i)=><a key={key} href={key==="verdict"?"/cutover/":"/cutover/"+key+"/"} aria-current={section===key?"page":undefined}><span>{String(i+1).padStart(2,"0")}</span>{label}{section===key&&<b>→</b>}</a>)}</nav><div className="asideFoot">PUBLIC DATA<br/>FICTIONAL CUSTOMER<br/>EVIDENCE REQUIRED</div></aside>
  <main id="main"><div className="kicker"><span>VEHICLE COMPLAINT TRIAGE</span><span className="phase">IN DEVELOPMENT</span></div>
  <h1>{title}</h1><p className="lead">{subtitle}</p>
  <section className="notice" aria-label="Completion status"><strong>Release hold</strong><p>No fitted encoder or recorded language model has been promoted. Model quality, cost savings and rollout success remain unmeasured.</p></section>
  {loadError?<p role="alert">{loadError}</p>:!manifest?<p role="status" className="loading">Loading evidence sheet…</p>:<>
    {["verdict","criteria","report"].includes(section)&&<section><div className="sectionHead"><h2>Success criteria</h2><button onClick={()=>setShowSource(!showSource)}>{showSource?"Hide source":"Show source"}</button></div>
    <div className="criteriaStrip">{manifest.criteria.map(c=><a href="/cutover/criteria/" key={c.id}><span>{c.id}</span><strong>◻ {c.verdict.replaceAll("_"," ")}</strong></a>)}</div>
    <div className="tableWrap"><table><thead><tr><th scope="col">Criterion</th><th scope="col">The commitment</th><th scope="col">Evidence</th></tr></thead><tbody>{manifest.criteria.map(c=><tr key={c.id}><th scope="row">{c.id}</th><td>{c.sentence}</td><td><span className="unmeasured">{c.verdict.replaceAll("_"," ")}</span><small>{c.reason}</small></td></tr>)}</tbody></table></div>{showSource&&<pre>{JSON.stringify({source:"config/criteria.yaml",manifest_digest:manifest.manifest_digest,criteria:manifest.criteria},null,2)}</pre>}</section>}
    {section==="try"&&<section className="try"><div className="sectionHead"><h2>Inspect a triage</h2><span className="mode">LIVE REQUEST</span></div><p>Use test text. The service stores a text digest and decision receipt, never the narrative.</p><label htmlFor="narrative">Complaint narrative</label><textarea id="narrative" value={text} onChange={e=>setText(e.target.value)} maxLength={16000} rows={6}/><div className="buttons"><button onClick={()=>setText("The steering became difficult while parking the vehicle.")}>Steering example</button><button onClick={()=>setText("Smoke came from the engine while the vehicle was being driven.")}>Smoke example</button><button className="primary" disabled={busy||text.trim().length<20||!api} onClick={submit}>{busy?"Waiting for receipt…":"Request triage →"}</button></div>{!api&&<p className="unmeasured">API setup is pending.</p>}{error&&<p role="alert">{error}</p>}{receipt&&<div aria-live="polite" className="receipt"><p className="eyebrow">{receipt.mode.toUpperCase()}</p><h3>{receipt.decision.action==="send_to_analyst"?"Send to an analyst":"Route to "+receipt.decision.queue}</h3><dl><dt>Reason</dt><dd>{receipt.decision.reason.replaceAll("_"," ")}</dd><dt>Release</dt><dd>{receipt.release}</dd><dt>Receipt</dt><dd>{receipt.receipt_id}</dd></dl><p>A receipt confirms a committed log entry. It does not establish model accuracy.</p></div>}</section>}
    {["arms","verdict"].includes(section)&&<section><h2>Execution ledger</h2><div className="tableWrap"><table><thead><tr><th>Method</th><th>Evidence state</th><th>Measured quality</th></tr></thead><tbody>{manifest.arms.map(a=><tr key={a.arm}><th>{a.arm.replaceAll("_"," ")}</th><td>{a.status.replaceAll("_"," ")}</td><td>Not available</td></tr>)}</tbody></table></div></section>}
    {section==="canary"&&<section><h2>Rollout controls</h2><div className="runline"><span>PREPARE</span><div><h3>Register immutable artifacts</h3><p>Model and evaluation digests must match before a release can receive traffic.</p></div><b>HOLD</b></div><div className="runline"><span>OBSERVE</span><div><h3>Exercise bad releases</h3><p>Model-based drill evidence has not been produced. Synthetic monitor tests are reported separately.</p></div><b>HOLD</b></div><div className="rollback"><strong>Rollback trigger</strong><p>A safety alarm, or two other registered alarms, trips the switch. Only the Actions writer may change release state.</p></div></section>}
    {!["verdict","criteria","report","try","arms","canary"].includes(section)&&<section><h2>Evidence required</h2><div className="empty"><span>◻</span><div><h3>No promoted result for this stage</h3><p>The implementation and current limits are available in the repository. This page will report measured results only after their evidence is reviewed.</p><a href="https://github.com/mekala27-45/cutover" target="_blank" rel="noreferrer">Inspect the project →</a></div></div></section>}
  </>}
  <section className="pushback"><p className="eyebrow">THE LIMIT OF THIS EVIDENCE</p><p>{pushback}</p></section>
  <footer><p>{statement}</p><a href="https://github.com/mekala27-45/cutover" target="_blank" rel="noreferrer">Source and evidence ↗</a></footer>
  </main></div>
 </div>;
}
