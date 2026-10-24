"""
TITAN Platform API - Empirical Reliability Benchmark Analytics
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_platform_db, ExperimentModel

router = APIRouter(prefix="/api/v1/benchmarks", tags=["Reliability Benchmarks"])


class StrategyMetric(BaseModel):
    trials: int
    success_rate_pct: float
    mean_recovery_sec: float


class BenchmarkSummaryDTO(BaseModel):
    total_experiments: int
    successful_recoveries: int
    failed_recoveries: int
    recovery_success_rate_pct: float
    mean_time_to_detect_seconds: float
    mean_time_to_diagnose_seconds: float
    mean_time_to_recover_seconds: float
    strategy_breakdown: Dict[str, StrategyMetric]


@router.get("/summary", response_model=BenchmarkSummaryDTO)
def get_benchmark_summary(db: Session = Depends(get_platform_db)):
    experiments = db.scalars(select(ExperimentModel)).all()
    total = len(experiments)

    if total == 0:
        return BenchmarkSummaryDTO(
            total_experiments=0,
            successful_recoveries=0,
            failed_recoveries=0,
            recovery_success_rate_pct=0.0,
            mean_time_to_detect_seconds=0.0,
            mean_time_to_diagnose_seconds=0.0,
            mean_time_to_recover_seconds=0.0,
            strategy_breakdown={}
        )

    successful = [e for e in experiments if e.verified and e.status == "completed"]
    failed = [e for e in experiments if not e.verified or e.status == "failed"]

    mttd = sum(e.detection_time_sec for e in experiments) / total
    mtt_diag = sum(e.diagnosis_time_sec for e in experiments) / total
    mttr = sum(e.recovery_time_sec for e in successful) / len(successful) if successful else 0.0

    success_rate = round((len(successful) / total) * 100.0, 2)

    # Strategy breakdown
    strategies: Dict[str, list] = {}
    for exp in experiments:
        strategies.setdefault(exp.recovery_strategy_used, []).append(exp)

    strategy_breakdown = {}
    for strat, records in strategies.items():
        s_total = len(records)
        s_success = len([r for r in records if r.verified and r.status == "completed"])
        s_rate = round((s_success / s_total) * 100.0, 2)
        s_mttr = round(sum(r.recovery_time_sec for r in records if r.verified) / max(s_success, 1), 2)
        strategy_breakdown[strat] = StrategyMetric(
            trials=s_total,
            success_rate_pct=s_rate,
            mean_recovery_sec=s_mttr
        )

    return BenchmarkSummaryDTO(
        total_experiments=total,
        successful_recoveries=len(successful),
        failed_recoveries=len(failed),
        recovery_success_rate_pct=success_rate,
        mean_time_to_detect_seconds=round(mttd, 2),
        mean_time_to_diagnose_seconds=round(mtt_diag, 2),
        mean_time_to_recover_seconds=round(mttr, 2),
        strategy_breakdown=strategy_breakdown
    )
