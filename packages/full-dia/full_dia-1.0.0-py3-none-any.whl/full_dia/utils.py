import argparse
import warnings
from pathlib import Path

from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings(action='ignore', category=ConvergenceWarning)
warnings.filterwarnings(action='ignore', category=UserWarning)

import cupy as cp
import numpy as np
import pandas as pd
import torch
from numba import cuda, jit, prange

from full_dia import param_g
from full_dia.log import Logger
from full_dia import __version__

try:
    # profile
    profile = lambda x: x
except NameError:
    profile = lambda x: x

logger = Logger.get_logger()

@profile
def release_gpu_scans(*map_gpus):
    for map_gpu in map_gpus:
        del map_gpu['scan_rts']
        del map_gpu['scan_seek_idx']
        del map_gpu['scan_im']
        del map_gpu['scan_mz']
        del map_gpu['scan_height']
        map_gpu.clear()
        del map_gpu
    del map_gpus
    # gc.collect()
    torch.cuda.empty_cache()


def convert_numba_to_tensor(x):
    x = cp.asarray(x).toDlpack()
    x = torch.from_dlpack(x)
    return x


def create_cuda_zeros(shape, dtype=torch.float32):
    x = torch.zeros(shape, dtype=dtype, device=param_g.gpu_id)
    x = cuda.as_cuda_array(x)
    return x


