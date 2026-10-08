const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const start=html.indexOf('const VRAGEN = [');
const end=html.indexOf('];',html.indexOf('/* ===== RONDE 5'))+2;
const VRAGEN=eval(html.slice(start+'const VRAGEN = '.length,end-1));
fs.writeFileSync(process.argv[3],JSON.stringify(VRAGEN,null,1));
console.log(VRAGEN.length);
