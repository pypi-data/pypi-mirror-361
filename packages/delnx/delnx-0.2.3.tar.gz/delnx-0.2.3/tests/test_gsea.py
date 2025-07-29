import pandas as pd

from delnx.pp import label_de_genes
from delnx.tl import de_enrichment_analysis


def test_de_enrichment_analysis_output(de_results, gene_sets):
    """Test that de_enrichment_analysis returns expected columns."""

    # Label DE genes
    label_de_genes(de_results, coef_thresh=0.5)

    # Run enrichment analysis
    enr_results = de_enrichment_analysis(de_results, gene_sets=gene_sets, cutoff=0.1)

    # Check that the result is a non-empty DataFrame with expected columns
    assert isinstance(enr_results, pd.DataFrame), "Output should be a pandas DataFrame"
