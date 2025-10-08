def generate_integrated_cluster_figure():
    """
    Generate a comprehensive multi-panel figure combining:
    (a) PCA explained variance plots (elbow method),
    (b) hierarchical clustering dendrograms (with silhouette and WCSS cutoffs),
    (c) PCA-based KMeans cluster scatter plots with genotype labels.

    The function processes multiple datasets (defined in config_paths),
    applies PCA and clustering methods, and generates a figure.

    Outputs:
    - High-resolution figure saved to `final_figure_output`
    - Cluster assignments for each genotype saved to `cluster_csv_output`
    """

    #############################################################################
    # ====== Imports libaries  ======
    ##############################################################################

    # ====== Data Handling & Visualization ======
    import pandas as pd
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    from matplotlib.lines import Line2D
    from matplotlib import gridspec as mgs  # Nested grids for layout management

    # ====== Dimensionality Reduction & Clustering ======
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import AgglomerativeClustering, KMeans
    from sklearn.metrics import silhouette_score
    from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
    from kneed import KneeLocator  # Detect optimal elbow/knee in curves

    # ====== Plot Annotation Utilities ======
    from adjustText import adjust_text  # Improves label placement

    # ====== Internal Project Modules ======
    from .manual_offsets import manual_offsets  # Entry label offsets for scatter plots
    from .config_paths import final_figure_output, labels, paths
    from .load_data import load_clustering_data  # Load all datasets as dictionary

    from .plot_style import (
        font_name, fontsize_title, fontsize_medium, fontsize_tick, fontsize_small, fontsize_big,
        grid_linestyle, grid_linewidth, grid_alpha,
        line_color, line_width, marker_style, marker_size,
        above_threshold_color, threshold_line_style_list,
        marker_size_pca, edgecolor, line_width_pca, marker_styles,
        leaf_rotation, color_threshold,
        legend_font, legend_title_font, method_colors
    )

    ##############################################################################
    # ====== Create Combined Figure Layout ======
    ##############################################################################

    fig = plt.figure(figsize=(23, 13))
    gs = mgs.GridSpec(
        2, 2,
        width_ratios=[2, 4],  # Left = elbow + dendro, Right = scatter (wider)
        height_ratios=[1, 1],  # Top = elbow, Bottom = dendrogram
        wspace=0.30,  # Space between columns
        hspace=0.6,  # Space between elbow and dendrogram
        figure=fig
    )

    ##############################################################################
    # ====== Panel 1: PCA Explained Variance (2x2) ======
    ##############################################################################
    # Set up subplot grid dimensions (2x2 grid)
    nrows, ncols = 2, 2

    # Create 2x2 grid inside the top-left panel
    gs_elbow = mgs.GridSpecFromSubplotSpec(
        nrows, ncols, subplot_spec=gs[0, 0], hspace=0.25, wspace=0.1
    )

    # Create 2x2 grid inside the top-left panel with shared axes
    elbow_axes = []

    for i in range(nrows):
        for j in range(ncols):
            if i == 0 and j == 0:
                # First subplot: no shared axes
                ax = fig.add_subplot(gs_elbow[i, j])
                ref_ax = ax  # Save reference for sharing
            else:
                ax = fig.add_subplot(gs_elbow[i, j], sharex=ref_ax, sharey=ref_ax)
            elbow_axes.append(ax)

    # Create the plot
    for i, (label, path) in enumerate(zip(labels, paths)):

        # === Standardize the Data ===
        # Read the file
        df_wide = pd.read_csv(path)

        # Select numeric columns
        cols_to_use = df_wide.columns.difference(['genotype', 'entry', 'treatment', 'season'])

        # Handle missing values
        filtered_data = df_wide[cols_to_use].fillna(df_wide[cols_to_use].mean())

        # Standardize data
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(filtered_data)

        # === PCA Analysis ===
        pca = PCA()  # Initialize PCA object
        pca.fit(data_scaled)

        # Explained variance and cumulative sum
        explained_variance = pca.explained_variance_ratio_  # Variance explained by each component
        cumulative_variance = np.cumsum(explained_variance)  # Cumulative variance

        # === Find the Elbow Point Automatically ===
        x_values = range(1, len(explained_variance) + 1)

        # Use KneeLocator to find the elbow point
        kl = KneeLocator(
            x_values,
            explained_variance,
            curve="convex",
            direction="decreasing",
            interp_method="polynomial"
        )

        elbow_point = kl.knee

        # === Plotting the Cumulative Explained Variance ===

        # Get the current subplot from the flattened axes array
        ax = elbow_axes[i]

        # Plot cumulative explained variance curve with markers at each component
        ax.plot(
            x_values,  # X-axis: number of components
            explained_variance,  # Y-axis: cumulative variance
            marker=marker_style,
            color=line_color,
            linewidth=line_width,
            markersize=marker_size
        )

        # Add vertical line at elbow point
        if elbow_point:
            ax.axvline(x=elbow_point, color='blue', linestyle='--', linewidth=2, alpha=0.7)
            ax.annotate(
                f'PC: {elbow_point}', fontname=font_name,
                xy=(elbow_point, explained_variance[elbow_point - 1]),
                xytext=(elbow_point + 2, explained_variance[elbow_point - 1] + 0.02),
                arrowprops=dict(arrowstyle='-', color='black', alpha=0.7),
                fontsize=fontsize_small, color='black'
            )

        # Add a title to the subplot showing which dataset is being visualized
        ax.set_title(label, fontsize=fontsize_medium, fontname=font_name)

        # Set tick font size
        ax.tick_params(axis='both', which='both', labelsize=fontsize_tick)

        # Set tick font name
        for label_tick in ax.get_xticklabels() + ax.get_yticklabels():
            label_tick.set_fontname(font_name)

        ax.grid(True, linestyle=grid_linestyle, linewidth=grid_linewidth, alpha=grid_alpha)

        # Add grid lines to improve readability of variance values
        ax.grid(True, linestyle=grid_linestyle, linewidth=grid_linewidth, alpha=grid_alpha)

        # Hide x-axis tick labels except on the bottom row
        if i // ncols < nrows - 1:
            ax.tick_params(labelbottom=False)

        # Hide y-axis tick labels except on the first column
        if i % ncols != 0:
            ax.tick_params(labelleft=False)

    # === Add general axis labels only for the elbow panel area ===
    # Compute bounding box that includes all elbow subplots
    bbox_elbow_all = mpl.transforms.Bbox.union([ax.get_position() for ax in elbow_axes])

    # Add Y-axis label (centered)
    fig.text(
        bbox_elbow_all.x0 - 0.04,  # Shift left of elbow panel
        (bbox_elbow_all.y0 + bbox_elbow_all.y1) / 2,  # Vertical center
        'Explained variance ratio',
        va='center', ha='center', rotation='vertical',
        fontsize=fontsize_medium, fontname=font_name,
    )

    # Add X-axis label (centered)
    fig.text(
        (bbox_elbow_all.x0 + bbox_elbow_all.x1) / 2,  # Horizontal center
        bbox_elbow_all.y0 - 0.05,  # Below elbow panel
        'Number of components',
        ha='center', va='center',
        fontsize=fontsize_medium, fontname=font_name,
    )

    ##############################################################################
    # ====== Panel 2: Dendrograms (Empty Placeholder) ======
    ##############################################################################

    # Create 2x2 grid inside the bottom-left panel
    gs_dendo = mgs.GridSpecFromSubplotSpec(
        nrows, ncols, subplot_spec=gs[1, 0], hspace=0.55, wspace=0.1
    )

    # Create 2x2 grid inside the top-left panel with shared axes
    dendo_axes = []

    for i in range(nrows):
        for j in range(ncols):
            if i == 0 and j == 0:
                # First subplot: no shared axes
                ax = fig.add_subplot(gs_dendo[i, j])
                ref_ax = ax  # Save reference for sharing
            else:
                ax = fig.add_subplot(gs_dendo[i, j], sharex=ref_ax, sharey=ref_ax)
            dendo_axes.append(ax)

    # === Apply PCA with Optimal Components ===
    nrows, ncols = 2, 2

    # Create storage for linkage matrices and distances
    all_linkage_matrices = []
    all_distances_silhouette = {}
    all_distances_wcss = {}

    for i, (label, path) in enumerate(zip(labels, paths)):

        # === Standardize the Data ===
        # Read the file
        df_wide = pd.read_csv(path)

        # Select numeric columns
        cols_to_use = df_wide.columns.difference(['genotype', 'entry', 'treatment', 'season'])
        filtered_data = df_wide[cols_to_use]

        # Handle missing values
        filtered_data_filled = filtered_data.fillna(filtered_data.mean())

        # Standardize data
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(filtered_data_filled)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # === Determine Number of Components ===
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        pca = PCA()  # Initialize PCA object
        principal_components = pca.fit(data_scaled)  # Fit PCA to scaled data

        # Explained variance and cumulative sum
        explained_variance = pca.explained_variance_ratio_

        # === Find the Elbow Point Automatically ===
        x_values = range(1, len(explained_variance) + 1)
        kl = KneeLocator(
            x_values,
            explained_variance,
            curve="convex",
            direction="decreasing",
            interp_method="polynomial"
        )

        # Extract the optimal number of components from elbow analysis
        elbow_point = kl.knee
        if elbow_point is None:
            elbow_point = 2
        else:
            elbow_point = int(elbow_point)

        # ===  Apply PCA with Optimal Components ===
        pca = PCA(n_components=elbow_point)
        principal_components = pca.fit_transform(data_scaled)

        # Perform hierarchical clustering
        linked = linkage(principal_components, method='ward')

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # === Silhouette analysis to evaluate optimal number of clusters ===
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        silhouette_scores = []
        range_n_clusters = range(2, 11)  # Evaluate from 2 to 10 clusters

        # Loop over possible cluster numbers and calculate silhouette scores
        for n_clusters in range_n_clusters:
            # Perform Agglomerative Clustering
            clusterer = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
            labels_pca = clusterer.fit_predict(principal_components)

            # Compute silhouette score to measure cluster quality
            score = silhouette_score(principal_components, labels_pca)
            silhouette_scores.append(score)

        # === Find the number of clusters with the highest silhouette score ===
        optimal_clusters_silhouette = range_n_clusters[np.argmax(silhouette_scores)]

        # === Determine the threshold distance in the dendrogram to cut for optimal clusters ===
        distances = linked[:, 2]  # Extract distances from linkage matrix
        threshold_silhouette = ((sorted(distances, reverse=True)[optimal_clusters_silhouette - 1]) + (
        sorted(distances, reverse=True)[
            optimal_clusters_silhouette - 2])) / 2  # Distance corresponding to cluster cutoff

        # Store linkage matrix and distances
        all_linkage_matrices.append(linked)
        all_distances_silhouette[label] = (optimal_clusters_silhouette, threshold_silhouette)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # === Plot 1: Elbow curve (WCSS vs. number of clusters) ===
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        def elbow_method_for_hierarchical_clustering(data, linked, max_clusters=10):
            """
            Calculate Within-Cluster Sum of Squares (WCSS) for hierarchical clustering
            to identify the optimal number of clusters using the elbow method.
            """

            # Initialize list to store WCSS for each cluster count (k=1 to k=max_clusters)
            wcss = []

            # Iterate through possible cluster counts (k=1 to k=max_clusters)
            for k in range(1, max_clusters + 1):
                # Assign data points to clusters using hierarchical clustering results
                clusters = fcluster(linked, k, criterion='maxclust')  # 'maxclust' ensures exactly k clusters

                # Calculate WCSS for current cluster count
                temp_wcss = 0

                # Process each cluster to compute its contribution to total WCSS
                for cluster_label in np.unique(clusters):
                    # Extract data points belonging to the current cluster
                    cluster_points = data[clusters == cluster_label]

                    # Compute cluster centroid (mean of all points in the cluster)
                    centroid = cluster_points.mean(axis=0)

                    # Sum squared distances from points to centroid (cluster compactness)
                    temp_wcss += np.sum((cluster_points - centroid) ** 2)

                # Append WCSS for current k to the results list
                wcss.append(temp_wcss)

            return wcss

        # === Compute WCSS values for 1 to max_clusters ===
        max_clusters = 10
        wcss = elbow_method_for_hierarchical_clustering(principal_components, linked, max_clusters)

        # === Determine the optimal number of clusters using the "knee" in the curve ===
        kl = KneeLocator(range(1, max_clusters + 1), wcss, curve='convex', direction='decreasing')
        optimal_clusters_wcss = kl.elbow if kl.elbow is not None else 2  # fallback to 2 if elbow is not found

        # === Determine distance threshold for cutting dendrogram ===
        # Sort distances (linkage distances) and average two around the optimal split
        sorted_distances = sorted(distances, reverse=True)
        threshold_wcss = (
                (sorted_distances[optimal_clusters_wcss - 1] + sorted_distances[optimal_clusters_wcss - 2]) / 2
        )

        all_distances_wcss[label] = (optimal_clusters_wcss, threshold_wcss)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # === Create dendrograms ===
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Find global maximum distance across all dendrograms
    max_global_distance = max([linked[:, 2].max() for linked in all_linkage_matrices])

    # Create the color palette
    palette = sns.color_palette('twilight_shifted', n_colors=optimal_clusters_silhouette)

    # Second loop: Create dendrograms with systematic cluster selection
    for i, (label, path) in enumerate(zip(labels, paths)):

        # Read the file
        df_wide = pd.read_csv(path)

        # Assign the i-th element from the axes array to the variable ax
        ax = dendo_axes[i]

        # Generate dendrogram visualization using the stored linkage matrix
        dend = dendrogram(
            all_linkage_matrices[i],
            ax=ax,
            labels=df_wide['entry'].tolist(),
            leaf_font_size=fontsize_small,
            leaf_rotation=leaf_rotation,
            color_threshold=color_threshold,
            above_threshold_color=above_threshold_color,
            no_plot=False  # Make sure we get the dendrogram data
        )

        # Get cluster assignments using the optimal number of clusters from silhouette analysis
        cluster_info_silhouette = all_distances_silhouette[label]
        optimal_clusters = cluster_info_silhouette[0]  # Number of clusters

        # Get cluster assignments for each data point
        cluster_assignments = fcluster(all_linkage_matrices[i], optimal_clusters, criterion='maxclust')

        # Map the dendrogram leaf order to cluster assignments
        leaf_order = dend['leaves']  # Order of leaves in the dendrogram
        leaf_clusters = [cluster_assignments[leaf_idx] for leaf_idx in leaf_order]

        # Apply colors to x-axis labels based on cluster assignment
        xlabels = ax.get_xticklabels()
        for j, (xlabel, cluster) in enumerate(zip(xlabels, leaf_clusters)):
            color = palette[cluster - 1]  # cluster labels start from 1, palette indices from 0
            xlabel.set_color(color)

        # Horizontal lines
        line_position_silhouette = cluster_info_silhouette[1]
        num_clusters_silhouette = cluster_info_silhouette[0]

        # Add threshold silhouette line
        ax.axhline(y=line_position_silhouette + 0.3, color=method_colors['silhouette'],
                   linestyle=threshold_line_style_list[1], linewidth=1.5)
        ax.text(2, line_position_silhouette + 0.7, f'{num_clusters_silhouette} clusters',
                color=method_colors['silhouette'], fontsize=fontsize_medium)

        # Add horizontal lines for WCSS method
        cluster_info_wcss = all_distances_wcss[label]
        line_position_wcss = cluster_info_wcss[1]
        num_clusters_wcss = cluster_info_wcss[0]

        # Add threshold WCSS method line
        ax.axhline(y=line_position_wcss, color=method_colors['wcss'],
                   linestyle=threshold_line_style_list[3], linewidth=1.5)
        ax.text(2, line_position_wcss - 1.2, f'{num_clusters_wcss} clusters',
                color=method_colors['wcss'], fontsize=fontsize_medium)

        # Set subplot title and axis labels
        ax.set_ylim(0, max_global_distance * 1.05)
        ax.tick_params(axis='x', labelsize=fontsize_small, labelrotation=90)
        ax.set_title(label, fontsize=fontsize_medium, fontname=font_name)
        ax.grid(True, linestyle=grid_linestyle, linewidth=grid_linewidth, alpha=grid_alpha)

        # Hide y-axis tick labels except on the first column
        if i % ncols != 0:
            ax.tick_params(labelleft=False)

        # Only add y-axis label to leftmost subplots in the grid
        if i % ncols == 0:
            # Ensure y-axis tick labels use the correct font settings
            for label_tick in ax.get_yticklabels():
                label_tick.set_fontname(font_name)
                label_tick.set_fontsize(fontsize_tick)

    # === Add general axis labels only for the elbow panel area ===
    # Compute bounding box that includes all elbow subplots
    bbox_dendo_all = mpl.transforms.Bbox.union([ax.get_position() for ax in dendo_axes])

    # Add Y-axis label (centered)
    fig.text(
        bbox_dendo_all.x0 - 0.04,  # Shift left of elbow panel
        (bbox_dendo_all.y0 + bbox_dendo_all.y1) / 2,  # Vertical center
        'Distance',
        va='center', ha='center', rotation='vertical',
        fontsize=fontsize_medium, fontname=font_name,
        fontweight='normal'
    )

    # Add X-axis label (centered)
    fig.text(
        (bbox_dendo_all.x0 + bbox_dendo_all.x1) / 2,  # Horizontal center
        bbox_dendo_all.y0 - 0.05,  # Below elbow panel
        'Cultivar',
        ha='center', va='center',
        fontsize=fontsize_medium, fontname=font_name,
        fontweight='normal'
    )

    # Create legend handles
    legend_elements = [
        Line2D([0], [0], color=method_colors['silhouette'], linestyle=threshold_line_style_list[0],
               linewidth=2, label='Silhouette score'),
        Line2D([0], [0], color=method_colors['wcss'], linestyle=threshold_line_style_list[1],
               linewidth=2, label='Elbow method (WCSS)')
    ]

    # Add a general legend to the figure (outside the subplots)
    dendo_axes[0].legend(
        handles=legend_elements,
        loc='upper center',
        bbox_to_anchor=(1, -2.35),
        ncol=2,
        fontsize=fontsize_medium,
        frameon=True,
        columnspacing=1.2,
        handletextpad=0.0,
    )

    ##############################################################################
    # ====== Panel 3: PCA Clusters Scatter Plots (Empty Placeholder) ======
    ##############################################################################

    # Set up subplot grid dimensions (2x2 grid)
    nrows, ncols = 2, 2

    # Create 2x2 grid inside the bottom-left panel
    gs_scatter = mgs.GridSpecFromSubplotSpec(
        nrows, ncols, subplot_spec=gs[:, 1], hspace=0.25, wspace=0.2
    )

    # Create 2x2 grid inside the top-left panel with shared axes
    scatter_axes = []

    for i in range(nrows):
        for j in range(ncols):
            if i == 0 and j == 0:
                # First subplot: no shared axes
                ax = fig.add_subplot(gs_scatter[i, j])
                ref_ax = ax  # Save reference for sharing
            else:
                ax = fig.add_subplot(gs_scatter[i, j], sharex=ref_ax, sharey=ref_ax)
            scatter_axes.append(ax)

    # Prepare to collect handles and labels for a single legend
    all_handles = []
    all_labels = []

    # Initialize an empty list to collect cluster DataFrames
    cluster_dfs = []

    # Iterate through each dataset (label and file path)
    for i, (label, path) in enumerate(zip(labels, paths)):

        # === Standardize the Data ===
        # Read the file
        df_wide = pd.read_csv(path)

        # Select numeric columns
        cols_to_use = df_wide.columns.difference(['genotype', 'entry', 'treatment', 'season'])
        filtered_data = df_wide[cols_to_use]

        # Handle missing values
        filtered_data_filled = filtered_data.fillna(filtered_data.mean())

        # Standardize data
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(filtered_data_filled)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # === Determine Number of Components ===
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        pca = PCA()  # Initialize PCA object
        principal_components = pca.fit(data_scaled)  # Fit PCA to scaled data

        # Explained variance and cumulative sum
        explained_variance = pca.explained_variance_ratio_

        # === Find the Elbow Point Automatically ===
        x_values = range(1, len(explained_variance) + 1)
        kl = KneeLocator(
            x_values,
            explained_variance,
            curve="convex",
            direction="decreasing",
            interp_method="polynomial"
        )

        # Extract the optimal number of components from elbow analysis
        elbow_point = kl.knee
        if elbow_point is None:
            elbow_point = 2
        else:
            elbow_point = int(elbow_point)

        # === Apply PCA with Optimal Components ===
        pca_com = PCA(n_components=elbow_point)
        principal_components = pca_com.fit_transform(data_scaled)

        # Create a DataFrame with the principal components
        pc_df = pd.DataFrame(
            data=principal_components,
            columns=[f'PC{i + 1}' for i in range(elbow_point)]
        )

        # Add genotype and entry information
        pc_df['genotype'] = df_wide['genotype'].values
        pc_df['entry'] = df_wide['entry'].values

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # === Silhouette analysis to evaluate optimal number of clusters ===
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        silhouette_scores = []
        max_clusters = min(11, len(principal_components))
        range_n_clusters = range(2, max_clusters)
        for n_clusters in range_n_clusters:
            clusterer = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
            labels_pca = clusterer.fit_predict(principal_components)
            score = silhouette_score(principal_components, labels_pca)
            silhouette_scores.append(score)
        optimal_clusters_silhouette = range_n_clusters[np.argmax(silhouette_scores)]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # === Apply KMeans Clustering with Optimal Number of Clusters ===
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        kmeans = KMeans(n_clusters=optimal_clusters_silhouette, random_state=42)
        kmeans_labels = kmeans.fit_predict(principal_components)
        pc_df['Cluster'] = kmeans_labels

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # === Plot Clusters in Scatter Plot ===
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ax = scatter_axes[i]
        palette = sns.color_palette('twilight_shifted', n_colors=optimal_clusters_silhouette)
        texts = []  # List to store annotation objects for adjustText
        x_coords = []  # Store x-coordinates of points for adjustText
        y_coords = []  # Store y-coordinates of points for adjustText
        handles = []
        labels_ = []

        for cluster in range(optimal_clusters_silhouette):

            # Get points belonging to this cluster
            cluster_points = pc_df[pc_df['Cluster'] == cluster]

            # Plot this cluster with its unique marker
            sc = ax.scatter(
                cluster_points['PC1'],
                cluster_points['PC2'],
                marker=marker_styles[cluster % len(marker_styles)],
                s=marker_size_pca,
                c=[palette[cluster % len(palette)]],
                edgecolor=edgecolor,
                linewidth=line_width_pca
            )
            # Collect handle and label for the legend only if not already added
            if f'Cluster {cluster + 1}' not in labels_:
                handles.append(sc)
                labels_.append(f'Cluster {cluster + 1}')

            # === Add the cluster information to the df ===
            # Get points belonging to this cluster
            cluster_points = pc_df[pc_df['Cluster'] == cluster].copy()

            # Add dataset label to cluster points
            cluster_points['Dataset'] = label  # New column for dataset label

            # Append to cluster list
            cluster_dfs.append(cluster_points)

            # Add text labels with manual offsets where specified
            for j, entry in enumerate(cluster_points['entry']):
                xi = cluster_points['PC1'].iloc[j]
                yi = cluster_points['PC2'].iloc[j]

                # Check if manual offset exists for this dataset label and entry
                if label in manual_offsets and entry in manual_offsets[label]:
                    dx, dy = manual_offsets[label][entry]  # Get offset from nested dict
                else:
                    dx, dy = 0, 0  # Default: no offset

                text = ax.text(
                    xi + dx, yi + dy,
                    str(entry),
                    fontsize=fontsize_big
                )
                texts.append(text)
                x_coords.append(xi)  # Original data point coordinates
                y_coords.append(yi)

        # === Use the CORRECT adjustText API with target coordinates ===
        adjust_text(
            texts,
            target_x=x_coords,  # Original data point coordinates for arrows
            target_y=y_coords,  # Original data point coordinates for arrows
            ax=ax,
            avoid_self=False,  # Don't repel from original positions
            force_text=0.1,  # Minimal text repulsion
            force_points=0.1,  # Minimal point repulsion
            arrowprops=dict(
                arrowstyle='-',
                color='gray',
                alpha=0.7,
                lw=1.2,
                shrinkA=2,  # Shrink from text edge (2 points)
                shrinkB=2  # Shrink from target point (2 points)
            )
        )

        # Only collect handles/labels from the first subplot (or the one with the max clusters)
        if i == 0 or len(labels_) > len(all_labels):
            all_handles = handles
            all_labels = labels_

        # Set subplot title and axis labels using predefined variables
        ax.set_title(label, fontsize=fontsize_big)
        ax.set_xlabel(f'PC1 ({explained_variance[0]:.2%} variance)', fontsize=fontsize_big, fontname=font_name)
        ax.set_ylabel(f'PC2 ({explained_variance[1]:.2%} variance)', fontsize=fontsize_big, fontname=font_name)
        ax.grid(True, linestyle=grid_linestyle, linewidth=grid_linewidth, alpha=grid_alpha)

    for i in range(nrows):
        for j in range(ncols):
            ax = scatter_axes[i * ncols + j]

            # Show x tick labels only on bottom row
            if i != nrows - 1:
                ax.tick_params(labelbottom=False)

            # Show y tick labels only on left column
            if j != 0:
                ax.tick_params(labelleft=False)

    # Adjust the space between plots
    plt.subplots_adjust(hspace=0.3, wspace=0.3)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # === Add a single legend below all subplots (with extra space) ===
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Place the legend further below to avoid overlap with x-axis labels
    scatter_axes[0].legend(
        handles=all_handles,
        labels=all_labels,
        loc='lower center',
        bbox_to_anchor=(1, -1.745),  # Lower y-value moves legend further down
        # ncol=(len(all_labels) + 1) // 2,  # ← Divide into two rows
        ncol=(len(all_labels) + 1),
        frameon=True,
        columnspacing=1.2,
        handletextpad=0.0,
        fontsize=fontsize_medium,
        prop=legend_font,  # Font for legend labels
        title_fontproperties=legend_title_font  # Font for legend title
    )

    ##############################################################################
    # ====== Final Figure Customization and Save ======
    ##############################################################################
    # ====== Add Main Panel Titles ======
    fig.text(0.10, 0.92, '(a)', fontsize=fontsize_title, fontname=font_name, weight='bold')
    fig.text(0.10, 0.47, '(c)', fontsize=fontsize_title, fontname=font_name, weight='bold')
    fig.text(0.43, 0.92, '(b)', fontsize=fontsize_title, fontname=font_name, weight='bold')

    # Save the plot
    plt.tight_layout()
    plt.savefig(final_figure_output, dpi=300, bbox_inches='tight')