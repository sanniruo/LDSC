import gzip,argparse,os,multiprocessing,itertools,time
from utils import make_sure_path_exists,progressBar,tmp_bash


def get_unique_pairs(list1,list2):


    # read lists and keep only one instance of each file
    with open(list1) as i: first_list = [elem.strip() for elem in i.readlines()]
    with open(list2) as i: second_list = [elem.strip() for elem in i.readlines()]

    # get all couples possible as the product of both lists
    couples = itertools.product(set(first_list),set(second_list))
    # sort all couples into tuples --> create set in order to remove duplicate entries
    sorted_couples = sorted(list(set([tuple(sorted(list(couple))) for couple in couples])))

    return sorted_couples



def multiproc(couples,args,cpus,out_path,ldsc_path):

    cmd = f"{ldsc_path} {args} --rg FILE1,FILE2 --out {os.path.join(out_path,'ldsc_')}"
    print(cmd)


    params = [[elem[0],elem[1],cmd] for elem in couples]

    print(f"{len(params)} sumstats couples to loop over")

    pool = multiprocessing.Pool(cpus)
    results = pool.map_async(multi_wrapper,params,chunksize=1)
    while not results.ready():
        time.sleep(2)
        progressBar(len(params) - results._number_left,len(params))

    progressBar(len(params) - results._number_left,len(params))
    results = results.get()
    pool.close()

def multi_wrapper(args):
    multi_func(*args)
    return


def multi_func(file1,file2,cmd):
    cmd = cmd.replace("FILE1",file1).replace("FILE2",file2) + f"{os.path.basename(file1).split('.ldsc')[0]}_{os.path.basename(file2).split('.ldsc')[0]}"
    tmp_bash(cmd)


def main(args):

    couples = get_unique_pairs(args.list_1,args.list_2)

    multiproc(couples,args.args,args.cpus,args.o,args.ldsc_path)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description ="Parallelize ldsc generation.")
    parser.add_argument('--list-1',help ='Input files 1',required = True)
    parser.add_argument('--list-2',help ='Input files 2',required = True)
    parser.add_argument('--ldsc-path',help ='Path to ldsc path', required = False, default = 'ldsc.py')
    parser.add_argument("-o",help ="Out path")
    parser.add_argument("--args",help = "ldsc args",required = True,type = str)
    parser.add_argument("--cpus",type = int, help = "number of cpus to use", default =  multiprocessing.cpu_count())

    args = parser.parse_args()
    print(args)
    make_sure_path_exists(args.o)

main(args)
