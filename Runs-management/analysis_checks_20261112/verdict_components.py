"""Split the registered interval verdict into its separate conditions.

The 11/11 assessment asks that "CI lower bound > 0 and point estimate >= delta" (registered 'benefit')
be reported separately from the stricter "CI lower bound >= delta". This script reads the PA1
`contrasts.csv` without modifying it and writes `contrasts_verdict_components.csv` with:

  ci_excludes_0        : lower bound > 0 or upper bound < 0
  point_ge_margin      : delta >= margin
  lb_gt_0              : lower bound > 0
  lb_ge_margin         : lower bound >= margin (benefit established beyond the margin)
  ub_lt_margin         : upper bound < margin (benefit of size margin excluded; NOT equivalence)
  ub_lt_0              : upper bound < 0 (harm)
  registered_verdict   : copied from interval_verdict

Usage: python verdict_components.py --contrasts <contrasts.csv> --out <csv>
"""

import argparse
import csv
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--contrasts", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with open(args.contrasts, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    keep = ["dataset", "partition", "arm_a", "arm_b", "comparison_role", "metric", "threshold_policy",
            "delta", "ci95_lo", "ci95_hi", "margin"]
    out = []
    for r in rows:
        d, lo, hi, m = (float(r[k]) for k in ("delta", "ci95_lo", "ci95_hi", "margin"))
        out.append({**{k: r[k] for k in keep},
                    "ci_excludes_0": lo > 0 or hi < 0,
                    "point_ge_margin": d >= m,
                    "lb_gt_0": lo > 0,
                    "lb_ge_margin": lo >= m,
                    "ub_lt_margin": hi < m,
                    "ub_lt_0": hi < 0,
                    "registered_verdict": r["interval_verdict"]})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)
    benefit = [r for r in out if r["registered_verdict"] == "benefit"]
    print(f"{len(out)} rows; registered 'benefit': {len(benefit)}; of which lb >= margin: "
          f"{sum(r['lb_ge_margin'] for r in benefit)}")
    for r in benefit:
        print(" ", r["dataset"], r["partition"], f"{r['arm_a']}->{r['arm_b']}", r["metric"], r["threshold_policy"],
              f"delta={float(r['delta']):+.4f} [{float(r['ci95_lo']):+.4f}; {float(r['ci95_hi']):+.4f}] "
              f"margin={r['margin']} lb>=margin={r['lb_ge_margin']}")


if __name__ == "__main__":
    main()
