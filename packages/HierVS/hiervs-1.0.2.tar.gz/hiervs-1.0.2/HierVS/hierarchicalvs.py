import os
import subprocess
import pandas as pd
import sys
import argparse
import csv


def convert_to_absolute(path):
    if not os.path.isabs(path):
        return os.path.abspath(path)
    return path

def change_path_local2docker(old_path):
    absolute_path = convert_to_absolute(old_path)
    docker_path = docker_path = '/home'+absolute_path
    return docker_path

def read_smiles_from_file(text_file):
    molecules_dict = {}
    
    with open(text_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            molecule_info = line.split()
            molecule_name = molecule_info[1]
            molecule_smiles = molecule_info[0]
            molecules_dict[molecule_name] = molecule_smiles 
    return molecules_dict

def convert_txt_to_csv(input_file, output_file):
    with open(input_file, 'r') as txt_file:
        lines = txt_file.readlines()
        header = lines[0].strip()
        data_lines = lines[1:]

    with open(output_file, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(header.split('\t'))
        for line in data_lines:
            csv_writer.writerow(line.strip().split('\t'))

def get_pre_file_path(absolute_path):
    directory, filename = os.path.split(absolute_path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}_pre{extension}"
    new_path = os.path.join(directory, new_filename)
    return new_path

def process_karmadock_prediction_files(text_file, csv_file,karmadock_score_top_smile_txt , topN=50):
    
    df = pd.read_csv(csv_file)
    sorted_df = df.sort_values(by='karma_score', ascending=False).iloc[:topN,:]
    smile_ids = list(sorted_df['pdb_id'])
    name2smile = read_smiles_from_file(text_file)
    top_smiles = []
    for i in smile_ids:
        top_smiles.append(name2smile[i])
    
    with open(karmadock_score_top_smile_txt, 'w') as outfile:
        for smiles in top_smiles:
            outfile.write(smiles + '\n')
            
    sorted_df = df.sort_values(by='karma_score', ascending=False)
    sorted_df.insert(loc=1, column='smiles', value=[name2smile[i] for i in sorted_df['pdb_id']])
    sorted_df.rename(columns={'pdb_id': 'molecule_id'}, inplace=True)
    return sorted_df
    # sorted_df.to_csv(os.path.join(os.path.dirname(text_file) , 'karmadock_prediction_dealt.csv') , index=False) 

def karmadock_prediction(protein_file , crystal_ligand_file , ligand_smi, out_dir,cuda_number , image_version):
        # print('--shm-size="8g"')
        cmd = f'docker run -it --rm --gpus device={cuda_number} -v /:/home  --shm-size="8g" {image_version} /bin/bash -c \
                "source /root/miniconda3/bin/activate && conda activate karmadock && cd /mnt/Models/KarmaDock/utils   && \
                 python -u virtual_screening.py \
                --ligand_smi {ligand_smi} \
                --protein_file {protein_file} \
                --crystal_ligand_file {crystal_ligand_file} \
                --out_dir {out_dir} \
                --score_threshold 0 \
                --batch_size 64 \
                --random_seed 2023 "' 
        subprocess.call(cmd, shell=True)

def carsidock_prediction(protein_file , crystal_ligand_file , ligand_sdf, out_dir , cuda_number , image_version):
        cmd = f'docker run -it --rm --gpus device={cuda_number} -v /:/home --shm-size="8g" {image_version} /bin/bash -c \
                "source /root/miniconda3/bin/activate && conda activate carsidock && cd /mnt/Models/CarsiDock &&  python -u run_screening.py \
                --cuda_convert \
                --pdb_file {protein_file} \
                --reflig {crystal_ligand_file} \
                --ligands {ligand_sdf} \
                --output_dir {out_dir}"' 
        subprocess.call(cmd, shell=True)
    
def vs_file_pre(smile_file , number_worker , time_out , image_version):
        # print('--shm-size="8g"')
        cmd = f'docker run -it --rm --gpus all -v /:/home  --shm-size="8g" {image_version} /bin/bash -c \
                "source /root/miniconda3/bin/activate && conda activate karmadock && cd /mnt/Models/vs_filter && python -u vs_filter.py \
                --smile_file {smile_file} \
                --number_worker {number_worker} \
                --time_out {time_out}  "' 
        subprocess.call(cmd, shell=True)

def post_precess(carsidock_csv_file , karmadock_score_top_smile_txt, ligand_smi , image_version):
        # print('--shm-size="8g"')
        cmd = f'docker run -it --rm --gpus all -v /:/home  --shm-size="8g" {image_version} /bin/bash -c \
                "source /root/miniconda3/bin/activate && conda activate carsidock && cd /mnt/Models/post_process && python -u post_process.py \
                --carsidock_csv_file {carsidock_csv_file} \
                --karmadock_score_top_smile_txt {karmadock_score_top_smile_txt} \
                --ligand_smi {ligand_smi}  "' 
        subprocess.call(cmd, shell=True)
           

def hierarchical_prediction(protein_file, ligand_file, compound_library , output_path, topN, Poses_keep , number_worker , time_out , cuda_number ,image_version ):

    protein_file_local = convert_to_absolute(protein_file)
    crystal_ligand_file_local = convert_to_absolute(ligand_file)
    ligand_smi_local = convert_to_absolute(compound_library)
    out_dir_local = convert_to_absolute(output_path)
    number_worker = number_worker 
    time_out = time_out

    protein_file_docker = change_path_local2docker(protein_file_local)
    crystal_ligand_file_docker = change_path_local2docker(crystal_ligand_file_local)
    ligand_smi_docker = change_path_local2docker(ligand_smi_local)
    out_dir_docker = change_path_local2docker(out_dir_local)
    
    cuda_number = cuda_number
    image_version = image_version
    # vs_file preprocess
    print('smiles pre-process')
    vs_file_pre(ligand_smi_docker , number_worker , time_out , image_version)
    ligand_smi_local = get_pre_file_path(ligand_smi_local)
    ligand_smi_docker = change_path_local2docker(ligand_smi_local)
    
    
        
    # karmadock prediction 
    out_dir_karmadock_local = os.path.join(out_dir_local , 'karmadock')
    if not os.path.exists(out_dir_karmadock_local):
        os.mkdir(out_dir_karmadock_local)
    out_dir_karmadock_docker = os.path.join(out_dir_docker , 'karmadock')

    out_dir_carsidock_rtmscore_local = os.path.join(out_dir_local , 'carsidock_rtmscore')
    if not os.path.exists(out_dir_carsidock_rtmscore_local):
        os.mkdir(out_dir_carsidock_rtmscore_local)
    out_dir_carsidock_rtmscore_docker = os.path.join(out_dir_docker , 'carsidock_rtmscore')
    print('karmadock prediction')
    karmadock_prediction(protein_file_docker , crystal_ligand_file_docker , ligand_smi_docker, out_dir_karmadock_docker,cuda_number , image_version)

    # dealt with the prediction result of karmadock.
    os.rename(os.path.join(out_dir_karmadock_local , 'score.csv') , os.path.join(out_dir_karmadock_local , 'karmadock_prediction_initial.csv'))
    karmadock_prediction_file = os.path.join(out_dir_karmadock_local , 'karmadock_prediction_initial.csv')
    karmadock_score_top_smile_txt = os.path.join(out_dir_karmadock_local , 'karmadock_score_top%s_smile.txt'%topN)
    data_dealt = process_karmadock_prediction_files(ligand_smi_local, karmadock_prediction_file,  karmadock_score_top_smile_txt  ,topN)
    data_dealt.to_csv(os.path.join(out_dir_karmadock_local , 'karmadock_prediction.csv') , index=False)
    if os.path.exists(karmadock_prediction_file):
        os.remove(karmadock_prediction_file)
    
    # carsidock_rtmscore prediction 
    print('carsidock prediction')
    carsidock_prediction(protein_file_docker , crystal_ligand_file_docker , change_path_local2docker(karmadock_score_top_smile_txt), out_dir_carsidock_rtmscore_docker,cuda_number , image_version)
    
    # #dealt with the prediction result of carsidock_rtmscore.
    carsidock_score_dat = os.path.join(out_dir_carsidock_rtmscore_local , 'score.dat')
    carsidock_score_csv = os.path.join(out_dir_carsidock_rtmscore_local , 'score.csv')
    convert_txt_to_csv(carsidock_score_dat, carsidock_score_csv)
    carsidock_score_csv_docker = change_path_local2docker(carsidock_score_csv)
    karmadock_score_top_smile_txt_docker = change_path_local2docker(karmadock_score_top_smile_txt)
    
    print('result post-process')
    post_precess(carsidock_score_csv_docker , karmadock_score_top_smile_txt_docker, ligand_smi_docker , image_version)

    os.rename(os.path.join(out_dir_carsidock_rtmscore_local , 'score.csv') , os.path.join(out_dir_carsidock_rtmscore_local , 'carsidock_prediction.csv'))
    if os.path.exists(carsidock_score_dat):
        os.remove(carsidock_score_dat)

def hierarchicalvs():

    try:
        
        parser = argparse.ArgumentParser(description='Process input and output protein files.')
        parser.add_argument('-p', '--protein_file', required=True, help='the path of the protein file.')
        parser.add_argument('-l', '--ligand_file', required=True, help='the  path of the ligand file.')
        parser.add_argument('-cl', '--compound_library', required=True, help='the relative path of the compound library.')
        parser.add_argument('-o', '--output_path', required=True, help='the storage path for the output file')
        parser.add_argument('-n', '--topN', required=True, default = 50 , type = int , help='the Top N molecules for CarsiDock and RTMScore')
        parser.add_argument('-v', '--image_version', required=True, default = 'hier_vs:v8' , type = str , help='the name and version of employed docker image')
        parser.add_argument('-cuda_number', required=False, default = 0 ,  help='cuda device index')
        parser.add_argument('-number_worker', required=False, default = 10 ,  help='the number of cpu processors')
        parser.add_argument('-time_out', required=False, default = 0.5 ,  help='the cutoff time value of pre-process one smile')
        parser.add_argument('-poses_keep', required=False, default = True ,  help='whether to keep the docking poses generated by carsidock')
        args = parser.parse_args()

        protein_file = args.protein_file
        ligand_file = args.ligand_file
        compound_library = args.compound_library
        output_path = args.output_path
        topN = args.topN
        image_version = args.image_version
        cuda_number = args.cuda_number
        number_worker = args.number_worker
        time_out = args.time_out
        Poses_keep = args.poses_keep


        hierarchical_prediction(protein_file =protein_file , ligand_file = ligand_file, compound_library =compound_library, output_path = output_path, \
        topN=topN, Poses_keep = Poses_keep , number_worker = number_worker , time_out = time_out , cuda_number = cuda_number , image_version = image_version)
        


            
    except Exception as e:
    
        print("error:", e)
        sys.exit(1)


# hierarchicalvs()
# if __name__ == "__main__":
#     ligand_smi = '/home/shukai/project/cvsp_aie/online_version/hierarchicalvs-1.1/hierarchicalvs/examples/chemdiv_clustered1.txt'
#     protein_file = '/home/shukai/project/brd4/targets/protein.pdb'
#     crystal_ligand_file = '/home/shukai/project/brd4/targets/ligand.sdf'
#     out_dir = '/home/shukai/project/cvsp_aie/online_version/hierarchicalvs-1.1/hierarchicalvs/out_dir/carsidock_rtmscore'
#     topN=10000
#     Poses_keep = True
#     number_worker = 32
#     time_out = 0.5
#     cuda_number = 1
#     image_version = 'hier_vs:v8'
#     hierarchical_prediction(protein_file , crystal_ligand_file, ligand_smi, out_dir, topN=topN, Poses_keep = Poses_keep , number_worker = number_worker , time_out = time_out , cuda_number = cuda_number , image_version = image_version)




