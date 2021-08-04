import os,re,json,argparse
from utils import make_sure_path_exists,progressBar,isfloat,round_sig
from collections import defaultdict

def get_phenos(f):
    """
    Function that extracts the phenotypes 1/2 from the log file
    """

    with open(f) as i:
        for line in i:
            if line.startswith('--rg'):
                line = line.strip().split()
                for string in line:
                    if "," in string and 'ldsc.sumstats.gz' in string:
                        paths = string.split(',')

    pheno1 = os.path.basename(paths[0]).split('.ldsc.sumstats.gz')[0]
    pheno2 = os.path.basename(paths[1]).split('.ldsc.sumstats.gz')[0]

    return pheno1,pheno2


def get_summary(f):
    """
    Returns part with summary, replaces paths with pheno names and formats the summary
    """
    pheno1,pheno2 = get_phenos(f)

    with open(f) as i:lines = i.readlines()
    for i,line in enumerate(lines):
        #finds line with summary
        if line.startswith("Summary of Genetic Correlation Results"):
            index = i

    # reads summary header and content
    header,summary = lines[index+1:index+3]
    header = '\t'.join(header.strip().split()) + '\n'

    #replaces path with pheno
    paths = summary.split()[:2]
    summary = summary.replace(paths[0],pheno1)
    summary = summary.replace(paths[1],pheno2)

    #formats summary output
    summary = '\t'.join(summary.strip().split()) + '\n'

    return header,summary


def save_summaries(file_list,out_path = '/mnt/disks/r7/ldsc/cromwell/'):

    summary_file = out_path + '.ldsc.summary.log'

    with open(file_list) as i: files = [elem.strip() for elem in i]
    to_process = len(files)
    print(f"{to_process} files to parse.")

    header,summary = get_summary(files[0])
    with open(summary_file,'wt') as o:
        o.write(header)
        for i,f in enumerate(files):
            progressBar(i+1,to_process)
            header,summary = get_summary(f)
            o.write(summary)
    print('\ndone.')


def save_h2(file_list,out_path = '/mnt/disks/r7/ldsc/cromwell/'):
    h2_dict = defaultdict(list)

    with open(file_list) as i: files = [elem.strip() for elem in i]
    to_process = len(files)
    print(f"{to_process} files to parse.")

    h2_dict = {}
    #loop over jsons and update dictionary of h2
    for i,f in enumerate(files):
        progressBar(i+1,to_process)
        with open(f , 'r+') as i:
            d = json.load(i)
            h2_dict.update(d)
    print('\ndone.')

    with open(out_path + '.ldsc.heritability.json', 'w') as fp:
        json.dump(h2_dict, fp)

    with open(out_path + '.ldsc.heritability.tsv', 'w') as fp:
        fp.write('\t'.join(["PHENO","H2",'SE',"INT","INT_SE","RATIO","RATIO_SE"]) + '\n')
        for key,value in h2_dict.items():
            fp.write('\t'.join([key] + value) + '\n')


def main(summaries,het,out_path = '/mnt/disks/r7/ldsc/cromwell/'):

    if summaries:
        save_summaries(summaries,out_path)
    if het:
        save_h2(het,out_path)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description ="Gather summaries.")

    parser.add_argument('--summaries',help ='Summaries',default = "")
    parser.add_argument('--het',help ='Het_data',default="")
    parser.add_argument("-o",help ="Out path",default = "./")
    parser.add_argument("--name",default = "finngen_R7")
    args = parser.parse_args()
    print(args)
    make_sure_path_exists(args.o)
    args.o = os.path.join(args.o,args.name)
    main(args.summaries,args.het,args.o)
