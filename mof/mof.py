#! /usr/bin/env python3

import argparse
import copy
import datetime
import lzma
import os
import pathlib
import subprocess
import sys
import tarfile

import ete3

GITDIR = os.path.basename(sys.argv[0])[-3:] == ".py"
if GITDIR:
    HERE = pathlib.Path(os.path.abspath(os.path.dirname(sys.argv[0])))
else:
    HERE = pathlib.Path(
        os.path.abspath(os.path.dirname(os.path.realpath(__file__))))

sys.path.append(os.path.dirname(__file__))

#HERE = pathlib.Path(__file__).parent.resolve()
#HERE = pathlib.Path(sys.path[0])
#HERE = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))

EXAMPLE_ACC = "ERR486847"

#CLUSTERS_FN=pkg_resources.resource_filename('wof', 'data/clusters.tar.gz')
#URLS_FN=pkg_resources.resource_filename('wof', 'data/downloads.tsv')
#TREES_FN=pkg_resources.resource_filename('wof', 'data/trees.tar.gz')
CLUSTERS_FN = HERE / "data/clusters.tar.gz"
URLS_FN = HERE / "data/downloads.tsv"
TREES_FN = HERE / "data/trees.tar.gz"

##################
# Aux functions
##################


def log(*args):
    dt = datetime.datetime.now()
    print(f"[{dt}]", *args, file=sys.stderr)


def error(*args):
    dt = datetime.datetime.now()
    print(f"[{dt}] Error:", *args, file=sys.stderr)


def shell(cmd, directory="."):
    wrap = f'set -eo pipefail; mkdir -p "{directory}" && (cd "{directory}" && ({cmd}))'
    log("Running:", wrap)
    return_code = subprocess.call([f'/bin/bash', '-c', wrap])
    if return_code != 0:
        error(f"Command '{cmd}' failed")
        sys.exit(return_code)


def is_file(fn):
    return True


def compute_md5(fn):
    d = os.path.dirname(fn)
    f = os.path.basename(fn)
    cmd = 'cat "{fn}" | md5sum > "{fn}.md5")'


def check_md5(fn):
    return True


def check_cluster(fn):
    return True


###
# DB
##


def get_clusters_urls():
    d = {}
    with open(URLS_FN) as f:
        l = [x.strip().split("\t") for x in f]
    return dict(l)


def get_clusters_accs():
    d = {}
    with tarfile.open(CLUSTERS_FN) as tar:
        for member in tar.getmembers():
            f = tar.extractfile(member)
            content = f.read()
            accs = content.decode('ascii').split()
            name = member.name.replace(".txt", "")
            d[name] = accs
    return d


def determine_clusters(output_objects):
    log("Determine clusters for:", output_objects)
    d = {}
    da = get_clusters_accs()
    for k in da:
        d[k] = k
        for a in da[k]:
            d[a] = k
    #print(d)
    cl0 = [d[x] for x in output_objects]
    cl = sorted(list(set(cl0)))
    log("Determined as:", cl)
    return cl


def get_tree(cluster):
    with tarfile.open(TREES_FN) as f:
        handle = f.extractfile(f'{cluster}.nw')
        lines = handle.readlines()  # show file contents
    newick_line = lines[0].decode()
    return ete3.Tree(newick_line, format=1)


##################
# Info messages
##################


def print_clusters(header=False, urls=True, accessions=False):
    du = get_clusters_urls()
    if accessions:
        da = get_clusters_accs()

    if header:
        header = ["cluster"]
        if urls:
            header.append("url")
        if accessions:
            header.append("accessions")
        print(*header, sep="\t")

    for k in sorted(du):
        to_print = [k]
        if urls:
            to_print.append(du[k])
        if accessions:
            to_print.append(da[k])
        print(*to_print, sep="\t")


##################
# Downloads
##################


def download_cluster(cluster):
    log(f"Download cluster: {cluster}")
    du = get_clusters_urls()
    #print(du)
    print(cluster)
    url = du[cluster]
    cmd = f'wget --continue "{url}"'
    shell(cmd, "cache/downloads")
    fn = f"{cluster}.fa.xz"
    if not is_file(f"{fn}.md5"):
        compute_md5(fn)
    #check_download_md5(fn)


def fetch_cluster_files(objects):
    clusters = determine_clusters(objects)
    for x in clusters:
        download_cluster(x)


##################
# Pre-processing
##################


def _split_xz(fn, directory):
    log(f"Dumping node block fasta files")
    shell("true", directory)

    def _get_node_from_header(line):
        #print( line.lstrip("@"))
        name, _, _ = line.partition("@")
        assert (len(name) > 1)
        return name[1:]

    def _print_buffer(buf, directory):
        if len(buf) == 0:
            return
        name = _get_node_from_header(buf[0])
        dump_fn = f"node_{name}.fa"
        #log(f"Dumping {dump_fn}")
        with open(os.path.join(directory, dump_fn), "w") as f:
            f.write("".join(buf))

    bfr = []
    with lzma.open(fn, "rt") as f:
        for i, x in enumerate(f):
            if len(x) == 0:
                continue
            if x[0] == ">" and x[-4:] == "@c1\n":
                _print_buffer(bfr, directory)
                bfr = [x]
            else:
                bfr.append(x)
        _print_buffer(bfr, directory)


