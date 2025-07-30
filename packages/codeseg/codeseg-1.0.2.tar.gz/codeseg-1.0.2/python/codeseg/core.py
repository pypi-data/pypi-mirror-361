import os
import sys
import subprocess
import logging
from .utils import get_ntwk_change  

logger = logging.getLogger(__name__)

def find_executable():
    here = os.path.dirname(os.path.abspath(__file__))
    exe_name = "CoDeSEG.exe" if os.name == "nt" else "CoDeSEG"
    exe_path = os.path.join(here, "bin", exe_name)
    if not os.path.exists(exe_path):
        raise RuntimeError(f"CoDeSEG executable not found at {exe_path}. Please check installation.")
    return exe_path

def CoDeSEG(in_path, out_path, ground_truth="", name="", overlap=False, 
                weighted=False, directed=False, dynamic=False, it=10, 
                tau=0.3, gamma=1, r=2, parallel=1, verbose=False):
   
    executable = find_executable()
    
    if not dynamic:
        final_out_path = os.path.join(out_path, "CoDeSEG.txt")
        os.makedirs(os.path.dirname(final_out_path), exist_ok=True)
    else:
        final_out_path = os.path.join(out_path, "CoDeSEG")
        os.makedirs(final_out_path, exist_ok=True)
        snapshot_dir = os.path.join(os.path.dirname(in_path), "changed")
        if not os.path.exists(snapshot_dir):
            logger.info("Obtain and store network changes...")
            print(f"Obtain and store network changes...\nWarning: This operation is required only during the first execution. \nDo not interrupt the program; otherwise, please delete the '{snapshot_dir}' folder and rerun the program.")
            
            get_ntwk_change(os.path.dirname(in_path))

        in_path = snapshot_dir

    args = [
        executable,
        "-i", in_path,
        "-o", final_out_path,
        "-n", str(it),
        "-t", ground_truth,
        "-e", str(tau),
        "-r", str(r),
        "-g", str(gamma),
        "-p", str(parallel),
    ]
    
    if overlap:
        args.append("-x")
    if weighted:
        args.append("-w")
    if directed:
        args.append("-d")
    if verbose:
        args.append("-v")
    if dynamic:
        args.append("-c")

    logger.debug(f"Executing command: {' '.join(args)}")
    
    try:
        result = subprocess.run(
            args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if verbose:
            logger.info(result.stdout)
            print(result.stdout)
        if not dynamic:
            division = []
            with open(final_out_path) as f:
                for line in f:
                    nodes = line.strip().split()
                    nodes = [int(n) for n in nodes]
                    division.append(nodes)
            return division
        else:
            j = 1
            ntwk_comms = {}
            while os.path.exists(os.path.join(final_out_path, str(j) + ".txt")):
                result_path = os.path.join(final_out_path, str(j) + ".txt")

                division = []
                with open(result_path, "r") as f:
                    for line in f:
                        nodes = line.strip().split()
                        nodes = [int(n) for n in nodes]
                        division.append(nodes)
                ntwk_comms[f"G_{j}"] = division
                j += 1
            return ntwk_comms
    except subprocess.CalledProcessError as e:
        logger.error(f"CoDeSEG execution failed with error {e.returncode}")
        logger.error(f"Output: {e.stdout}")
        logger.error(f"Error: {e.stderr}")
        raise RuntimeError(f"CoDeSEG execution failed: {e.stderr}") from e