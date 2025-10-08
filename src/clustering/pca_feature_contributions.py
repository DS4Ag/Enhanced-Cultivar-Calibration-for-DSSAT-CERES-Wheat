def analyze_feature_contributions(data_dir, output_path=None):
    """
        Perform PCA-based feature contribution analysis for multiple data subsets.

        This function loads preprocessed clustering datasets for each treatment group, applies standard scaling,
        and determines the number of principal components to retain using the KneeLocator. It computes feature loadings
        (contributions) for each principal component, displays the most important features for PC1 and PC2, and aggregates
        all results. Optionally, the combined loadings can be saved to a specified output path.

        Parameters:
            data_dir (str): Path to the directory containing input datasets for clustering analysis.
            output_path (str, optional): File path for saving the aggregated feature contributions (default: None).
                                         If not specified, results are not saved to disk.

        Returns:
            None. The function operates for its side effects (printing and optional CSV output).
        """
    import pandas as pd
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from kneed import KneeLocator
    import os

    from .config_paths import feature_contributions_output
    from .variable_mapping import mapping_dict
    from src.clustering.config_paths import labels, paths

    all_loadings = []  # To collect each loading_df with treatment label

    for i, (label, path) in enumerate(zip(labels, paths)):

        # === Standardize the Data ===
        df_wide = pd.read_csv(path)

        # Select numeric columns
        cols_to_use = df_wide.columns.difference(['genotype', 'entry', 'treatment', 'season'])
        filtered_data = df_wide[cols_to_use]

        # Handle missing values
        filtered_data_filled = filtered_data.fillna(filtered_data.mean())

        # Standardize
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(filtered_data_filled)

        # === Determine Number of Components ===
        pca = PCA()
        pca.fit(data_scaled)

        # Explained variance and cumulative sum
        explained_variance = pca.explained_variance_ratio_

        # === Find the Elbow Point Automatically ===
        kl = KneeLocator(
            range(1, len(explained_variance) + 1),
            explained_variance,
            curve="convex",
            direction="decreasing",
            interp_method="polynomial"
        )

        # Extract the optimal number of components from elbow analysis
        elbow_point = int(kl.knee) if kl.knee else 2

        print(f"Number of components for {label}: {elbow_point}")

        # === Apply PCA with Optimal Components ===
        pca_com = PCA(n_components=elbow_point)
        principal_components = pca_com.fit_transform(data_scaled)

        # Create a DataFrame with the principal components
        pc_df = pd.DataFrame(
            data=principal_components,
            columns=[f'PC{i+1}' for i in range(elbow_point)]
        )

        # Add genotype and entry information
        pc_df['genotype'] = df_wide['genotype'].values
        pc_df['entry'] = df_wide['entry'].values

        # === Feature Contributions ===
        # Get feature loadings (correlations between features and PCs)
        loadings = pca_com.components_

        # Create a DataFrame of feature loadings
        loading_df = pd.DataFrame(
            loadings.T,
            columns=[f'PC{i+1}' for i in range(elbow_point)],
            index=cols_to_use
        ).reset_index().rename(columns={'index': 'feature'})

        # Add treatment info from label
        loading_df['data_subset'] = label

        # Append to global list
        all_loadings.append(loading_df)

        # Display top contributing features for first two PCs
        print('Features contributing to PC1:')
        print(loading_df['PC1'].abs().sort_values(ascending=False))

        print('\nFeatures contributing to PC2:')
        print(loading_df['PC2'].abs().sort_values(ascending=False))
        print('\n')

    # Combine all loading dataframes
    combined_loadings_df = pd.concat(all_loadings, ignore_index=True)

    # Map dictionary to DataFrame features
    def map_feature_and_treatment(df, mapping_dict):
        updated_names = []
        treatments = []
        for f in df['feature']:
            if f in mapping_dict:
                updated_names.append(mapping_dict[f][0])
                treatments.append(mapping_dict[f][1])
            else:
                updated_names.append(f)  # Keep original if not found
                treatments.append(None)
        df['future_new_name'] = updated_names
        df['treatment'] = treatments
        return df

    # Apply the mapping to your combined_loadings_df
    combined_loadings_df = map_feature_and_treatment(combined_loadings_df, mapping_dict)

    # Delete old future names column
    combined_loadings_df.drop('feature', axis=1, inplace=True)

    # Rename the future column
    combined_loadings_df.rename(columns={'future_new_name': 'feature'})

    # Move columns to the beginning onf the df
    cols_to_move = ['data_subset', 'treatment', 'future_new_name']
    combined_loadings_df = combined_loadings_df[cols_to_move + [col for col in combined_loadings_df.columns if col not in cols_to_move]]

    # (Optional) Save to CSV
    combined_loadings_df.to_csv(feature_contributions_output, index=False)

