"""Run the preregistered finite follow-ups after the core native batch completes."""
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'output/v2-readiness-r31'
deadline=time.monotonic()+14400
while not (OUT/'core/results.json').is_file():
    if time.monotonic()>deadline:
        raise SystemExit('Core batch did not finish; follow-ups were not started')
    time.sleep(5)
runner=ROOT/'maintenance/tests/evidence/v2-independent-readiness-r31/run_native.py'
jobs=[
    ('parent', ['0','3'], ['markdown_application_review'], 'parent', 'frozen/candidate', []),
    ('qwen2', ['1'], ['news_commentary'], 'baseline', 'frozen/candidate', []),
    ('deepseek', ['2'], ['remediation_report'], 'baseline', 'frozen/candidate', []),
    ('glmflash', ['4'], ['server_technical_requirements'], 'baseline', 'frozen/candidate', []),
    ('word', ['3'], ['ordinary_word_summary'], 'baseline', 'preview/chinese-official-writing-v2', ['--candidate-skill-name','chinese-official-writing-v2']),
]
for name,models,cases,baseline,candidate,extra in jobs:
    command=[sys.executable,str(runner),'--output',str(OUT/name),'--baseline-dir',str(OUT/'frozen'/baseline),
             '--candidate-dir',str(OUT/candidate),'--models',*models,'--cases',*cases,'--timeout','600','--effort','max',
             '--isolated-profile','--ordinary-only','--utf8-read',*extra]
    print('FOLLOWUP',name,flush=True)
    result=subprocess.run(command,cwd=ROOT)
    print('FOLLOWUP_EXIT',name,result.returncode,flush=True)
