// Run with Node.js and Newman installed: node scripts/run_collection.cjs
// Secrets stay in runtime/. Published evidence is deliberately sanitized.
const fs = require('fs');
const path = require('path');
const newman = require('newman');
const root = path.resolve(__dirname, '..');
const collectionPath = path.join(root, 'postman/Sprint1.postman_collection.json');
const collection = JSON.parse(fs.readFileSync(collectionPath, 'utf8'));
const environment = JSON.parse(fs.readFileSync(path.join(root, 'runtime/postman.private.json'), 'utf8'));
const redact = value => {
  if (Array.isArray(value)) return value.map(redact);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k,v]) => [k, ['token','password','password_hash','token_hash'].includes(k) ? '[REDACTED]' : redact(v)]));
  return value;
};
newman.run({collection, environment, reporters:['cli'], color:'off', delayRequest:100, timeoutRequest:15000}, (error, summary) => {
  if (error) { console.error(error.message); process.exitCode=1; return; }
  const captures = summary.run.executions.map(e => {
    const body=e.response ? redact(JSON.parse(e.response.stream.toString('utf8'))) : null;
    const req=e.request.toJSON();
    req.header=(req.header||[]).filter(h=>h.key.toLowerCase()!=='authorization');
    req.auth={type:'noauth'};
    if(req.body?.raw) { try { req.body.raw=JSON.stringify(redact(JSON.parse(req.body.raw)),null,2); } catch {} }
    const item=collection.item.find(i=>i.name===e.item.name);
    if(e.response)item.response=[{name:`Actual Newman ${e.response.code} — ${item.name}`,originalRequest:req,status:e.response.status,code:e.response.code,header:[{key:'Content-Type',value:'application/json'}],body:JSON.stringify(body,null,2),_postman_previewlanguage:'json'}];
    return {name:e.item.name,method:e.request.method,url:e.request.url.toString(),status:e.response?.code,body,assertions:(e.assertions||[]).map(a=>({name:a.assertion,passed:!a.error}))};
  });
  const result={captured_at:new Date().toISOString(),runner:'Newman '+require('newman/package.json').version,stats:summary.run.stats,failures:summary.run.failures.map(f=>({name:f.error.name,message:f.error.message,source:f.source?.name})),captures};
  fs.writeFileSync(path.join(root,'evidence/newman-results.json'),JSON.stringify(result,null,2));
  fs.writeFileSync(collectionPath,JSON.stringify(collection,null,2));
  fs.writeFileSync(path.join(root,'runtime/postman.after-run.private.json'),JSON.stringify(summary.environment.toJSON(),null,2));
  console.log(`Saved ${captures.length} real responses; ${summary.run.stats.assertions.total} assertions; ${result.failures.length} failures.`);
  if(result.failures.length)process.exitCode=1;
});
