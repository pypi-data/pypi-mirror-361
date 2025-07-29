from __future__ import annotations

from typing import Dict, List, Tuple
from tqdm import tqdm
from multiprocessing.pool import AsyncResult
import time
import warnings
from sklearn.neighbors import KDTree
from sklearn.metrics.pairwise import euclidean_distances
from scipy import sparse as sp
import numpy as np
from itertools import product
from Bio.Seq import Seq
from pandas import Series as pd_Series
from polars import Series as pl_Series

from spyce.constants import DNA_ALPHABET
from spyce.dataType import DataLoadingStructure, KMerHistogramObject


class TopicNode(DataLoadingStructure):
    """
    Node class for parsing framework-specific .embed files, which provide hierarchical information by indent
    Instances of this class are nodes in a topic tree that represents the hierarchical structure of the .embed files
    
    :param str indented_line: entire line of file as string including indents
    """
    def __init__(self, indented_line: str):
        self.children = []
        self.level = len(indented_line) - len(indented_line.lstrip())
        self.text = indented_line.strip()

    def add_children(self, topic_nodes: List):
        """
        Add topic children to node
        
        :param List topic_nodes: Topic nodes that are added as children
        :return: None
        """
        childlevel = topic_nodes[0].level
        while topic_nodes:
            tp = topic_nodes.pop(0)
            if tp.level == childlevel:  # add node as a child
                self.children.append(tp)
            elif tp.level > childlevel:  # add nodes as grandchildren of the last child
                topic_nodes.insert(0, tp)
                self.children[-1].add_children(topic_nodes)
            elif tp.level <= self.level:  # this node is a sibling, no more children
                topic_nodes.insert(0, tp)
                return

    def as_dict(self) -> Dict | str:
        """
        Convert hierarchical tree structure of which this node is root as dict
        
        :return Dict | str: tree structure as dict. If leaf node return string
        """
        if len(self.children) > 1:
            child_dict = {} 
            child_list = []
            for tp in self.children:
                tp_dict = tp.as_dict()
                try:
                    child_dict = dict(**child_dict, **tp_dict)
                except TypeError:
                    child_list.append(tp_dict)
            return {self.text: child_dict} if len(child_list) == 0 else {self.text: child_list}
        elif len(self.children) == 1:
            return {self.text: self.children[0].as_dict()}
        else:
            return self.text


def load_specifications(path: str) -> Dict:
    """
    Load an `.embed` file, parse to hierarchical tree, and convert to dict
    
    :param str path: path to .embed file
    :return Dict: python dict with hierarchical information
    """
    root_topic = TopicNode("root")
    with open(path, "r") as spec_file:
        root_topic.add_children([TopicNode(line) for line in spec_file.read().splitlines() if line.strip()])
    return root_topic.as_dict()["root"]


def seq_to_int(seq: str, alphabet: List[str]) -> int:
    """
    Convert a sequence of letters to an integer value given a full alphabet
    
    :param str seq: sequence string, e.g. ACCAGTA
    :param List[str] alphabet: List with single characters representing alphabet
    :return int: integer representing sequence
    """
    alphabet = list(sorted(alphabet))
    value = 0
    for i_letter, letter in enumerate(reversed(seq)):
        value += alphabet.index(letter) * len(alphabet)**i_letter

    return value

def nozero_kmer_to_idx(alphabet: List[str] = DNA_ALPHABET, k: int = 4) -> Dict[str, int]:
    """
    To avoid a bias based in the orientation of the reference genome, we treat a k-mer and its
    reverse implement (for example for `k=3`, `AAT` and `ATT` are treated as the same k-mer).
    This creates many values in the kmer histogram that will always be zero. This function
    returns a dictionary with all present k-mers and their indices.

    :param List[str] alphabet: Alphabet used for creating k-mer histogram.
    :param int k: Length of the k-mers
    :return Dict[str, int]: dictionary with (k-mer, index) key:value pairs.
    """
    kmer_idx_dict = {}
    ctr = 0
    for kmer in sorted(product(alphabet, repeat=k)):
        kmer = "".join(kmer)
        rev_kmer =  str(Seq(kmer).reverse_complement())
        save_kmer = kmer if kmer < rev_kmer else rev_kmer
        if save_kmer in kmer_idx_dict:
            continue
        else:
            kmer_idx_dict[save_kmer] = ctr
            ctr += 1
    return kmer_idx_dict