def get_diann_info(path_ws):
    if not param_g.is_compare_mode:
        return

    df_diann = pd.read_csv(path_ws / 'diann' / 'report.tsv', sep='\t')
    df_diann = df_diann[df_diann['Q.Value'] < 0.01]
    df_diann['pr_id'] = (df_diann['Modified.Sequence'] +
                         df_diann['Precursor.Charge'].astype(str))

    # rt
    rt_tol_diann = (df_diann['RT'] - df_diann['Predicted.RT']).abs().max() * 60.
    info = 'DIA-NN tol_rt: {:.2f}'.format(rt_tol_diann)
    logger.info(info)

    # im
    im_tol_diann = (df_diann['IM'] - df_diann['Predicted.IM']).abs().max()
    info = 'DIA-NN tol_im: {:.4f}'.format(im_tol_diann)
    logger.info(info)

    # ppm
    import re
    with open(path_ws / 'diann' / 'report.log.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.find('Recommended MS1 mass accuracy setting') > -1:
                pattern = r"\d+\.\d+"
                match = re.search(pattern, line)
                ppm_ms1 = match.group()
                logger.info('DIA-NN MS1 tol_ppm: {}'.format(ppm_ms1))
            if line.find('Optimised mass accuracy') > -1:
                pattern = r"\d+\.\d+"
                match = re.search(pattern, line)
                ppm_ms2 = match.group()
                logger.info('DIA-NN MS2 tol_ppm: {}'.format(ppm_ms2))
            if line.find('window radius') > -1:
                pw = int(line.split(' ')[-1])
                logger.info('DIA-NN peak width: {}'.format(pw))
            if line.find('Training neural networks') > -1:
                x = ' '.join(line.split(' ')[1:])
                logger.info('DIA-NN ' + x.strip())
            if line.find('Number of IDs at 0.01 FDR') > -1:
                t = line.split(' ')[0][1:-1]
                ids = line.split(' ')[-1]
                logger.info(f'DIA-NN time: {t}')
                logger.info(f'DIA-NN 1% FDR prs: {ids}')


def cal_acc_recall(path_ws, df_input,
                   diann_q_pr=None, diann_q_pro=None, diann_q_pg=None,
                   alpha_q_pr=None, alpha_q_pro=None, alpha_q_pg=None):
    if not param_g.is_compare_mode:
        return
    df_alpha = df_input.copy()

    if 'decoy' in df_alpha.columns:
        df_alpha = df_alpha[df_alpha['decoy'] == 0].reset_index(drop=True)

    # for diann pr
    df_diann = pd.read_csv(path_ws / 'diann' / 'report.tsv', sep='\t')
    if diann_q_pr is not None:
        df_diann_pr = df_diann[df_diann['Q.Value'] < diann_q_pr].copy()
    else:
        df_diann_pr = df_diann.copy()
    df_diann_pr['pr_id'] = (df_diann_pr['Modified.Sequence'] +
                            df_diann_pr['Precursor.Charge'].astype(str))
    pr_diann = set(df_diann_pr['pr_id'])

    # for full pr
    if alpha_q_pr is not None:
        df_alpha_pr = df_alpha[df_alpha.q_pr < alpha_q_pr].copy()
    else:
        df_alpha_pr = df_alpha.copy()

    # intersection
    df_cross_pr = df_alpha_pr[['pr_id', 'measure_rt']]
    df_cross_pr = df_cross_pr.merge(df_diann_pr, on='pr_id')
    rt_delta = (df_cross_pr.measure_rt - df_cross_pr.RT * 60.).abs()
    df_cross_pr = df_cross_pr[rt_delta < param_g.locus_rt_thre]
    pr_cross_pr = set(df_cross_pr.pr_id)

    # recall and acc on pr level
    pr_alpha = set(df_alpha_pr['pr_id'])
    pr_recall_2 = len(pr_cross_pr) / (len(pr_diann) + 1)
    pr_recall_1 = len(pr_diann & pr_alpha) / (len(pr_diann) + 1)
    pr_acc = len(pr_diann & pr_alpha) / (len(pr_alpha) + 1)
    pr_gain = (len(pr_alpha) - len(pr_diann)) / (len(pr_diann) + 1)
    info = 'Df: {}, ' \
           'Prs: {}, ' \
           'Pr_gain: {:.2f}, ' \
           'pr_acc: {:.3f}, pr_recall_1: {:.3f}, pr_recall_2: {:.3f}'.format(
        len(df_alpha),
        len(pr_alpha),
        pr_gain,
        pr_acc, pr_recall_1, pr_recall_2,
    )

    # pro and pg
    if diann_q_pro or alpha_q_pro or diann_q_pg or alpha_q_pg:
        # protein
        df_diann_pro = df_diann[(df_diann['Protein.Q.Value'] < diann_q_pro) &
                                (df_diann['Proteotypic'] == 1)]
        df_alpha_pro = df_alpha[(df_alpha['q_pro'] < alpha_q_pro) &
                                (df_alpha['proteotypic'] == 1)].copy()

        pro_diann = set(df_diann_pro['Protein.Ids'])
        pro_alpha = set(df_alpha_pro['protein_id'])
        pro_recall = len(pro_diann & pro_alpha) / (len(pro_diann) + 1)
        pro_acc = len(pro_diann & pro_alpha) / (len(pro_alpha) + 1)
        pro_gain = (len(pro_alpha) - len(pro_diann)) / (len(pro_diann) + 1)

        # protein group
        df_diann_pg = df_diann[(df_diann['PG.Q.Value'] < diann_q_pg)]
        df_alpha_pg = df_alpha[(df_alpha['q_pg'] < alpha_q_pg)]

        pg_diann = set(df_diann_pg['Protein.Group']) # raw
        pg_alpha = set(df_alpha_pg['protein_group'])
        pg_recall = len(pg_diann & pg_alpha) / (len(pg_diann) + 1)
        pg_acc = len(pg_diann & pg_alpha) / (len(pg_alpha) + 1)
        pg_gain = (len(pg_alpha) - len(pg_diann)) / (len(pg_diann) + 1)

        info = 'Prs: {}, ' \
               'Pr_gain: {:.2f}, ' \
               'pr_acc: {:.3f}, pr_recall_1: {:.3f}, pr_recall_2: {:.3f}, ' \
               'Pro_num: {}, ' \
               'Pro_gain: {:.2f}, ' \
               'pro_acc: {:.2f}, pro_recall: {:.2f}, ' \
               'Pg_num: {}, ' \
               'pg_gain: {:.2f}, ' \
               'pg_acc: {:.2f}, pg_recall: {:.2f}'.format(
            len(pr_alpha),
            pr_gain,
            pr_acc, pr_recall_1, pr_recall_2,
            len(pro_alpha),
            pro_gain, pro_acc, pro_recall,
            len(pg_alpha),
            pg_gain, pg_acc, pg_recall
        )
    logger.info(info)


def save_as_pkl(df, fname):
    if param_g.is_compare_mode and (param_g.phase == 'First'):
        df.to_pickle(param_g.dir_out_single / fname)


def save_or_clean(df_main, df_other, ws_single, phase):
    cols_base = ['pr_id', 'pr_charge', 'pr_index',
            'swath_id', 'decoy', 'locus',
            'measure_rt', 'measure_im'
            ]
    cols = cols_base + ['cscore_pr_run', 'q_pr_run',]
    df_main = df_main.loc[:, cols]

    cols = cols_base + ['score_ion_quant_' + str(i) for i in range(14)]
    cols += ['score_ion_sa_' + str(i) for i in range(14)]
    df_other = df_other.loc[:, cols]

    # assert set(df_main['pr_index']).issubset(set(df_other['pr_index']))
    df = pd.merge(df_main, df_other, on=cols_base, how='outer')

    # dtype
    df['locus'] = df['locus'].astype(np.int32)
    cols_big = df.select_dtypes(include=[np.float64]).columns
    df[cols_big] = df[cols_big].astype(np.float32)

    if phase == 'First':
        output_file = param_g.dir_out_global / (ws_single.name + '.parquet')
        df.to_parquet(output_file)
    else:
        return df


def save_lib(df):
    output_file = param_g.dir_out_global / 'report-lib.parquet'
    df.to_parquet(output_file)


def read_from_pq(ws_single, cols=None):
    fname = param_g.dir_out_global / (ws_single.name + '.parquet')
    if cols is None:
        df = pd.read_parquet(fname)
    else:
        df = pd.read_parquet(fname, columns=cols)
    return df


@jit(nopython=True, nogil=True, parallel=True)
def cal_group_rank(x, group_size_cumsum):
    item_num = len(x)
    rank = np.zeros(item_num, dtype=np.uint8)
    for i in prange(len(group_size_cumsum) - 1):
        start = group_size_cumsum[i]
        end = group_size_cumsum[i + 1]
        xx = x[start: end]
        rank[start : end] = np.argsort(np.argsort(-xx)) + 1
    return rank


def push_all_zeros_back(a):
    # Based on http://stackoverflow.com/a/42859463/3293881
    valid_mask = a != 0
    flipped_mask = valid_mask.sum(1, keepdims=1) > np.arange(a.shape[1] - 1, -1,
                                                             -1)
    flipped_mask = flipped_mask[:, ::-1]
    a[flipped_mask] = a[valid_mask]
    a[~flipped_mask] = 0
    return a


def cal_sa_by_np(x, y):
    '''
    x/y has to be two-dimentions
    '''
    norm_x = np.linalg.norm(x, axis=1)
    norm_y = np.linalg.norm(y, axis=1)
    norm_xy = norm_x * norm_y

    xy_sum = (x * y).sum(axis=1)
    sa = xy_sum / (norm_xy + 1e-7)
    sa = 1 - 2 * np.arccos(sa) / np.pi

    return sa


def convert_cols_to_diann(df, ws_single):
    df = df[df['decoy'] == 0].reset_index(drop=True)

    df['file_name'] = '/'.join(ws_single.parts[-2:])
    df['run'] = ws_single.stem

    cols_quant = ['score_ion_quant_' + str(i) for i in range(2+param_g.fg_num)]
    tmp = np.round(df[cols_quant].values, 2).astype(str)
    df['ion_quant'] = [';'.join(row) for row in tmp]

    cols_sa = ['score_ion_sa_' + str(i) for i in range(2+param_g.fg_num)]
    tmp = np.round(df[cols_sa].values, 2).astype(str)
    df['ion_sa'] = [';'.join(row) for row in tmp]

    df = df.rename(columns={
        'file_name': 'File.Name',
        'run': 'Run',
        'protein_group': 'Protein.Group',
        'protein_id': 'Protein.Ids',
        'protein_name': 'Protein.Names',
        'quant_pg_raw': 'PG.Quantity.Raw',
        'quant_pg_deep': 'PG.Quantity.Deep',
        'quant_pg_mix': 'PG.Quantity.Mix',
        'pr_id': 'Precursor.Id',
        'pr_charge': 'Precursor.Charge',
        'q_pr_run': 'Q.Value',
        'q_pr_global': 'Global.Q.Value',
        'q_pg_run': 'PG.Q.Value',
        'q_pg_global': 'Global.PG.Q.Value',
        'proteotypic': 'Proteotypic',
        'quant_pr_raw': 'Precursor.Quantity.Raw',
        'quant_pr_deep': 'Precursor.Quantity.Deep',
        'quant_pr_mix': 'Precursor.Quantity.Mix',
        'measure_rt': 'RT',
        'ion_sa': 'Fragment.Correlations',
        'ion_quant': 'Fragment.Quant.Raw',
        # 'cscore_pr_run': 'CScore',
        'measure_im': 'IM',
    })
    df = df[[
        'File.Name', 'Run',
        # PG
        'Protein.Group', 'Protein.Ids', 'Protein.Names',
        'PG.Q.Value', 'Global.PG.Q.Value',
        'PG.Quantity.Raw', 'PG.Quantity.Deep', 'PG.Quantity.Mix',
        # Pr
        'Precursor.Id', 'Precursor.Charge', 'Proteotypic',
        'Q.Value', 'Global.Q.Value',  # 'CScore',
        'Precursor.Quantity.Raw', 'Precursor.Quantity.Deep', 'Precursor.Quantity.Mix',
        'Fragment.Quant.Raw', 'Fragment.Correlations', 'RT', 'IM'
    ]]
    return df


def get_args():
    name = f"Full-DIA {__version__}"
    print(' ' * 9, "*" * (len(name) + 4))
    print(' ' * 9, f"* {name} *")
    print(' ' * 9, "*" * (len(name) + 4))

    parser = argparse.ArgumentParser('full_dia')

    # required=True
    parser.add_argument(
        '-ws', required=True,
        help='Specify the folder that contains .d files.'
    )
    parser.add_argument(
        '-lib', required=True,
        help='Specify the absolute path of a .speclib spectra library.'
    )

    # optional
    parser.add_argument(
        '-out_name', type=str, default='full_dia',
        help='Specify the folder name of outputs. Default: full_dia.'
    )
    parser.add_argument(
        '-gpu_id', type=int, default=0,
        help='Specify the GPU-ID (e.g. 0, 1, 2) which will be used. Default: 0'
    )
    parser.add_argument(
        '-low_memory', action='store_true',
        help='Specify whether running in low memory mode. Default: False'
    )
    parser.add_argument(
        '-overwrite', action='store_true',
        help='Specify whether overwrite the existing run-specific analysed files. Default: False'
    )
    # develop
    parser.add_argument(
        '-compare', action='store_true',
        help='Developing use. Default: False'
    )

    # process params
    args = parser.parse_args()
    init_gpu_params(args.gpu_id)
    param_g.is_compare_mode = args.compare
    param_g.is_overwrite = args.overwrite
    if args.low_memory:
        param_g.target_batch_max = 250000

    return Path(args.ws), Path(args.lib), args.out_name


def init_gpu_params(gpu_id):
    torch.manual_seed(666)

    param_g.gpu_id = torch.device('cuda:' + str(gpu_id))
    param_g.device_name = torch.cuda.get_device_name(gpu_id)
    torch.backends.cudnn.benchmark = True

    from numba import cuda
    cuda.select_device(gpu_id)

    # xic extraction occupied the GPU memory ratio
    if '4090' in param_g.device_name:
        param_g.batch_xic_seed = 5000
        param_g.batch_xic_locus = param_g.batch_xic_seed * 5
        param_g.batch_deep_center = 10000
        param_g.batch_deep_big = 5000
    else:
        param_g.batch_xic_seed = 4000
        param_g.batch_xic_locus = param_g.batch_xic_seed * 5
        param_g.batch_deep_center = 10000
        param_g.batch_deep_big = 2000


def init_multi_ws(ws_global, out_name):
    # output for global
    param_g.ws_global = ws_global
    param_g.dir_out_name = out_name
    param_g.dir_out_global = (ws_global / out_name)
    param_g.dir_out_global.mkdir(exist_ok=True)
    Logger.set_logger(param_g.dir_out_global, is_time_name=param_g.is_time_log)

    # show version and platform
    import platform
    logger.info(f'Full-DIA (v{__version__}) on {platform.system()} OS')

    # show time
    from datetime import datetime
    logger.info(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # show cpu
    import psutil
    cpu_num = psutil.cpu_count()
    cpu_frq = psutil.cpu_freq().max / 1000
    logger.info(f'CPU: {cpu_num}cores, Frequency: {cpu_frq:.1f}GHz')

    # show memory
    total = psutil.virtual_memory().total / 1024**3
    free = psutil.virtual_memory().available / 1024**3
    logger.info(f'RAM: {free:.0f}G/{total:.0f}G in free/total')

    # show GPU
    i = param_g.gpu_id
    gpu_name = torch.cuda.get_device_name(i)
    free, total = cuda.current_context().get_memory_info()
    free, total = free / 1024**3, total / 1024**3
    logger.info(f'GPU: {gpu_name}-{i}, {free:.0f}G/{total:.0f}G in free/total')
    if free < 10:
        logger.warning('GPU memory is less than 10G. Full-DIA may crash!')

    # show cmd
    import sys
    logger.info(f'CMD: {" ".join(sys.argv)}')

    multi_ws = []
    if ws_global.suffix == '.d':
        multi_ws.append(ws_global)
    else:
        for ws_i in ws_global.rglob('*.d'):
            if ws_i.is_dir():
                multi_ws.append(ws_i)
    param_g.multi_ws = multi_ws
    param_g.file_num = len(param_g.multi_ws)

    info = 'The number of .d files contained in specified ws is less than 2!'
    if param_g.file_num < 2:
        logger.warning(info)


def init_single_ws(ws_i, total, ws_single):
    param_g.ws_single = ws_single
    param_g.dir_out_single = (ws_single / param_g.dir_out_name)
    if param_g.is_compare_mode:
        param_g.dir_out_global.mkdir(exist_ok=True)

    logger.info(f'================Run: {ws_i+1}/{total}================')
    logger.info(f'.d: {str(ws_single.name)}')


def cal_external_q_pr(df):
    dfx = df[(df['q_pr'] < 0.01) & (df['decoy'] == 0)].copy()
    dfx['species'] = 'HUMAN'
    dfx.loc[dfx['protein_name'].str.contains('ARATH'), 'species'] = 'ARATH'
    dfx.loc[dfx['protein_name'].str.contains('HUMAN'), 'species'] = 'HUMAN'
    external_fdr = sum(dfx['species'] == 'ARATH') / sum(dfx['species'] == 'HUMAN')
    print(f'{len(dfx)}, external_fdr: {external_fdr:.4f}')


def cross_cos(x):
    norms = np.linalg.norm(x, axis=1) + 1e-6
    normalized_x = x / norms[:, np.newaxis]
    cosine_sim = np.dot(normalized_x, normalized_x.T)
    return cosine_sim


def cal_kde(labels, choice_size=10000):
    from sklearn.model_selection import GridSearchCV
    from sklearn.neighbors import KernelDensity

    # sample labels
    choice_size = min(choice_size, len(labels))
    labels_sample = np.random.choice(labels, size=choice_size, replace=False)

    # init bandwidth by Silverman
    b = 1.06 * np.std(labels_sample) * choice_size**(-1/5)
    bandwidths = np.linspace(0.1 * b, 1.5 * b, 20)

    # grid search for bandwidth
    grid = GridSearchCV(KernelDensity(kernel='gaussian'),
                        param_grid={'bandwidth': bandwidths},
                        cv=5,
                        n_jobs=1 if __debug__ else 8)
    grid.fit(labels_sample[:, None])
    best_bandwidth = grid.best_params_['bandwidth']

    # fit by sample
    best_kde = KernelDensity(kernel='gaussian', bandwidth=best_bandwidth)
    best_kde.fit(labels_sample[:, None])

    # pred for grid
    x_grid = np.linspace(labels.min(), labels.max(), 1000)
    log_density_grid = best_kde.score_samples(x_grid[:, None])
    density_grid = np.exp(log_density_grid)

    # interp
    from scipy.interpolate import interp1d
    interp_func = interp1d(x_grid, density_grid, fill_value="extrapolate")

    # pred for all
    density = interp_func(labels)

    # cal weights
    weights = 1 / (density + 1e-6)
    # weights = np.log2(1 + np.sqrt(weights))
    # weights = (weights - weights.min()) / (weights.max() - weights.min())
    weights = np.clip(weights, None, 200* weights.min())
    return weights


def cal_pccs(X):
    from scipy.stats import pearsonr
    x = np.arange(X.shape[1])
    pccs = np.array([pearsonr(x, row)[0] for row in X])

    # x = X[np.where(pccs == np.median(pccs))[0][0]]
    # pccs = np.array([pearsonr(x, row)[0] for row in X])
    return pccs

@jit(nopython=True, nogil=True, parallel=True)
def interp_xics(xics, rts, target_dim):
    '''
    xics: [n_pep, n_ion, n_cycle]
    rts: [n_pep, n_cycle]
    result_xics: [n_pep, n_ion, target_dim]
    result_rts: [n_pep, target_dim]
    '''
    n_pep, n_ion, n_cycle = xics.shape
    result_xics = np.zeros((n_pep, n_ion, target_dim))
    result_rts = np.zeros((n_pep, target_dim))
    for i_pep in prange(n_pep):
        rts_pep = rts[i_pep]
        rts_interp = np.linspace(rts_pep[0], rts_pep[-1], target_dim)
        result_rts[i_pep] = rts_interp
        for i_ion in range(n_ion):
            xic_raw = xics[i_pep, i_ion]
            xic_interp = np.interp(rts_interp, rts_pep, xic_raw)
            result_xics[i_pep, i_ion] = xic_interp
    return result_rts, result_xics


def print_ids(df, q_cut, pr_or_pg, run_or_global):
    if pr_or_pg == 'pr':
        ids = []
        for q_pr in [0.01, q_cut]:
            df_sub = df[(df['q_pr_' + run_or_global] <= q_pr)]
            df_sub = df_sub[(df_sub['decoy'] == 0)]
            ids.append(df_sub.pr_id.nunique())
            if param_g.is_compare_mode and (run_or_global == 'run'):
                cal_acc_recall(param_g.ws_single, df_sub, diann_q_pr=0.01)
        id100 = (df['decoy'] == 0).sum()
        info = 'Ids-Precursor at {} FDR:     {}-0.01, {}-{:.2f}, {}-all'.format(
            run_or_global, ids[0], ids[1], q_cut, id100
        )
        logger.info(info)

    if pr_or_pg == 'pg':
        ids = []
        for q_pg in [0.01, q_cut]:
            df_sub = df[(df['q_pg_' + run_or_global] <= q_pg)]
            df_sub = df_sub[(df_sub['decoy'] == 0)]
            ids.append(df_sub['protein_group'].nunique())
        id100 = df[df['decoy'] == 0]['protein_group'].nunique()
        info = 'Ids-Protein Group at {} FDR: {}-0.01, {}-{:.2f}, {}-all'.format(
            run_or_global, ids[0], ids[1], q_cut, id100
        )
        logger.info(info)


def print_external_global_fdr(df):
    for fdr in [0.01, 0.05]:
        total = (df['q_pr_global'] < fdr) & (df['decoy'] == 0)
        bad = ((df['q_pr_global'] < fdr) & (df['decoy'] == 0) &
               (df['protein_name'].str.contains('ARATH')) &
               (~df['protein_name'].str.contains('HUMAN'))
              )
        external_fdr = sum(bad) / sum(total)
        print(f'Global Pr level: {fdr:.3f}-{external_fdr:.3f}')
    for fdr in [0.01, 0.05]:
        total = (df['q_pg_global'] < fdr) & (df['decoy'] == 0)
        bad = ((df['q_pg_global'] < fdr) & (df['decoy'] == 0) &
               (df['protein_name'].str.contains('ARATH')) &
               (~df['protein_name'].str.contains('HUMAN'))
               )
        total = df[total]['protein_group'].nunique()
        bad = df[bad]['protein_group'].nunique()
        external_fdr = bad / total
        print(f'Global Pg level: {fdr:.3f}-{external_fdr:.3f}')


def print_external_run_fdr(df):
    for fdr in [0.01, 0.05]:
        total = (df['q_pr_run'] < fdr) & (df['decoy'] == 0)
        bad = ((df['q_pr_run'] < fdr) & (df['decoy'] == 0) &
               (df['protein_name'].str.contains('ARATH')) &
               (~df['protein_name'].str.contains('HUMAN'))
              )
        external_fdr = sum(bad) / sum(total)
        print(f'Run Pr level: {fdr:.3f}-{external_fdr:.3f}')
    for fdr in [0.01, 0.05]:
        total = (df['q_pg_run'] < fdr) & (df['decoy'] == 0)
        bad = ((df['q_pg_run'] < fdr) & (df['decoy'] == 0) &
               (df['protein_name'].str.contains('ARATH')) &
               (~df['protein_name'].str.contains('HUMAN'))
               )
        total = df[total]['protein_group'].nunique()
        bad = df[bad]['protein_group'].nunique()
        external_fdr = bad / total
        print(f'Run Pg level: {fdr:.3f}-{external_fdr:.3f}')