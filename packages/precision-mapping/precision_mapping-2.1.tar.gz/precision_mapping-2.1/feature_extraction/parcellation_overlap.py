import numpy as np
import pandas as pd
import pandas as pd
import nibabel as nib

from importlib import resources
from scipy.spatial.distance import dice


def get_parcellation_overlaps(args):

    # Set-up.
    hemi = args.hemi
    output = args.output
    tmp = f'{args.output}/tmp'
    clusters_file = f'{tmp}/clusters.{hemi}.func.gii'

    def get_cluster_overlap(cluster):

        # Measure Dice coefficient between cluster and Glasser/Desikan parcellations.
        glasser_overlap = {}
        for idx, label in enumerate(glasser_labels):
            glasser_overlap[str(label)] = round(1 - dice(cluster, (glasser == idx)),3)

        desikan_overlap = {}
        for idx, label in enumerate(desikan_labels):
            desikan_overlap[str(label)] = round(1 - dice(cluster, (desikan == idx)),3)

        # Remove non-overlapping ROIs from dict.
        glasser_overlap = {key: value for key, value in glasser_overlap.items() if value != 0.0}
        desikan_overlap = {key: value for key, value in desikan_overlap.items() if value != 0.0}

        # Sort dict by most to least overlap.
        glasser_overlap = dict(sorted(glasser_overlap.items(), key=lambda item: item[1], reverse=True))
        desikan_overlap = dict(sorted(desikan_overlap.items(), key=lambda item: item[1], reverse=True))

        return desikan_overlap, glasser_overlap


    # Load Desikan and Glasser parcellations.
    desikan_file = resources.files('cortex_mapping.data.parcellations') / f'Desikan.32k.{hemi}.label.gii'
    glasser_file = resources.files('cortex_mapping.data.parcellations') / f'Glasser_2016.32k.{hemi}.label.gii'

    desikan_gii = nib.load(desikan_file)
    glasser_gii = nib.load(glasser_file)

    # Get label-names.
    desikan_labels = np.array([gii_label.label for gii_label in desikan_gii._labeltable.labels])
    glasser_labels = np.array([gii_label.label for gii_label in glasser_gii._labeltable.labels])

    # Get label-indexed arrays.
    desikan = desikan_gii.darrays[0].data
    glasser = glasser_gii.darrays[0].data

    # Load clusters.
    clusters_gii = nib.load(clusters_file)

    # Calculate overlaps.
    desikan_overlaps = []
    glasser_overlaps = []
    for cluster in clusters_gii.darrays:
        desikan_overlap, glasser_overlap = get_cluster_overlap(cluster.data)
        glasser_overlaps.append(glasser_overlap)
        desikan_overlaps.append(desikan_overlap)

    # Add parcellation overlaps to feature dataframe.
    feature_df = pd.read_csv(f'{output}/features_{hemi}.csv')
    feature_df['desikan_overlap'] = [str(overlap_dict) for overlap_dict in desikan_overlaps]
    feature_df['glasser_overlap'] = [str(overlap_dict) for overlap_dict in glasser_overlaps]

    feature_df.to_csv(f'{output}/features_{hemi}.csv', index=False)
