from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from pyranges.core.names import CHROM_COL, END_COL, START_COL
from pyranges.core.pyranges_helpers import ensure_rangeframe

if TYPE_CHECKING:
    from pyranges.range_frame.range_frame import RangeFrame


def _complement(
    df: "RangeFrame",
    *,
    by: list[str],
    slack: int = 0,
    chromsizes_col: str | None = None,
    chromsizes: "dict[str | int, int] | None" = None,
    include_first_interval: bool = False,
) -> "RangeFrame":
    import ruranges

    from pyranges.range_frame.range_frame import RangeFrame

    if df.empty:
        return df

    col_order = [col for col in df if col in [*by, START_COL, END_COL]]

    factorized = pd.Series(np.zeros(len(df), dtype=np.uint32)) if not by else df.groupby(by).ngroup().astype(np.uint32)
    # The Rust kernel must see the *same* dtype that we pass for starts/ends
    pos_dtype: np.dtype[Any] = df[START_COL].to_numpy(copy=False).dtype
    grp_dtype: np.dtype[Any] = factorized.to_numpy(copy=False).dtype

    if chromsizes and chromsizes_col:
        group_to_len = (
            pd.DataFrame(
                {
                    "group_id": factorized,
                    "length": df[chromsizes_col].replace(chromsizes),
                }
            )
        ).drop_duplicates()
        chrom_len_ids = group_to_len["group_id"].to_numpy(grp_dtype)
        chrom_lens = group_to_len["length"].to_numpy(pos_dtype)
    else:
        chrom_len_ids = np.array([], dtype=grp_dtype)
        chrom_lens = np.array([], dtype=pos_dtype)

    chrs, start, end, idxs = ruranges.complement(
        groups=factorized.to_numpy(),
        starts=df.Start.to_numpy(),
        ends=df.End.to_numpy(),
        slack=slack,
        chrom_len_ids=chrom_len_ids,  # type: ignore[arg-type]
        chrom_lens=chrom_lens,
        include_first_interval=include_first_interval,
    )

    ids = df.take(idxs)  # type: ignore[arg-type]

    result = RangeFrame({CHROM_COL: chrs, START_COL: start, END_COL: end} | {_by: ids[_by] for _by in by})[col_order]

    return ensure_rangeframe(result.reset_index(drop=True))
