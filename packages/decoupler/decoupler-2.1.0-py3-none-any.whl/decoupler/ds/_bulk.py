from anndata import AnnData

from decoupler._docs import docs
from decoupler._download import _bytes_to_pandas, _download
from decoupler._log import _log


@docs.dedent
def hsctgfb(
    verbose: bool = False,
) -> AnnData:
    """
    Hepatic stellate cells (HSC).

    Downloads RNA-seq bulk data consisting of 6 samples of hepatic stellate cells
    (HSC) where three of them were activated by the cytokine
    Transforming growth factor (TGF-β) :cite:`hsc_tgfb`.

    Parameters
    ----------
    %(verbose)s

    Returns
    -------
    AnnData object.

    Example
    -------
    .. code-block:: python

        import decoupler as dc

        adata = dc.ds.hsctgfb()
        adata
    """
    # Download
    url = (
        "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE151251&format=file&"
        "file=GSE151251%5FHSCs%5FCtrl%2Evs%2EHSCs%5FTGFb%2Ecounts%2Etsv%2Egz"
    )
    adata = _download(url, verbose=verbose)
    adata = _bytes_to_pandas(adata, compression="gzip", sep="\t")
    # Transform to AnnData
    adata = adata.drop_duplicates("GeneName").set_index("GeneName").iloc[:, 5:].T
    adata.columns.name = None
    adata = AnnData(adata)
    adata.X = adata.X.astype(float)
    # Format obs
    adata.obs["condition"] = ["control" if "-Ctrl" in sample_id else "treatment" for sample_id in adata.obs.index]
    adata.obs["sample_id"] = [sample_id.split("_")[0] for sample_id in adata.obs.index]
    adata.obs["condition"] = adata.obs["condition"].astype("category")
    adata.obs["sample_id"] = adata.obs["sample_id"].astype("category")
    m = f"generated AnnData with shape={adata.shape}"
    _log(m, level="info", verbose=verbose)
    return adata


@docs.dedent
def knocktf(
    thr_fc: int | float | None = -1,
    verbose: bool = False,
) -> AnnData:
    """
    KnockTF perturbation database.

    Downloads gene contrast statistics from KnockTF :cite:`knocktf`,
    a large collection of transcription factor (TF) RNA-seq
    perturbation experiments.

    The values in ``adata.X`` represent the log2FCs of genes between
    perturbed and unperturbed samples.

    It also downloads all metadata associated to each perturbation
    experiment, such as which TF was perturbed, or in which tissue.

    Parameters
    ----------
    %(verbose)s

    Returns
    -------
    AnnData object.

    Example
    -------
    .. code-block:: python

        import decoupler as dc

        adata = dc.ds.knocktf()
        adata
    """
    assert isinstance(thr_fc, int | float) or thr_fc is None, "thr_fc must be numeric or None"
    # Download
    url = "https://zenodo.org/record/7035528/files/knockTF_expr.csv?download=1"
    adata = _download(url, verbose=verbose)
    adata = _bytes_to_pandas(adata, sep=",", index_col=0)
    url = "https://zenodo.org/record/7035528/files/knockTF_meta.csv?download=1"
    obs = _download(url, verbose=verbose)
    obs = _bytes_to_pandas(obs, sep=",", index_col=0)
    obs = obs.rename(columns={"TF": "source"}).assign(type_p=-1)
    # Make anndata
    adata = AnnData(X=adata, obs=obs)
    # Filter by thr_fc
    if thr_fc is not None:
        msk = adata.obs["logFC"] < thr_fc
        prc_keep = (msk.sum() / msk.size) * 100
        m = f"filtering AnnData for thr_fc={thr_fc}, will keep {prc_keep:.2f}% of observations"
        _log(m, level="info", verbose=verbose)
        adata = adata[msk, :].copy()
    m = f"generated AnnData with shape={adata.shape}"
    _log(m, level="info", verbose=verbose)
    return adata
