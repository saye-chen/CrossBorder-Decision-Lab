#!/usr/bin/env python3
"""Pull-forward, sibling SKU cannibalization and channel shift economics."""
from mbcm_common import finite, require, run_cli, sequence, text

def calculate(d):
    require(d,"expected_post_units","observed_post_units","baseline_cm_per_unit","siblings","channel_shifts","currency")
    pull=max(0,finite(d["expected_post_units"],"expected_post_units",0)-finite(d["observed_post_units"],"observed_post_units",0))
    pull_loss=pull*finite(d["baseline_cm_per_unit"],"baseline_cm_per_unit")
    cannibal=0.0
    for i,row in enumerate(sequence(d["siblings"],"siblings")):
        require(row,"counterfactual_units","observed_units","baseline_cm")
        lost=max(0,finite(row["counterfactual_units"],f"siblings[{i}].counterfactual_units",0)-finite(row["observed_units"],f"siblings[{i}].observed_units",0))
        cannibal+=lost*finite(row["baseline_cm"],f"siblings[{i}].baseline_cm")
    shift=0.0
    for i,row in enumerate(sequence(d["channel_shifts"],"channel_shifts")):
        require(row,"orders","new_channel_cm","original_channel_cm")
        shift+=finite(row["orders"],f"channel_shifts[{i}].orders",0)*(finite(row["new_channel_cm"],f"channel_shifts[{i}].new_channel_cm")-finite(row["original_channel_cm"],f"channel_shifts[{i}].original_channel_cm"))
    return {"currency":text(d["currency"],"currency"),"pull_forward_units":pull,"pull_forward_loss":pull_loss,
            "cannibalization_loss":cannibal,"channel_shift_value":shift,
            "total_adjustment":shift-pull_loss-cannibal}
if __name__=="__main__": run_cli(calculate,"pull_forward_cannibalization")
