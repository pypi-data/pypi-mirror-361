import itertools
from dataclasses import dataclass, field

import anndata as ad
import marsilea as ma
import marsilea.plotter as mp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ._palettes import default_palette


@dataclass
class BasePlot:
    """
    Base class for plotting annotated data matrices with AnnData and Marsilea.

    This class provides a flexible interface for generating annotated heatmaps and related
    visualizations from single-cell or other high-dimensional data stored in AnnData objects.
    It supports grouping, annotation, and customization of plot appearance, and is designed
    to be extended for specific plot types.

    Parameters
    ----------
    adata : ad.AnnData
        Annotated data matrix (AnnData object) containing observations and variables.
    markers : list[str]
        List of marker gene names (variables) to include in the plot.
    groupby_keys : str or list[str]
        Key(s) in `adata.obs` used to group samples (e.g., cell types, clusters).
        If a string is provided, it is converted to a list internally.
    layer : str or None, optional
        If specified, use this layer from `adata` instead of the default `.X` matrix
    scale: bool, default=True
        Whether to scale gene expression values before plotting.
    row_grouping : str, list[str], pd.Series, pd.Categorical, or None, default="auto"
        How to group rows in the heatmap. Can be:
        - "auto": Use the group labels defined by `groupby_keys`.
        - str: Name of a column in `adata.obs` to use for grouping.
        - list[str]: List of column names in `adata.obs` to combine for grouping.
        - pd.Series or pd.Categorical: Custom grouping vector.
        - None: No row grouping.
    cmap : str, default="viridis"
        Colormap to use for the heatmap.
    height : float, default=3.5
        Height of the plot in inches.
    width : float, default=3
        Width of the plot in inches.
    scale_render : float, default=1.0
        Scale factor for the plot size.
    show_column_names : bool, default=True
        Whether to display column (gene) names on the plot.
    show_row_names : bool, default=True
        Whether to display row (group) names on the plot.
    show_legends : bool, default=True
        Whether to display legends for groupings and colorbars.
    groupbar_size : float, default=0.1
        Size of the group color bar relative to the plot.
    groupbar_pad : float, default=0.05
        Padding between the group color bar and the heatmap.
    chunk_rotation : int, default=0
        Rotation angle (in degrees) for chunk (group) labels.
    chunk_align : str, default="center"
        Alignment for chunk (group) labels.
    chunk_pad : float, default=0.1
        Padding for chunk (group) labels.
    chunk_fontsize : int, default=10
        Font size for chunk (group) labels.
    dendrograms : list[str] or None, default=None
        List of dendrogram positions to add to the plot (e.g., ["top", "left"]).
    """

    adata: ad.AnnData
    markers: list[str]
    groupby_keys: str | list[str]

    # Layer to use for the data matrix
    # If None, uses the default `.X` matrix from `adata`
    layer: str | None = None

    # Whether to scale the data before plotting
    scale: bool = True

    # Row grouping options
    row_grouping: str | list[str] | pd.Series | pd.Categorical | None = "auto"

    # Column grouping options
    column_grouping: bool = False

    # Plotting parameters for heatmap
    cmap: str = "viridis"

    # Layout and appearance parameters
    height: float = 3.5
    width: float = 3
    scale_render: float = 1.0

    # Annotations and labels
    show_column_names: bool = True
    show_row_names: bool = True
    show_legends: bool = True

    # Grouping and annotation parameters
    groupbar_size: float = 0.1
    groupbar_pad: float = 0.05
    chunk_rotation: int = 0
    chunk_align: str = "center"
    chunk_pad: float = 0.1
    chunk_fontsize: int = 10

    # Dendrograms
    dendrograms: list[str] | None = None

    # Group names for annotations
    group_names: str | list[str] | None = None
    group_labels: pd.Categorical = field(init=False)

    def __post_init__(self):
        """Initialize group labels and add them to adata.obs as '_group'."""
        # Make category dtype for groupby_keys if not already categorical
        if isinstance(self.groupby_keys, str):
            if self.groupby_keys not in self.adata.obs.columns:
                raise ValueError(f"Key '{self.groupby_keys}' not found in adata.obs.")
            if not pd.api.types.is_categorical_dtype(self.adata.obs[self.groupby_keys]):
                self.adata.obs[self.groupby_keys] = self.adata.obs[self.groupby_keys].astype("category")
        elif isinstance(self.groupby_keys, list):
            for key in self.groupby_keys:
                if key not in self.adata.obs.columns:
                    raise ValueError(f"Key '{key}' not found in adata.obs.")
                if not pd.api.types.is_categorical_dtype(self.adata.obs[key]):
                    self.adata.obs[key] = self.adata.obs[key].astype("category")

        if isinstance(self.groupby_keys, str):
            self.groupby_keys = [self.groupby_keys]

        # If group_names is not provided, use groupby_keys as default
        if self.group_names is None:
            self.group_names = self.groupby_keys
        else:
            if isinstance(self.group_names, str):
                self.group_names = [self.group_names]

        # Create _group labels
        group_labels = self.adata.obs[self.groupby_keys].astype(str).agg("_".join, axis=1)

        # Build all possible combinations from category levels in order
        category_levels = [self.adata.obs[k].cat.categories for k in self.groupby_keys]
        ordered_combinations = ["_".join(tup) for tup in itertools.product(*category_levels)]

        # Create ordered categorical
        self.group_labels = pd.Categorical(group_labels, categories=ordered_combinations, ordered=True)
        self.adata.obs["_group"] = self.group_labels

    def _resolve_row_grouping(self, index_source=None) -> tuple[pd.Categorical | None, pd.Index | None]:
        """
        Resolve row grouping for the heatmap.

        Parameters
        ----------
        index_source : pd.Index or None, optional
            If provided, the grouping will be based on this index. If None, uses the full
            group labels from `adata.obs`.

        Returns
        -------
        tuple[pd.Categorical | None, pd.Index | None]
            A tuple containing:
            - pd.Categorical or None: The resolved row grouping.
            - pd.Index or None: The categories of the grouping.
        """
        if self.row_grouping == "auto":
            group = index_source if index_source is not None else self.group_labels
            return group, getattr(group, "categories", list(group))
        elif self.row_grouping is None:
            return None, None
        elif isinstance(self.row_grouping, str):
            group = (
                self.adata.obs[self.row_grouping].loc[index_source]
                if index_source is not None
                else self.adata.obs[self.row_grouping]
            )
            group = pd.Categorical(group)
            return group, group.categories
        elif isinstance(self.row_grouping, list):
            group = self.adata.obs[self.row_grouping].astype(str).agg("_".join, axis=1)
            group = group.loc[index_source] if index_source is not None else group
            group = pd.Categorical(group)
            return group, group.categories
        elif isinstance(self.row_grouping, pd.Series | pd.Categorical):
            group = (
                self.row_grouping.loc[index_source] if isinstance(self.row_grouping, pd.Series) else self.row_grouping
            )
            group = pd.Categorical(group)
            return group, group.categories
        else:
            raise ValueError("Invalid value for row_grouping")

    def _build_data(self) -> np.ndarray:
        """Extracts the data matrix for the selected markers from .X or a specified layer."""
        # Flatten markers if given as a dict
        if isinstance(self.markers, dict):
            flat_markers = list(itertools.chain.from_iterable(self.markers.values()))
        else:
            flat_markers = self.markers

        # Extract matrix from specified layer if provided
        if getattr(self, "layer", None):
            if self.layer not in self.adata.layers:
                raise ValueError(f"Layer '{self.layer}' not found in adata.layers.")
            mat = self.adata[:, flat_markers].layers[self.layer]
        else:
            mat = self.adata[:, flat_markers].X

        # Convert to dense array if sparse
        if hasattr(mat, "toarray"):
            mat = mat.toarray()

        return mat

    def _add_row_labels(self, m: ma.Heatmap):
        """
        Add row labels to the heatmap

        - If self.order is defined, use `Chunk` to show grouped labels.
        - If self.order is None, use `Labels` to show individual row names.

        Parameters
        ----------
        m : ma.Heatmap
            The heatmap object to which row labels will be added.
        """
        if self.row_group is not None:
            # Create chunked row labels using the order
            chunk = mp.Chunk(
                self.order,
                rotation=self.chunk_rotation,
                align=self.chunk_align,
                fontsize=self.chunk_fontsize,
            )
            m.group_rows(self.row_group, order=self.order)
            m.add_left(chunk)
        else:
            # Use index from the data matrix as row labels
            labels = mp.Labels(
                list(self.mean_df.index),  # or m.data.index
                rotation=self.chunk_rotation,
                align=self.chunk_align,
                fontsize=self.chunk_fontsize,
            )
            m.add_left(labels, pad=self.chunk_pad)

    def _add_column_labels(self, m: ma.Heatmap):
        """
        Add column labels to the heatmap.

        - If `self.markers` is a dict, create grouped chunks using keys as categories.
        - Otherwise, show all markers using `mp.Labels`.

        Parameters
        ----------
        m : ma.Heatmap
            The heatmap object to which column labels will be added.
        """
        if isinstance(self.markers, dict):
            # Build matching group labels for each column
            chunk_labels = list(itertools.chain.from_iterable([key] * len(vals) for key, vals in self.markers.items()))

            # Create Categorical with explicit order
            group_labels = pd.Categorical(chunk_labels, categories=list(self.markers.keys()), ordered=True)

            # Apply column grouping
            m.group_cols(group_labels, order=list(self.markers.keys()))

            # Add chunked column annotations
            chunk = mp.Chunk(
                list(self.markers.keys()),
                rotation=90,
                align=self.chunk_align,
                fontsize=self.chunk_fontsize,
            )

            m.add_top(chunk)
        else:
            # Simple unchunked label case
            labels = mp.Labels(self.markers, fontsize=self.chunk_fontsize)
            m.add_top(labels, pad=self.chunk_pad)

    def _add_annotations(self, m: ma.Heatmap):
        """
        Add group colorbars and labels to the heatmap.

        Parameters
        ----------
        m : ma.Heatmap
            The heatmap object to which annotations will be added.
        """
        # Add an annotation colorbar for each group key
        for key in reversed(self.groupby_keys):
            self._add_group_colorbar(m, key)
        # Add column and gene labels if specified
        if self.show_column_names:
            self._add_column_labels(m)
        if self.show_row_names:
            self._add_row_labels(m)

    def _add_group_colorbar(self, m: ma.Heatmap, key: str):
        """
        Add a colorbar for a specific group key.

        Parameters
        ----------
        m : ma.Heatmap
            The heatmap object to which the colorbar will be added.
        key : str
            The key in `adata.obs` for which to add the colorbar.

        Raises
        ------
        ValueError
            If the key is not found in `adata.obs`.
        """
        # Check if the key exists in adata.obs
        if key not in self.adata.obs:
            raise ValueError(f"Key '{key}' not found in adata.obs. Available keys: {self.adata.obs.columns.tolist()}")
        # Extract values and palette for the group key
        values = self.adata.obs[key]
        palette = self.adata.uns.get(f"{key}_colors")
        # If no palette is found, use a default palette
        if palette is None:
            categories = values.cat.categories
            palette = dict(zip(categories, default_palette(len(categories)), strict=False))
        # Create and add the colorbar
        label = self.group_names[self.groupby_keys.index(key)]
        colorbar = mp.Colors(list(values), palette=palette, label=label)
        m.add_left(colorbar, size=self.groupbar_size, pad=self.groupbar_pad)

    def _add_extras(self, m):
        """
        Add additional features to the heatmap.

        Parameters
        ----------
        m : ma.Heatmap
            The heatmap object to which extras will be added.
        """
        # Add categorical annotations
        self._add_annotations(m)
        # Add dendrograms if specified
        if self.dendrograms:
            for pos in self.dendrograms:
                m.add_dendrogram(pos, add_base=False)
        # Add legends if specified
        if self.show_legends:
            m.add_legends()
        return m

    def _scale_data(self, data: np.ndarray) -> np.ndarray:
        """
        Scale the data matrix if scaling is enabled.

        Parameters
        ----------
        data : np.ndarray
            The data matrix to scale.

        Returns
        -------
        np.ndarray
            The scaled data matrix.
        """
        if self.scale:
            # Scale the data to [0, 1] range
            data_min = np.min(data, axis=0)
            data_max = np.max(data, axis=0)
            data = (data - data_min) / (data_max - data_min)
        return data

    def _build_plot(self):
        """Build the base heatmap plot."""
        # Build the data matrix for the heatmap
        data = self._build_data()

        # Scale the data if scaling is enabled
        data = self._scale_data(data)

        # Create heatmap
        m = ma.Heatmap(
            data,
            cmap=self.cmap,
            height=self.height,
            width=self.width,
            cbar_kws={"title": "Expression\nin group"},
        )
        # Extract grouping information
        self.row_group, self.order = self._resolve_row_grouping()
        if self.row_group is not None:
            m.group_rows(self.row_group, order=self.order)
        # Add extras to the heatmap
        m = self._add_extras(m)
        return m

    def show(self):
        """Display the plot using matplotlib's interactive mode."""
        # Build the plot
        m = self._build_plot()
        # Render the plot
        with plt.rc_context(rc={"axes.grid": False, "grid.color": ".8"}):
            m.render(scale=self.scale_render)

    def save(self, filename: str, **kwargs):
        """
        Save the plot to a file.

        Parameters
        ----------
        filename : str
            The path to save the plot.
        **kwargs
            Additional keyword arguments passed to the save method.
        """
        # Build the plot
        m = self._build_plot()
        # Render the plot
        with plt.rc_context(rc={"axes.grid": False, "grid.color": ".8"}):
            m.save(filename, **kwargs)