def _compress_nodes(dn):
    log(f"Compressing node block fasta files")
    shell('find . -name "*.fa" | parallel --progress gzip -fv', dn)


def _complete_nodes(dn, tree):
    log(f"Completing empty blocks")
    node_names = [f"node_{x.name}.fa.gz" for x in tree.traverse()]
    n = 500
    touch_groups = [node_names[i:i + n] for i in range(0, len(node_names), n)]
    for x in touch_groups:
        shell("touch {}".format(" ".join(x)), dn)


#def _tar_node(dn, name):
#    cmd = f'(cd "{dn}" && tar -cvf {name}.tar node*.gz)'
#    cmd = f'(cd "{dn}" && rm -f node*.gz)'
#    #compute_md5()


def _prep_one(cluster):
    bl = f"cache/blocks/{cluster}"
    _split_xz(f"cache/downloads/{cluster}.fa.xz", directory=bl)
    _compress_nodes(bl)
    tree = get_tree(cluster)
    _complete_nodes(bl, tree)


def prep(objects):
    clusters = determine_clusters(objects)
    for x in clusters:
        _prep_one(x)


##################
# Building
##################


def _build_one(cluster):
    directory = f"output/{cluster}"

    def _bytes_from_file(fn):
        return open(fn, "rb").read()

    def _process_node(node, stack):
        name = node.name

        fn = f"cache/blocks/{cluster}/node_{name}.fa.gz"
        stack.append(_bytes_from_file(fn))
        if node.is_leaf():
            log(f"Creating {name}.fa.gz")
            with open(f"{directory}/{name}.fa.gz", "wb+") as f:
                for y in stack:
                    f.write(y)
        else:
            for x in node.children:
                stack2 = copy.copy(stack)
                _process_node(x, stack2)

    shell("true", directory)
    tree = get_tree(cluster)
    _process_node(tree, [])


def build(objects):
    clusters = determine_clusters(objects)
    for x in clusters:
        _build_one(x)


##################
# Main
##################


def main():
    log("MoF starting")
    #print_clusters()
    #sys.exit()
    desc1 = f"Example:\n   mof get {EXAMPLE_ACC}"

    desc2 = """    main command:
        get       Get genomes

    substeps:
        fetch     Download cluster binary
        prep      Preprocess node blocks
        build     Build k-mer sets from blocks

    information about the database:
        clusters  Print list of clusters
        search    Search genomes
        info      Detailed info on genomes\
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc1)

    subparsers = parser.add_subparsers(title='commands',
                                       description=desc2,
                                       help='',
                                       dest='cmd')
    subparsers.required = True

    #parser.add_argument("-v", ...)

    g_parser = subparsers.add_parser("get")

    f_parser = subparsers.add_parser("fetch")
    p_parser = subparsers.add_parser("prep")
    b_parser = subparsers.add_parser("build")

    c_parser = subparsers.add_parser("clusters")
    s_parser = subparsers.add_parser("search")
    i_parser = subparsers.add_parser("info")

    ######################################
    g_parser.add_argument(
        'what',
        nargs='+',
        help='Objects to download (accessions, clusters)',
    )
    ######################################
    f_parser.add_argument(
        'what',
        nargs='+',
        help='Objects to download (accessions, clusters)',
    )
    ######################################
    p_parser.add_argument(
        'what',
        nargs='+',
        help='Objects to prepare (accessions, clusters)',
    )
    ######################################
    b_parser.add_argument(
        'what',
        nargs='+',
        help='Objects to build (accessions, clusters)',
    )
    ######################################
    c_parser.add_argument(
        '-u',
        '--urls',
        dest='u',
        action='store_true',
        help='Print URLs',
    )

    c_parser.add_argument(
        '-a',
        '--accessions',
        dest='a',
        action='store_true',
        help='Print accessions',
    )

    c_parser.add_argument(
        '-H',
        '--header',
        dest='h',
        action='store_true',
        help='Print header',
    )

    args = parser.parse_args()
    #print(args)
    if args.cmd == 'clusters':
        print_clusters(urls=args.u, accessions=args.a, header=args.h)
    elif args.cmd == 'fetch':
        fetch_cluster_files(objects=args.what)
    elif args.cmd == 'prep':
        prep(objects=args.what)
    elif args.cmd == 'build':
        build(objects=args.what)
    elif args.cmd == 'get':
        fetch_cluster_files(objects=args.what)
        prep(objects=args.what)
        build(objects=args.what)
    log("MoF successfully finished")


if __name__ == "__main__":
    main()
