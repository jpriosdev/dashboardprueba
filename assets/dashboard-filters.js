(function(){
    // Enhances dashboard: populate selects with counts, keep options updated, and update charts on filter change
    function safe(fn){ try{ fn(); }catch(e){ console.warn('dashboard-filters error', e); }}

    function getRows(){ return Array.isArray(window.DASH_DATA && window.DASH_DATA.rows) ? window.DASH_DATA.rows : []; }

    function computeCounts(rows){
        const sprint = {}; const type = {}; const priority = {}; const status = {};
        rows.forEach(r=>{
            if (r.sprint) sprint[r.sprint] = (sprint[r.sprint]||0)+1;
            if (r.type) type[r.type] = (type[r.type]||0)+1;
            if (r.priority) priority[r.priority] = (priority[r.priority]||0)+1;
            if (r.status) status[r.status] = (status[r.status]||0)+1;
        });
        return {sprint,type,priority,status};
    }

    function addOptions(select, itemsMap, preserveFirst){
        if (!select) return;
        // keep only first option (defaults)
        const first = select.options && select.options.length? select.options[0].value : null;
        // remove old added options except first
        while(select.options.length>1) select.remove(1);
        Object.keys(itemsMap).sort().forEach(k=>{
            const cnt = itemsMap[k]||0;
            if (cnt<=0) return;
            const opt = document.createElement('option');
            opt.value = k;
            opt.text = `${k} (${cnt})`;
            select.add(opt);
        });
    }

    function parseFilters(){
        const sprint = (document.getElementById('filterSprint')||{}).value || '';
        const type = (document.getElementById('filterType')||{}).value || '';
        const priority = (document.getElementById('filterPriority')||{}).value || '';
        const status = (document.getElementById('filterStatus')||{}).value || '';
        return [sprint,type,priority,status];
    }

    function filterRows(rows, vals){
        const [sprintFilter, typeFilter, priorityFilter, statusFilter] = vals;
        return rows.filter(r=>{
            if (sprintFilter && /todos?/i.test(sprintFilter)===false && sprintFilter!==''){
                if (!r.sprint || r.sprint.indexOf(sprintFilter)===-1) return false;
            }
            if (typeFilter && /todos?/i.test(typeFilter)===false && typeFilter!==''){
                const t = typeFilter.toLowerCase();
                if (t==='bugs' && (r.type||'').toLowerCase()!=='bug') return false;
                if (t==='stories' && (r.type||'').toLowerCase()!=='story') return false;
                if (t==='tests' && (r.type||'').toLowerCase()!=='test') return false;
            }
            if (priorityFilter && /tod/i.test(priorityFilter)===false && priorityFilter!==''){
                if (!r.priority || (r.priority||'').toLowerCase().indexOf(priorityFilter.toLowerCase())===-1) return false;
            }
            if (statusFilter && /tod/i.test(statusFilter)===false && statusFilter!==''){
                if (!r.status || (r.status||'').toLowerCase().indexOf(statusFilter.toLowerCase())===-1) return false;
            }
            return true;
        });
    }

    function updateCharts(filtered){
        try{
            // bugTrendChartObj
            if (window.bugTrendChartObj){
                const trend = {};
                filtered.forEach(r=>{ if ((r.type||'').toLowerCase()==='bug'){ const k = r.sprint||'Unspecified'; trend[k] = (trend[k]||0)+1; }});
                const labels = Object.keys(trend).length? Object.keys(trend).sort() : Object.keys(window.DASH_DATA.bugs_trend||{});
                const data = labels.map(l=> trend[l] || (window.DASH_DATA.bugs_trend||{})[l] || 0);
                window.bugTrendChartObj.data.labels = labels;
                if (window.bugTrendChartObj.data.datasets[0]) window.bugTrendChartObj.data.datasets[0].data = data;
                if (window.bugTrendChartObj.data.datasets[1]) window.bugTrendChartObj.data.datasets[1].data = data.map(x=>Math.max(0,Math.round(x*0.8)));
                if (window.bugTrendChartObj.data.datasets[2]) window.bugTrendChartObj.data.datasets[2].data = data.map(x=>Math.max(0,Math.round(x*2)));
                window.bugTrendChartObj.update();
            }
            // coverageChart
            if (window.coverageChartObj){
                const typeMap = {};
                filtered.forEach(r=>{ const k = r.type||'Unknown'; typeMap[k] = (typeMap[k]||0)+1; });
                const labels = Object.keys(typeMap).length? Object.keys(typeMap) : ['Stories','Tasks','Bugs','Epics'];
                const total = labels.map(l=> typeMap[l]||0);
                const testsCount = (typeMap['Test']||0) + (typeMap['Test Execution']||0);
                const storiesCount = (typeMap['Story']||0) || 1;
                const withTests = Math.min(testsCount, storiesCount);
                const withTestsArr = labels.map(l=> l==='Stories'? withTests:0);
                window.coverageChartObj.data.labels = labels;
                if (window.coverageChartObj.data.datasets[0]) window.coverageChartObj.data.datasets[0].data = total;
                if (window.coverageChartObj.data.datasets[1]) window.coverageChartObj.data.datasets[1].data = withTestsArr;
                window.coverageChartObj.update();
            }
            // velocity
            if (window.velocityChartObj){
                const weeks = Object.keys(window.DASH_DATA.bugs_trend||{}).slice(-8);
                const vdata = weeks.map(w=> filtered.filter(r=> (r.type||'').toLowerCase()==='bug' && ((r.sprint||'').indexOf(w)!==-1)).length || (window.DASH_DATA.bugs_trend||{})[w] || 0);
                window.velocityChartObj.data.labels = weeks;
                if (window.velocityChartObj.data.datasets[0]) window.velocityChartObj.data.datasets[0].data = vdata;
                if (window.velocityChartObj.data.datasets[1]) window.velocityChartObj.data.datasets[1].data = vdata.map(x=>Math.max(0,x+2));
                window.velocityChartObj.update();
            }
            // forecast
            if (window.forecastChartObj){
                const weeks = Object.keys(window.DASH_DATA.bugs_trend||{}).slice(-12);
                const hist = weeks.map(w=> filtered.filter(r=> (r.type||'').toLowerCase()==='bug' && ((r.sprint||'').indexOf(w)!==-1)).length || (window.DASH_DATA.bugs_trend||{})[w] || 0);
                if (window.forecastChartObj.data.datasets[0]) window.forecastChartObj.data.datasets[0].data = hist.slice(0,8);
                if (window.forecastChartObj.data.datasets[1]){
                    const proj = new Array(weeks.length).fill(null);
                    for (let i=8;i<weeks.length;i++) proj[i] = Math.round(((hist[i-1]||0)*1.05)+2);
                    window.forecastChartObj.data.datasets[1].data = proj;
                }
                window.forecastChartObj.update();
            }
        }catch(e){console.warn('updateCharts',e);}    
    }

    function updateExecutiveKPIs(filtered){
        try{
            if (!Array.isArray(filtered)) filtered = [];
            const total = filtered.length || 0;
            const bugs = filtered.filter(r=> (r.type||'').toLowerCase()==='bug').length;
            const stories = filtered.filter(r=> (r.type||'').toLowerCase()==='story').length;
            const tests = filtered.filter(r=> {
                const t=(r.type||'').toLowerCase(); return t==='test' || t==='test execution' || t==='testexecution';
            }).length;

            // defect rate % (bugs / total)
            const defectRate = total>0? Math.round((bugs/total)*1000)/10 : 0;
            // test execution % relative to stories
            const testExecPct = stories>0? Math.round((tests/stories)*1000)/10 : (window.DASH_DATA && window.DASH_DATA.test_coverage? Math.round(window.DASH_DATA.test_coverage*10)/10 : 0);

            // Update KPI cards in resumen tab
            const resumen = document.getElementById('resumen');
            if (!resumen) return;
            const cards = resumen.querySelectorAll('.kpi-card');
            cards.forEach(card=>{
                const labelEl = card.querySelector('.kpi-label');
                const valueEl = card.querySelector('.kpi-value');
                if (!labelEl || !valueEl) return;
                const label = (labelEl.textContent||'').toLowerCase();
                if (label.indexOf('defect')!==-1 || label.indexOf('defect rate')!==-1){
                    valueEl.textContent = `${defectRate}%`;
                } else if (label.indexOf('test exec')!==-1 || label.indexOf('test execution')!==-1 || label.indexOf('test exec %')!==-1){
                    valueEl.textContent = `${testExecPct}%`;
                } else if (label.indexOf('mttr')!==-1){
                    // Only update MTTR if the generator provided a value; otherwise keep existing DOM value
                    if (window.DASH_DATA && typeof window.DASH_DATA.mttr_days !== 'undefined'){
                        valueEl.textContent = `${window.DASH_DATA.mttr_days}d`;
                    }
                } else if (label.indexOf('lead time')!==-1){
                    if (window.DASH_DATA && typeof window.DASH_DATA.lead_time_days !== 'undefined'){
                        valueEl.textContent = `${window.DASH_DATA.lead_time_days}d`;
                    }
                } else if (label.indexOf('total bugs')!==-1 || label.indexOf('total bugs'.toLowerCase())!==-1){
                    valueEl.textContent = bugs;
                }
            });
        }catch(e){console.warn('updateExecutiveKPIs',e);}    
    }

    function updateOptionCounts(filtered){
        const counts = computeCounts(filtered);
        const sprintSelect = document.getElementById('filterSprint');
        const typeSelect = document.getElementById('filterType');
        const prioritySelect = document.getElementById('filterPriority');
        const statusSelect = document.getElementById('filterStatus');
        // update texts and disable
        [[sprintSelect, counts.sprint],[typeSelect, counts.type],[prioritySelect, counts.priority],[statusSelect, counts.status]].forEach(([sel,map])=>{
            if (!sel) return;
            for (let i=0;i<sel.options.length;i++){
                const opt = sel.options[i];
                const val = opt.value;
                if (!val) continue;
                if (/todos?/i.test(opt.text)) continue;
                const base = val;
                const cnt = map[base]||0;
                opt.text = `${base} (${cnt})`;
                opt.disabled = cnt===0;
            }
        });
    }

    function init(){
        if (!window.DASH_DATA) return;
        safe(()=>{
            const rows = getRows();
            const counts = computeCounts(rows);
            addOptions(document.getElementById('filterSprint'), counts.sprint);
            addOptions(document.getElementById('filterType'), counts.type);
            addOptions(document.getElementById('filterPriority'), counts.priority);
            addOptions(document.getElementById('filterStatus'), counts.status);

            // attach listeners: when selects change, call existing updateFilters() then our updates
            ['filterSprint','filterType','filterPriority','filterStatus'].forEach(id=>{
                const el = document.getElementById(id);
                if (!el) return;
                el.addEventListener('change', ()=>{
                    try{ if (typeof updateFilters === 'function') updateFilters(); }catch(e){}
                    const vals = parseFilters();
                    const f = filterRows(rows, vals);
                    updateOptionCounts(f);
                    updateCharts(f);
                    updateExecutiveKPIs(f);
                });
            });

            // initial sync
            const vals = parseFilters();
            const f = filterRows(rows, vals);
            updateOptionCounts(f);
            updateCharts(f);
            updateExecutiveKPIs(f);
        });
    }

    if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
