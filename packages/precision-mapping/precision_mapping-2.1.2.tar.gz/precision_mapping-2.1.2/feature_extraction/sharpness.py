import warnings
import numpy as np
import pandas as pd
import nibabel as nib

from feature_extraction import utils
from cortex_mapping.mapping import get_template_info

from scipy.stats import mode
warnings.filterwarnings('ignore')


def get_boundary_sharpness(args):
    '''Calculates the boundary-sharnpess of each network.

    1. Identify the spatially contiguous clusters that make up the 'networks' label file.
    2. Take the mean BOLD time-series across vertices within the cluster.
    3. At each vertex on the border of the spatial cluster:
        a. Find all the vertices within 'distance' (default=5mm) of this border-vertex.
        b. Calculate the correlation between each of these neighbouring vertex and the cluster time-series.
        c. For each neighbouring network seprately, compare how correlated the correlations within the 
           cluster are to the correlations outside the cluster (cohen's d).
        d. Define this as the network-specific boundary sharpness for the current spatial cluster.
    4. Take the average boundary sharpness across border vertices, write to .csv
    '''

    # Set-up.
    func = args.func
    surf = args.surf
    hemi = args.hemi
    networks = args.networks
    output = args.output
    tmp = f'{args.output}/tmp'

    network_indices, network_labels, _ = get_template_info()
    time_series = utils.get_time_series(func)
    coords = utils.get_surf_coords(surf)
    tree = utils.get_kdtree(surf)
    network_data = nib.load(networks).darrays[0].data

    # Get spatial clusters.
    clusters_gii = nib.load(f'{tmp}/clusters.{hemi}.func.gii')
    borders_gii = nib.load(f'{tmp}/borders.{hemi}.func.gii')


    # --- Define function for calculating sharpness of single cluster ---
    def get_cluster_sharpness(cluster_data, border_data, distance=5):
        '''
        Input:
        cluster_data: boolean array (shape:[n_vertices]) of spatial cluster.
        border_data: boolean array (shape:[n_vertices]) of border vertices.
        distance: Maximum distance for vertices to be considered in sharnpoess calculation (mm).

        Output: 
        cluster_sharpness: dictionary with the mean boundary sharpness across vertices for each network
        cluster_network: the network label with which the current cluster belongs.
        '''

        cluster_data_bool = np.array([bool(x) for x in cluster_data])

        border_vertices = np.argwhere(border_data).flatten()
        cluster_network, _ = mode(network_data[cluster_data_bool])

        # Get cluster time-series (mean BOLD signal across vertices within the cluster).
        cluster_xs = time_series[:,cluster_data_bool].mean(axis=1)

        # Get list of nearby vertices (i.e., those +/- the specified distance) for each border vertex.
        all_nearby_vertices = [np.array(tree.query_ball_point(coords[border_vertex], r=distance)) for border_vertex in border_vertices]
        relevant_vertices = np.unique(np.hstack(all_nearby_vertices))

        # Correlate the time-series of each vertex on the surface with the cluster time-series.
        r_vals = np.zeros(network_data.shape[0])
        r_vals[relevant_vertices] = np.array([np.corrcoef(cluster_xs, vertex_xs)[0,1] for vertex_xs in time_series.T[relevant_vertices]])

        # Get network-wise border-sharpness.
        cluster_sharpness_vertex = {label:[] for label in network_labels}
        for vertex_idx, _ in enumerate(border_vertices):

            nearby_vertices = all_nearby_vertices[vertex_idx]
            vertex_networks = network_data[nearby_vertices]
            inside_corrs = r_vals[nearby_vertices][vertex_networks == cluster_network]

            # Get efect-size difference between r_vals in current network and r_vals in other networks.
            for net_idx, net_label in zip(network_indices, network_labels):

                outside_corrs = r_vals[nearby_vertices][vertex_networks == net_idx]

                # Excude network-network borders with fewer than 5 vertices.
                if len(outside_corrs) < 5: 
                    continue

                seg = utils.get_cohens_d(inside_corrs, outside_corrs)
                cluster_sharpness_vertex[net_label].append(seg)

        cluster_sharpness = {label: np.nanmean(cluster_sharpness_vertex[label]) for label in network_labels}

        return cluster_sharpness, cluster_network


    # Get boundary sharpness of each cluster.
    cluster_sharpness = {idx:[] for idx in network_indices}

    for cluster_darray, border_darray  in zip(clusters_gii.darrays, borders_gii.darrays):

        cluster_data = cluster_darray.data
        border_data = border_darray.data

        sharpness, net_idx = get_cluster_sharpness(cluster_data, border_data)
        cluster_sharpness[net_idx].append(sharpness)

    # Combine into single dataframe and save to output.
    all_df = [pd.DataFrame(cluster_sharpness[idx]).assign(network_idx=idx) for idx in network_indices]
    sharpness_df = pd.concat(all_df, ignore_index=True)
    idx_to_label = dict(zip(network_indices, network_labels))
    sharpness_df['network_label'] =  sharpness_df['network_idx'].map(idx_to_label)

    feature_df = pd.read_csv(f'{output}/features_{hemi}.csv')
    df = pd.concat([feature_df, sharpness_df], axis=1)

    # Reorder columns.
    front_cols = ['cluster_idx', 'network_idx', 'network_label']
    existing_front_cols = [col for col in front_cols if col in df.columns]
    other_cols = [col for col in df.columns if col not in existing_front_cols]
    df = df[existing_front_cols + other_cols]

    # Rename columns.
    df = df.rename(columns={col: f'{col}__sharpness' for col in network_labels})
    df.to_csv(f'{output}/features_{hemi}.csv', index=False)