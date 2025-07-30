is_compare_mode = False
is_time_log = False
phase = 'First' # or 'Second'

# placeholder
dir_out_global = None
dir_out_single = None
dir_out_name = None
multi_ws = None
file_num = None
tol_rt = None # second
locus_rt_thre = None # second
gpu_id = None
is_overwrite = False

# tol_rt is related to the length of gradient
tol_rt_ratio = 1/15
sample_ratio = 0.1 # sample for calculate tolerances
# locuses from Full-DIA and DIA-NN within this value are considered consistent
locus_valid_num = 3.5
# seek locus
top_sa_cut, top_deep_cut = 0.75, 0.66
# batch size max for targets; when low memory mode, it's 250000
target_batch_max = 450000
# batch q cut
rubbish_q_cut = 0.5

# widely used
fg_num = 12
tol_ppm = 20  # boin in centroid or profile data
tol_im_xic_before_calib = 0.08 # 1/k0. For centroid data.
tol_im_xic_after_calib = 0.05
tol_im_xic = tol_im_xic_before_calib

# deepmap
tol_im_map = 0.025 # half width of im for DeepMap

# The mobility span ≈ 0.01-0.02, gap-0.0001 guarantees 10 sampling points.
# Maximum in a bin. Also, a push is 0.001(1/1000)
map_im_gap = 0.001 # bin width in im dimension for DeepMap
map_im_dim = int(2 * tol_im_map / map_im_gap)
map_cycle_dim = 13 # locus with 13 cycles
window_points = 7 # SA only using 7 cycles.

# deepmap retrain or deepmall train
patient = 5

# global
top_k_fg = 5 # select top_k_fg ions for cross quantification of precursors
top_k_pr = 1 # select top_k_pr prs for protein quantification
q_cut_infer = None # which prs will be used for protein group infer and score

g_aa_to_mass = {'A': 89.0476792233, 'C': 160.030644505, 'D': 133.0375092233,
                'E': 147.05315928710002,
                'F': 165.07897935090006, 'G': 75.0320291595,
                'H': 155.06947728710003, 'I': 131.0946294147,
                'K': 146.10552844660003, 'L': 131.0946294147,
                'M': 149.05105008089998, 'm': 165.04596508089998,
                'N': 132.0534932552, 'P': 115.06332928709999,
                'Q': 146.06914331900003, 'R': 174.11167644660003,
                'S': 105.0425942233, 'T': 119.05824428710001,
                'V': 117.0789793509, 'W': 204.0898783828,
                'Y': 181.07389435090005, "c": 178.04121404900002}
