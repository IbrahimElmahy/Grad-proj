from __future__ import annotations

import argparse
import csv
import shutil
import time
from datetime import datetime
from pathlib import Path


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def read_last_line(path: Path, limit: int = 1) -> list[str]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        return [line.rstrip("\n") for line in lines[-limit:]]
    except OSError:
        return []


def parse_last_metrics(results_csv: Path) -> dict[str, str] | None:
    if not results_csv.exists():
        return None
    try:
        with results_csv.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError:
        return None
    if not rows:
        return None
    row = rows[-1]
    return {
        "epoch": row.get("epoch", "").strip(),
        "precision": row.get("metrics/precision(B)", "").strip(),
        "recall": row.get("metrics/recall(B)", "").strip(),
        "map50": row.get("metrics/mAP50(B)", "").strip(),
        "map50_95": row.get("metrics/mAP50-95(B)", "").strip(),
    }


def is_finished(stdout_log: Path) -> bool:
    tail = "\n".join(read_last_line(stdout_log, limit=40))
    markers = (
        "100 epochs completed",
        "EarlyStopping",
        "Results saved to",
        "Validating",
    )
    return any(marker in tail for marker in markers) and "Starting training for" in stdout_log.read_text(
        encoding="utf-8", errors="ignore"
    )


def best_ready(run_dir: Path) -> bool:
    return (run_dir / "weights" / "best.pt").exists()


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor a YOLO training run and log status every N minutes.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--stdout-log", required=True)
    parser.add_argument("--stderr-log", required=True)
    parser.add_argument("--interval-minutes", type=int, default=15)
    parser.add_argument("--monitor-log", required=True)
    parser.add_argument("--copy-best-to", default="")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    stdout_log = Path(args.stdout_log).resolve()
    stderr_log = Path(args.stderr_log).resolve()
    monitor_log = Path(args.monitor_log).resolve()
    copy_best_to = Path(args.copy_best_to).resolve() if args.copy_best_to else None
    interval_seconds = max(args.interval_minutes, 1) * 60

    monitor_log.parent.mkdir(parents=True, exist_ok=True)

    with monitor_log.open("a", encoding="utf-8") as log:
        log.write(f"[{now()}] monitor started for {run_dir}\n")
        log.flush()

        while True:
            metrics = parse_last_metrics(run_dir / "results.csv")
            stderr_tail = read_last_line(stderr_log, limit=5)
            stdout_tail = read_last_line(stdout_log, limit=5)

            if metrics:
                log.write(
                    f"[{now()}] epoch={metrics['epoch']} precision={metrics['precision']} "
                    f"recall={metrics['recall']} map50={metrics['map50']} map50_95={metrics['map50_95']}\n"
                )
            else:
                log.write(f"[{now()}] waiting for first metrics row\n")

            if stdout_tail:
                log.write(f"[{now()}] stdout_tail: {' | '.join(stdout_tail)}\n")
            if stderr_tail:
                log.write(f"[{now()}] stderr_tail: {' | '.join(stderr_tail)}\n")
            log.flush()

            if best_ready(run_dir) and is_finished(stdout_log):
                best_path = run_dir / "weights" / "best.pt"
                log.write(f"[{now()}] training finished, best.pt detected at {best_path}\n")
                if copy_best_to:
                    copy_best_to.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(best_path, copy_best_to)
                    log.write(f"[{now()}] copied best.pt to {copy_best_to}\n")
                log.flush()
                return 0

            time.sleep(interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
