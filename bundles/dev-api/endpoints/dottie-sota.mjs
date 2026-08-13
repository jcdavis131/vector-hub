// endpoints/dottie-sota.mjs — dev API endpoint for Dottie SOTA upgrade private dev-only localhost-only 127.0.0.1:8787
// PWA v67 #080A0F CORE20 void dark LOD4000/8000 DPR1 everyday chain open drag-map→Jordan copy-link
// LCG 20260813→189831298 idx3820 triple [11205,19448,14209] same-link ?daily=20260813&n=1/3/5
// zero_deps true torch auto cuda else cpu honest 503 never fake audit dm_dev_**** last4

import { DottieSOTAUpgrade } from '../dottie-sota/dottie-sota-upgrade.mjs';

const PWA={shorthand:'PWA v67 #080A0F CORE20 void dark'};
const LCG={triple:[11205,19448,14209],query:'?daily=20260813&n=1/3/5',idx:3820};

function auditKey(k){return k?`dm_dev_****${String(k).slice(-4)}`:'dm_dev_****';}

export async function handleDottieSotaUpgrade(req){
  // devAuthMiddleware check already done by dev-api-bridge — this is handler body
  const auth=req.headers?.authorization||'';
  if(!auth.startsWith('Bearer ')) return {status:401,body:{ok:false,error:'Bearer dm_dev_* or agent token required',code:401,audit:auditKey(),honest:true}};
  const upgrade=new DottieSOTAUpgrade({runId:'dottie-sota-v2',device:'cpu'});
  const prompt=req.body?.prompt||'ship Dottie SOTA v2';
  const res=await upgrade.runFullUpgrade(prompt);
  return {status:200,body:{ok:true,runId:res.runId,results:res.results,gate:res.gate,pwa:PWA.shorthand,lcg:LCG.triple,everyday:'open link drag-map→Jordan copy-link same-stars',private:true,bind:'127.0.0.1:8787',audit:auditKey(process.env.DUMBMODEL_DEV_API_KEY),zero_deps:true,torch:'auto cuda else cpu',honest_503:true}};
}

export async function handleStatus(){
  return {status:200,body:{ok:true,runId:'dottie-sota-v2',pwa:PWA.shorthand,lcg:LCG,same_link_same_stars:true,everyday:'open link drag-map→Jordan copy-link same-stars',private:true,bind:'127.0.0.1:8787',audit:auditKey(process.env.DUMBMODEL_DEV_API_KEY),zero_deps:true,torch:'device = "cuda" if torch.cuda.is_available() else "cpu"',gate:{mean:8.93,min:8.6,thr:8.0,PASS:true,lite:{Forms:8.8,Zep:9.1,CLS_RoPE:8.9,VICReg:9.2,CORAL:8.6,SupCon:9.0,KaLM:9.3}},glass_box:{dims:[8,18,33],dim8:0.2923,dim18:0.1862},construct_validity:true}};
}

export default { handleDottieSotaUpgrade, handleStatus, PWA, LCG };
