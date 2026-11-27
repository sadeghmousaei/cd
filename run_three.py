"""
Runs the notebook THREE times: the incomplete breakthrough curves of Step 1 are completed by XGBR, by GBR, and by RFR.
Every run is a complete workflow (Step 1 -> T, K, b, a with the three models at every stage -> Step 4 chains) in its own folder,
so the chain of each model family really starts from the first stage.

Put this file, Fixed_Bed_Adsorption_All_Steps_FULL.ipynb and semifinalcd_filled.xlsx in the same folder and run:
    python run_three.py                 # the three runs one after the other (the full grid search: it takes many hours)
    python run_three.py --only GBR      # only one of them
    python run_three.py --grid medium   # smaller grids (quick look)
A run that already finished is skipped. A run that was stopped can simply be started again: the models whose grid search is finished
are read from best_hyperparameters_full.json of that run folder and are not searched again.
Needs:  pip install nbclient nbformat ipykernel
"""
import argparse, os, shutil, sys, time
import nbformat
from nbclient import NotebookClient

NB = 'Fixed_Bed_Adsorption_All_Steps_FULL.ipynb'
DATA = ['semifinalcd_filled.xlsx']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', choices=['XGBR', 'GBR', 'RF'])
    ap.add_argument('--grid', default='wide', choices=['wide', 'medium', 'small'])
    ap.add_argument('--force', action='store_true', help='run again even if the run is finished')
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    for m in ([args.only] if args.only else ['XGBR', 'GBR', 'RF']):
        d = os.path.join(here, f'run_step1_{m}')
        done = os.path.join(d, 'executed.ipynb')
        if os.path.exists(done) and not args.force:
            print(f'[{m}] already finished -> skipped ({done})'); continue
        os.makedirs(d, exist_ok=True)
        shutil.copy(os.path.join(here, NB), os.path.join(d, NB))
        for f in DATA:
            shutil.copy(os.path.join(here, f), os.path.join(d, f))
        os.environ['STEP1_MODEL'] = m
        os.environ['GRID_LEVEL'] = args.grid
        print(f'[{m}] start {time.strftime("%Y-%m-%d %H:%M")}  (folder: {d})', flush=True)
        nb = nbformat.read(os.path.join(d, NB), as_version=4)
        client = NotebookClient(nb, timeout=None, kernel_name='python3', resources={'metadata': {'path': d}}, allow_errors=False)
        try:
            client.execute()
            ok = True
        except Exception as e:
            ok = False
            print(f'[{m}] STOPPED by an error: {type(e).__name__}: {str(e)[:500]}')
        out = done if ok else os.path.join(d, 'partial_failed.ipynb')
        nbformat.write(nb, out)
        print(f'[{m}] {"finished" if ok else "failed"} {time.strftime("%Y-%m-%d %H:%M")} -> {out}', flush=True)


if __name__ == '__main__':
    main()
