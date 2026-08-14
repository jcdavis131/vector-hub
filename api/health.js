export default function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  res.status(503).json({ok:false,error:"unified health 503 honest fallback — use /api/v1/free for free platform",version:"v67-free-knowledge-edge-money",dailySeed:"20260813→189831298 idx3820"});
}