def fetch_async_result(
        job_list: List[Tuple[int | str, AsyncResult]],
        process_bar: tqdm | None = None,
        max_attempt: int | None = 200  # approx 100 secs
    ) -> List:
    """
    Fetch result from asynchronous job when ready.

    :param List[AsyncResult] job_list: list with asynchronous results.
    :param tqdm | None process_bar: Process bar. If none, no process bar is plotted
    :param int | None max_attempt: Maximum number of attempts to fetch result with half a second
        sleep time between each completed iteration through all remaining open jobs.
    :return List: List with results
    """
    processed_jobs = set()
    results = []
    attempts = 0
    while len(job_list) > 0:
        if attempts > max_attempt:
            warnings.warn("Reached limit of %d attempts without results. Continue." % max_attempt)
            break
        # get first in list
        i, async_res = job_list.pop(0)
        # wait when iterated through entire job list and still unfinished jobs
        if i in processed_jobs:
            # attempt to fetch the same
            attempts += 1
            time.sleep(.5)
            processed_jobs = set()
        processed_jobs.add(i)
        # check if ready and fetch
        if async_res.ready():
            attempts = 0
            results.append((i, async_res.get()))
            if process_bar is not None:
                process_bar.update(1)
        else:
            # otherwise add to end of list.
            job_list.append((i, async_res))
    return results


def get_dist_mat(data: np.ndarray) -> np.ndarray:
    return euclidean_distances(data, data)


def get_nn_mat(
        data: np.ndarray | KMerHistogramObject,
        n_neighbors: int | None = 10,
        radius: float | None = None,
        neighbor_batch: int = 128,
        return_distance: bool = True,
        dr_name: str | None = None,
        verbosity: int = 0,
        verbosity_indent: str = ""
) -> sp.csc_matrix:
    """
    Calculate nearest neighbor adjacency matrix.

    :param np.ndarray | KMerHistogramObject data: Input data of size `(#cells x #features)`
    :param int n_neighbors: Number of nearest neighbors per cell.
    :param float | None radius: Use neighborhood radius around each cell rather than k-nearest neighbors.
    :param int neighbor_batch: Number of cells processed at the same time for finding the nearest neighbors.
    :param bool return_distance: Return distance between cell and neighbors instead of adjacency.
    :param str | None dr_name: Name of dimensionality reduction that should be used.
    :param int verbosity: Verbosity levels.
    :param str verbosity_indent: Prefix that is added to the output.
    :return sp.csc_matrix: Sparse adjacency matrix.
    """
    # number of neighbors must be larger than 1, otherwise only returns autoconnections
    if n_neighbors <= 1:
        raise ValueError("Number of neighbors must be at least 2.")
    
    # check whether data is KMerClass and extract data if necessary
    if isinstance(data, KMerHistogramObject):
        if dr_name is not None and dr_name in data.dr:
            data = data.dr[dr_name]
        else:
            data = data.kmer_hist

    # create KD tree
    kdtree = KDTree(data=data)
    adj_mat = sp.lil_matrix((data.shape[0], data.shape[0]), dtype="float")
    cell_kmer_iterator = tqdm(
        range(0, data.shape[0], neighbor_batch),
        desc="%s\tProgress" % verbosity_indent
    ) if verbosity > 0 else range(0, data.shape[0], neighbor_batch)
    # iterate over all cells to create adjacency matrix
    for i_cell_start in cell_kmer_iterator:
        # if based on neighbors, query with number of neighbors
        if radius is None and n_neighbors is not None:
            dist, neighbor_idc = kdtree.query(
                data[i_cell_start:np.minimum(i_cell_start + neighbor_batch, data.shape[0])],
                k=n_neighbors,
                return_distance=True
            )
            cell_idc = np.repeat(
                np.arange(i_cell_start, np.minimum(i_cell_start + neighbor_batch, data.shape[0]), 1),
                n_neighbors 
            )
        # if based on radius, query neighborhood of input data points
        elif radius is not None:
            dist, neighbor_idc = kdtree.query_radius(
                data[i_cell_start:np.minimum(i_cell_start + neighbor_batch, data.shape[0])],
                r=radius,
                return_distance=True
            )
            cell_idc = np.concatenate([
                i * np.ones(len(neighbor_idc[num]))
                for num, i in enumerate(
                    np.arange(i_cell_start, np.minimum(i_cell_start + neighbor_batch, data.shape[0]), 1)
                )
            ])
            dist = np.concatenate(dist)
            neighbor_idc = np.concatenate(neighbor_idc)
        else:
            raise ValueError("Pass either `n_neighbors` or `radius`.")

        # set adjacency matrix. If flag is set, return distance
        adj_mat[cell_idc, neighbor_idc.reshape(-1)] = dist.reshape(-1) if return_distance else 1.
    adj_mat = adj_mat.tocsc()
    return adj_mat


def match_annotations(
        annot_x: List | np.ndarray | pl_Series | pd_Series,
        annot_y: List | np.ndarray | pl_Series | pd_Series
) -> np.ndarray:
    """
    Return mask for matching annotation labels.

    :param List | np.ndarray | pl_Series | pd_Series annot_x: Cell type annotation
    :param List | np.ndarray | pl_Series | pd_Series annot_y: Cell type annotation `annot_x` is compared to
    :return np.ndarray: Mask for matching labels
    """
    def _convert(annot):
        if isinstance(annot, list):
            annot = np.array(annot)
        elif isinstance(annot_x, pl_Series) or isinstance(annot, pd_Series):
            annot = annot_x.to_numpy()
        return annot
    
    annot_x = _convert(annot_x)
    annot_y = _convert(annot_y)
    return annot_x == annot_y

