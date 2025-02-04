import re
import os
import sys
import argparse
sys.path.append('library')
from library import Cluster,Unique_kmer_detect_direct,Build_kmer_sets_unique_region_lasso_test_allinone_sp,select_rep,Build_overlap_matrix_sp,Build_tree
import time
from collections import defaultdict



__author__="Liao Herui, Ji Yongxin - PhD of City University of HongKong"
usage="StrainScan - A kmer-based strain-level identification tool."

def initial_para(para,value):
	if not para:
		para=value
	return para

def build_dir(in_dir):
	if not os.path.exists(in_dir):
		os.makedirs(in_dir)
def merge_cls(dc_in):
	dc_out=defaultdict(lambda:{})
	for e in dc_in:
		for e2 in dc_in[e]:
			dc_out['C'][e2]=''
	return dict(dc_out)


def mannual(icf,fa_dir):
	dn={} # pre -> full file dir
	for filename in os.listdir(fa_dir):
		pre=re.split('\.',filename)[0]
		dn[pre]=fa_dir+'/'+filename
	f=open(icf,'r')
	dc95_l2=defaultdict(lambda:{})
	while True:
		line=f.readline().strip()
		if not line:break
		ele=line.split('\t')
		st=re.split(',',ele[-1])
		for s in st:
			dc95_l2[int(ele[0])][dn[s]]=''
	return dc95_l2

	

def main():
	pwd=os.getcwd()
	# Get para
	parser=argparse.ArgumentParser(prog='StrainScan_build.py',description=usage)
	parser.add_argument('-i','--input_fasta',dest='input_fa',type=str,required=True,help="The dir of input fasta genome --- Required")
	parser.add_argument('-o','--output_dir',dest='out_dir',type=str,help='Output dir (default: current dir/StrainVote_DB)')
	parser.add_argument('-k','--kmer_size',dest='ksize',type=str,help='The size of kmer, should be odd number. (default: k=31)')
	parser.add_argument('-u','--uk_num',dest='uknum',type=str,help='The maximum number of unique k-mers in each genome to extract. (default: u=100000)')
	parser.add_argument('-g','--gk_ratio',dest='gkratio',type=str,help='The ratio of group-specific k-mers to extract. (default: g=1.0)')

	#parser.add_argument('-l','--input_clster_file',dest='icf',type=str,help='The cluster file offered by users for mannual database construction')

	args=parser.parse_args()
	fa_dir=args.input_fa
	out_dir=args.out_dir
	ksize=args.ksize
	if not args.uknum:
		uknum=100000
	else:
		uknum=int(args.uknum)
	if not args.gkratio:
		gkratio=1.0
	else:
		gkratio=float(args.gkratio)
	ksize=initial_para(ksize,31)

	#icf=args.icf
	'''
	tid=args.tid
	if not tid:
		tid='1747'
	'''

	out_dir=initial_para(out_dir,pwd+'/StrainScan_DB')
	if not re.search('/',out_dir):
		out_dir=pwd+'/'+out_dir
	cls_res=out_dir+'/Cluster_Result'
	#tree_dir=out_dir+'/Tree_database'
	#kk_db=out_dir+'/Krakenuniq_DB'
	#kk_db1=out_dir+'/Krakenuniq_DB/library'
	#kk_db2=out_dir+'/Krakenuniq_DB/taxonomy'
	#uni_kmer=out_dir+'/Unique_Kmer'
	#union_kmer=out_dir+'/Union_Kmer'
	#kmer_sets_l1=out_dir+'/Kmer_Sets_L1'
	kmer_sets_l2=out_dir+'/Kmer_Sets_L2'
	#tem_dir=out_dir+'/Tem_dir'
	

	
	build_dir(out_dir)
	build_dir(cls_res)
	#build_dir(kk_db)
	#build_dir(kk_db1)
	#build_dir(kk_db2)
	#os.system('cp library/taxonomy/* '+kk_db2)
	#build_dir(uni_kmer)
	#build_dir(tree_dir)
	#build_dir(uni_kmer)
	#build_dir(kmer_sets_l1)
	build_dir(kmer_sets_l2)
	#build_dir(tem_dir)
	
	# Construct matrix with dashing (jaccard index)
	matrix=Cluster.construct_matrix(fa_dir)
	
	# -------- Hirarchical clustering Part --------
	#### Default: Single: 0.95, Complete: 0.95
	# ---------------------------------------------
	dc95=Cluster.hcls(matrix,'single','0.05')
	os.system('mv hclsMap_* distance_matrix_rebuild.txt distance_matrix.txt '+cls_res)
	cls_file=cls_res+'/hclsMap_95.txt'
	dc95_rep,dc95_l2=select_rep.pick_rep(cls_res+'/distance_matrix_rebuild.txt',cls_file,cls_res)
	

	# Construct the tree 	
	build_dir(out_dir+'/Tree_database/test')
	build_dir(out_dir+'/Tree_database/nodes_kmer')
	build_dir(out_dir+'/Tree_database/overlap')
	Build_tree.build_tree((cls_res+'/distance_matrix.txt',cls_res+'/hclsMap_95_recls.txt',out_dir+'/Tree_database',31,'single'))
	icf=out_dir+'/Tree_database/hclsMap_95_recls.txt'
	os.system('cp '+out_dir+'/Tree_database/hclsMap_95_recls.txt '+cls_res)
	dc95_l2=mannual(icf,fa_dir)
	# Delete tem dir
	os.system('rm -rf '+out_dir+'/Tree_database/test')



	# --------- Inside cluster strains kmer sets construction -------
	Build_kmer_sets_unique_region_lasso_test_allinone_sp.build_kmer_sets(dc95_l2,kmer_sets_l2,ksize,uknum,gkratio)
	
	
	# --------- Build Overlap matrix -----------
	new_cls_file=out_dir+'/Tree_database/hclsMap_95_recls.txt'
	Build_overlap_matrix_sp.build_omatrix(fa_dir,new_cls_file,kmer_sets_l2+'/Kmer_Sets')

	# --------- Delete tem dir ---------
	os.system('rm -rf '+kmer_sets_l2+'/Colinear_Block')
	


if __name__=='__main__':
	sys.exit(main())
