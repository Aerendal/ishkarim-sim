"""
extracted.py — kod wyekstrahowany z WORK.md dla obszaru sim.

Zawiera 65 fragmentów kodu. Każdy fragment poprzedzony komentarzem
z nazwą katalogu-źródła.
"""
from __future__ import annotations



# ────────────────────────────────────────────────────────────# Source: AMBER  - CPU-only scaffold dla ABM
class RunConfig(BaseModel):
    model: str = "demo_valuewalk"
    steps: PositiveInt = 100
    agents: PositiveInt = 10
    seed: int = 12345                        # uint32
    activation: Literal["fixed_order","shuffled","batch"] = "fixed_order"
    record_level: Literal["none","aggregate","agent_trace"] = "aggregate"
    record_every: PositiveInt = 1
    deterministic_run_id: bool = True
    run_id: Optional[str] = None

# Source: AMBER  - CPU-only scaffold dla ABM
@dataclass(frozen=True)
class AmberPolicy:
    steps: int
    seed: int
    activation: str        # "fixed_order" | "shuffled" | "batch"
    show_progress: bool = False

class AmberCompatRunner:
    def __init__(self, model_factory: Callable[[dict], Any]): ...
    def run(self, parameters: dict, pol: AmberPolicy) -> dict:
        # → {"info": dict, "agents": pl.DataFrame, "model": pl.DataFrame}
        # agents ma: t_amber (Int64), step_norm = t_amber - 1 (Int64)
        # model ma: t_amber (Int64), step_norm = t_amber - 1 (Int64)

# Source: AMBER  - CPU-only scaffold dla ABM
@dataclass(frozen=True)
class NormalizePolicy:
    run_id: str
    record_level: str                    # "none" | "aggregate" | "agent_trace"
    trace_fields: Sequence[str] = ()
    step_col_candidates: Sequence[str] = ("step", "t")

def normalize_results(
    results: dict,
    pol: NormalizePolicy
) -> tuple[pl.DataFrame, pl.DataFrame, Optional[pl.DataFrame]]:
    # → (state_agents, metrics_step, trace_agents)

# Source: AMBER  - CPU-only scaffold dla ABM
@dataclass(frozen=True)
class FloatPolicy:
    mode: str = "exact"      # "exact" | "canonical" | "approx"
    abs_epsilon: float = 0.0
    rel_epsilon: float = 0.0
    decimals: Optional[int] = None

@dataclass(frozen=True)
class EquivSpec:
    table_name: str
    sort_keys: tuple[str, ...]
    float_policy: FloatPolicy = FloatPolicy()
    drop_schema_metadata: bool = True
    column_order: str = "sorted"    # "sorted" | "as_is"

def data_hash_polars(df: pl.DataFrame, spec: EquivSpec, batch_rows: int = 250_000) -> dict:
    # → {"table", "rows", "cols", "schema_hash", "data_hash", "float_policy", "sort_keys", "column_order"}
    # Algorytm: df.sort() → df.select(sorted_cols) → df.to_arrow() →
    #           cast(remove_metadata) → apply_float_policy → IPC stream → SHA-256

# Source: AMBER  - CPU-only scaffold dla ABM
SPECS = {
    "metrics_step":    EquivSpec("metrics_step",    ("step_norm", "metric")),
    "state_agents":    EquivSpec("state_agents",    ("id",)),
    "trace_agents":    EquivSpec("trace_agents",    ("step_norm", "id", "field")),
    "determinism_probe": EquivSpec("determinism_probe", ("step_norm",)),
}

# Source: AMBER  - CPU-only scaffold dla ABM
class TraceChunkWriter:
    schema = {"run_id": pl.Utf8, "step_norm": pl.Int64, "id": pl.Int64,
              "field": pl.Utf8, "value_f64": pl.Float64, "value_str": pl.Utf8}
    
    def __init__(self, run_dir: Path, max_rows_in_buffer: int = 5_000_000,
                 row_group_size: int = 262_144): ...
    def append(self, df: pl.DataFrame) -> None: ...   # auto-flush gdy buffer ≥ max_rows
    def flush(self) -> None: ...                       # zapisuje part-XXXXXX.parquet
    def close(self) -> Path: ...                       # zapisuje trace_index.json

# Odczyt lazy (bez OOM):
lf = pl.scan_parquet("runs/<run_id>/data/trace/trace_agents_part-*.parquet")

# Source: AMBER  - CPU-only scaffold dla ABM
@dataclass(frozen=True)
class ResourceLimits:
    cpu_core_fraction: float = 0.70
    polars_max_threads: Optional[int] = None
    blass_threads: int = 1
    ram_fraction: float = 0.50
    rss_soft_bytes: Optional[int] = None
    rss_hard_bytes: Optional[int] = None
    set_rlimit_as: bool = False
    check_interval_s: float = 0.5

class ResourceGovernor:
    def setup_limits(self) -> dict: ...      # ustawia progi, opcjonalnie RLIMIT_AS
    def check(self, now: float = None) -> ResourceState: ...  # RSS monitoring

class ResourceViolation(RuntimeError): pass

# Source: AMBER  - CPU-only scaffold dla ABM
# Backend sysfs (preferowany fallback):
class PowercapSysfsBackend:
    def available(self) -> bool: ...    # sprawdza /sys/class/powercap/intel-rapl:*
    def sample(self) -> EnergySample: ...  # {"pkg": uj, "core": uj, "dram": uj}

def delta_energy(prev, cur, max_ranges_uj) -> tuple[float, dict]:
    # obsługuje rollover: de[k] = (max_range - e1) + e2 gdy e2 < e1

# Miernik fazowy:
class PhaseEnergyMeterSysfs:
    def measure(self, phase: str) -> ContextManager: ...
    # on exit → self.result = PhaseEnergy(phase, duration_s, domains_uj)

# Source: Ceny dualne jako kompas w symulacjach
import sqlite3
import numpy as np
from datetime import datetime
from scipy.optimize import linprog

def solve_and_store(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    resources = cur.execute('SELECT id, limit_value FROM resources ORDER BY id').fetchall()
    jobs      = cur.execute('SELECT id, value FROM jobs ORDER BY id').fetchall()
    res_ids  = [r['id'] for r in resources]
    b        = np.array([r['limit_value'] for r in resources], dtype=float)
    job_ids  = [j['id'] for j in jobs]
    c_max    = np.array([j['value'] for j in jobs], dtype=float)
    m, n     = len(resources), len(jobs)

    A = np.zeros((m, n), dtype=float)
    res_index = {rid: i for i, rid in enumerate(res_ids)}
    job_index = {jid: j for j, jid in enumerate(job_ids)}
    for row in cur.execute('SELECT job_id, resource_id, consumption FROM job_resource'):
        A[res_index[row['resource_id']], job_index[row['job_id']]] = float(row['consumption'])

    c_min  = -c_max  # MAX(c^T x) -> MIN(-c^T x)
    bounds = [(0, None)] * n
    res    = linprog(c_min, A_ub=A, b_ub=b, bounds=bounds, method='highs')

    ts     = datetime.utcnow().isoformat(timespec='seconds')
    status = 'OPTIMAL' if res.success else f'FAILED: {res.message}'
    obj    = float(-res.fun) if res.success else None
    cur.execute('INSERT OR REPLACE INTO snapshots VALUES (?,?,?)', (ts, obj, status))

    if not res.success:
        conn.commit(); conn.close(); return

    x     = res.x.astype(float)
    slack = (b - A @ x)

    # UWAGA: SciPy/HiGHS marginals: dla MAX rozw. jako MIN(-c): shadow = -marginals
    marg        = np.array(res.ineqlin.marginals, dtype=float)
    shadow_raw  = -marg

    # Normalizacja robust: percentyl 90
    clipped     = np.maximum(shadow_raw, 0.0)
    denom       = np.percentile(clipped, 90) if np.any(clipped > 0) else 1.0
    shadow_norm = np.clip(clipped / (denom + 1e-12), 0.0, 1.0)

    TOL = 1e-9
    cur.executemany(
        'INSERT OR REPLACE INTO job_solution(ts, job_id, x_value) VALUES (?,?,?)',
        [(ts, jid, float(x[job_index[jid]])) for jid in job_ids]
    )
    cur.executemany(
        'INSERT OR REPLACE INTO shadow_prices(ts, resource_id, price_raw, price_norm, slack, binding) VALUES (?,?,?,?,?,?)',
        [(ts, rid, float(shadow_raw[i]), float(shadow_norm[i]), float(slack[i]), int(abs(slack[i]) <= TOL))
         for i, rid in enumerate(res_ids)]
    )
    conn.commit(); conn.close()

# Source: Ceny dualne jako kompas w symulacjach
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Variable:
    var_id:   str
    lower:    Optional[float] = 0.0
    upper:    Optional[float] = None
    var_type: str = 'CONTINUOUS'   # CONTINUOUS | INTEGER | BINARY

@dataclass
class Constraint:
    constraint_id: str
    a:     List[float]   # wektor wsp. (len = n_vars)
    sense: str           # LE | GE | EQ
    rhs:   float
    name:  str = ''
    unit:  str = ''

@dataclass
class Model:
    objective_sense: str           # MAX | MIN
    c:           List[float]
    constraints: List[Constraint]
    variables:   List[Variable]

@dataclass
class FDCheck:
    constraint_id: str
    delta:        float
    obj0:         float
    obj1:         float
    approx:       float
    shadow_used:  float
    rel_err:      float

@dataclass
class SnapshotResult:
    ts:              str
    solver_name:     str
    objective_sense: str
    objective_value: Optional[float]
    status:          str
    mip_mode:        str
    sign_rule:       str
    validation_ok:   bool
    x:               Dict[str, float]
    constraint_rows: Dict[str, dict]   # {cid: {slack, shadow_raw}}
    fd_checks:       list

# Source: Ceny dualne jako kompas w symulacjach
import numpy as np

def canonicalize(model):
    ''
    Sprowadza constrainty do postaci SciPy (A_ub x <= b_ub, A_eq x = b_eq).
    cmap[constraint_id] = {type: UB|EQ, rows: [...], flip_sign: +1|-1}
    ''
    n = len(model.variables)
    ub_rows, ub_rhs, eq_rows, eq_rhs = [], [], [], []
    cmap = {}
    ui = ei = 0
    for con in model.constraints:
        a = list(con.a)
        if con.sense == 'LE':
            ub_rows.append(a); ub_rhs.append(con.rhs)
            cmap[con.constraint_id] = {'type':'UB','rows':[ui],'flip_sign':1}
            ui += 1
        elif con.sense == 'GE':
            ub_rows.append([-x for x in a]); ub_rhs.append(-con.rhs)
            cmap[con.constraint_id] = {'type':'UB','rows':[ui],'flip_sign':-1}
            ui += 1
        elif con.sense == 'EQ':
            eq_rows.append(a); eq_rhs.append(con.rhs)
            cmap[con.constraint_id] = {'type':'EQ','rows':[ei],'flip_sign':1}
            ei += 1
    A_ub = np.array(ub_rows) if ub_rows else np.zeros((0, n))
    b_ub = np.array(ub_rhs)  if ub_rhs  else np.zeros(0)
    A_eq = np.array(eq_rows) if eq_rows else np.zeros((0, n))
    b_eq = np.array(eq_rhs)  if eq_rhs  else np.zeros(0)
    return A_ub, b_ub, A_eq, b_eq, cmap

# Source: Ceny dualne jako kompas w symulacjach
# Dla każdego joba j: koszt zasobów wg cen dualnych
cost_j = sum(y_i * a_ij for i, y_i in enumerate(shadow_prices))
# Score (bang per buck):
score_j = value_j / (1e-9 + cost_j)
# Sortuj kolejkę malejąco po score_j
queue.sort(key=lambda j: -score_j[j.id])

# Source: Differentiable simulators & hybrids
class Simulator(Protocol):
    def forward(self, state, params) -> Any: ...
    def info(self) -> SimulatorInfo: ...

class Objective(Protocol):
    def __call__(self, state, target) -> torch.Tensor: ...

class HybridModel(Protocol):
    def forward(self, state, params, t) -> Any: ...

# Source: Differentiable simulators & hybrids
class LinearEulerStepFn(torch.autograd.Function):
    """x_next = x + dt*(A@x + B@u) — custom backward dla kontroli pamięci"""
    @staticmethod
    def forward(ctx, x, A, B, u, dt): ...
    @staticmethod
    def backward(ctx, grad_output): ...

# Source: Differentiable simulators & hybrids
class ImplicitSolveFn(torch.autograd.Function):
    """VJP przez A(θ)x(θ) = b(θ): dx/dθ = -A^{-1}(dA/dθ * x - db/dθ)"""
    @staticmethod
    def forward(ctx, b, A_fn, AT_fn, M, cfg): ...  # solve Ax=b
    @staticmethod
    def backward(ctx, grad_x): ...  # solve A^T v = grad_x; grad_b = v

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
from dataclasses import dataclass
from typing import Dict, Callable, Iterable, Tuple, Optional

@dataclass
class KernelConfig:
    step: float = 0.1           # rozmiar kroku czasowego
    reversible: bool = True     # True = zachowanie masy
    clamp: Optional[Tuple[float, float]] = None  # np. (0.0, 1.0)
    seed: int = 0

class Graph:
    def nodes(self) -> Iterable[str]: ...
    def neighbors(self, i: str) -> Iterable[Tuple[str, float]]: ...  # (sasiad, waga)

class DiffusionKernel:
    def __init__(self, graph: Graph, flux_fn: Callable, cfg: KernelConfig): ...
    def step_update(self, x: Dict[str, float]) -> Dict[str, float]: ...
    # Akumuluje flux po wszystkich sasiadach; jesli reversible, odejmuje od j

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

@dataclass
class GridKernelConfig:
    step: float = 0.1
    k: float = 1.0
    clamp: Optional[Tuple[float, float]] = None
    boundary: str = 'wrap'   # 'wrap' | 'reflect' | 'clamp' | 'zero_flux'
    stencil: str = '4'       # '4' (2D, 4-neigh) | '8' (2D, 8-neigh) | '6' (3D) | '26' (3D)

def grid_step_softbody(
    x: np.ndarray,          # (H,W) lub (D,H,W)
    cfg: GridKernelConfig
) -> Tuple[np.ndarray, dict]: ...
# Zwraca (x_new, info) gdzie info['clamp_hit_rate'] = float

def grid_step_gossip(
    x: np.ndarray,
    cfg: GridKernelConfig,
    a: float = 2.0
) -> Tuple[np.ndarray, dict]: ...

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
lap = (
    np.roll(x, -1, axis=0) +  # up
    np.roll(x,  1, axis=0) +  # down
    np.roll(x, -1, axis=1) +  # left
    np.roll(x,  1, axis=1) +  # right
    - 4 * x
)
x_new = x + cfg.step * cfg.k * lap

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
import math

def linear_softbody(xi: float, xj: float, w: float, k: float = 1.0) -> float:
    # Liniowa sprezystosc; zachowuje mase przy reversible=True
    return w * k * (xj - xi)

def spatial_econ(xi: float, xj: float, w: float,
                 tax: float = 0.05, theta: float = 0.0) -> float:
    # Dyfuzja popytu/podazy z tarciem (podatek od nadwyzki)
    return w * (xj - xi) - tax * max(0.0, xi - theta)

def gossip_sigmoid(xi: float, xj: float, w: float, a: float = 2.0) -> float:
    # Nieliniowe progowanie -- rozchodzenie informacji/zaufania
    return w * (1.0 / (1.0 + math.exp(-a * (xj - xi))) - 0.5)

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
def total_mass(x) -> float:
    return float(sum(x.values()) if isinstance(x, dict) else x.sum())

def l2_energy(x) -> float:
    return float(sum(v*v for v in x.values()) if isinstance(x, dict) else (x*x).sum())

def max_grad(x, G=None) -> float: ...
    # dla grid: max(|grad_x|); dla grafu: max(|x[j]-x[i]|) po krawedziach

def compute_metrics(x) -> dict:
    return {'mass': total_mass(x), 'energy': l2_energy(x), 'max_grad': max_grad(x)}

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
@dataclass
class SnapshotMeta:
    run_id: str; step: int; path_bin: str; path_meta: str
    sha256: str; size_bytes: int; created_utc: str
    metrics: dict; kernel_info: dict

class SnapshotStore:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.db_path = os.path.join(base_dir, 'index.sqlite')
        self._init_db()  # PRAGMA journal_mode=WAL; CREATE TABLE snapshots

    def save(self, run_id, step, x, metrics=None, kernel_info=None, notes=None) -> SnapshotMeta:
        # 1. zapis do *.tmp
        # 2. fsync(plik)
        # 3. rename(tmp, final)
        # 4. fsync(katalog)
        # 5. INSERT INTO snapshots ...

    def load(self, run_id, step) -> Tuple[np.ndarray, SnapshotMeta]:
        # Weryfikuje SHA-256; rzuca RuntimeError przy niezgodnosci

    def list_steps(self, run_id, status='OK') -> List[int]: ...
    def mark_corrupt(self, run_id, step) -> None: ...

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
@dataclass
class RollbackConfig:
    enabled: bool = True
    eps_mass: float = 1e-6           # tolerancja dryfu masy
    spike_factor: float = 3.0        # energy > spike_factor * median(last_K)
    grad_limit: float = 50.0         # max_grad przekroczony
    clamp_hit_rate_limit: float = 0.20
    recent_window: int = 25          # ostatnie K krokow do mediany
    step_shrink: float = 0.5         # mnoznik redukcji step_size po rollback
    min_step_size: float = 1e-6

class RollbackController:
    def __init__(self, store: SnapshotStore, cfg: RollbackConfig, audit_log_path: str): ...

    def check_anomaly(self, x, metrics, step_size, kernel_cfg,
                      clamp_hit_rate=0.0, baseline_mass=None) -> Optional[str]:
        # Sprawdza: NaN/Inf, mass_drift, energy_spike, max_grad, clamp_hit_rate
        # Zwraca opis anomalii lub None

    def rollback(self, run_id, current_step, reason, step_size, kernel_cfg
                ) -> Tuple[np.ndarray, int, float]:
        # Zwraca (x_restored, restored_step, new_step_size)
        # Wpisuje do patch_audit.log

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
@dataclass
class RetentionPolicy:
    max_run_gb: float = 20.0
    keep_last_steps: int = 2000
    thin_after_steps: int = 2000
    thin_keep_every: int = 100  # po thin_after_steps: zachowaj co N krokow

class RetentionManager:
    def __init__(self, snapshot_db_path: str): ...
    def apply(self, run_id, current_step, policy: RetentionPolicy) -> int:
        # Prune'uje snapshoty; zwraca liczbe usunietych
        # Usuwa .bin + .meta.json, ustawia status='PRUNED' w SQLite

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
class GridView(QtWidgets.QWidget):
    def set_grid(self, x: np.ndarray) -> None:
        # Obsluguje 2D (H,W) i 3D (Z,H,W)
        # Dla 3D aktywuje z_slider (setMinimum(0), setMaximum(Z-1))
        # setImage(x.T) lub setImage(x[0].T)

    def append_metrics(self, metrics: Dict[str, float]) -> None:
        # Dodaje punkt do historii mass/energy/max_grad
        # Odswierza curve.setData(x, y) dla kazdej metryki

    def _on_z_changed(self, z: int) -> None:
        # Callback z_slider -> setImage(data[z].T)

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
class SnapshotReplayPanel(QtWidgets.QGroupBox):
    step_selected = QtCore.pyqtSignal(int)
    def set_steps(self, steps: list) -> None:
        # slider.setMinimum(min(steps)); slider.setMaximum(max(steps))

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
def test_mass_conservation(kernel, x0):
    x1 = kernel.step_update(x0)
    assert abs(sum(x1.values()) - sum(x0.values())) < 1e-6

def test_no_growth_small_step(kernel, x0):
    x1 = kernel.step_update(x0)
    assert max(abs(v) for v in x1.values()) < 1e4

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
from hypothesis import given, strategies as st

@given(st.lists(st.floats(-1.0, 1.0), min_size=3, max_size=10))
def test_stability(vals):
    # buduj graf, kernel, 1 krok, sprawdz zakres
    assert max(abs(v) for v in vals) < 2.0

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
def test_snapshot_roundtrip_hash_ok():
    x0 = np.random.randn(32, 32).astype(np.float32)
    meta = store.save('runA', 1, x0)
    x1, meta2 = store.load('runA', 1)
    assert np.allclose(x1, x0)
    assert meta.sha256 == meta2.sha256

def test_snapshot_corrupt_detected():
    # zapis, reczna modyfikacja pliku .bin, load -> RuntimeError
    ...

# Source: Mikrojądra dyfuzyjne w silnikach symulacyjnych
def test_impulse_symmetry_one_step():
    x[H//2, W//2] = 1.0
    y, _ = grid_step_softbody(x, cfg)
    # gorny i dolny sasiad: identyczne wartosci
    assert abs(y[c[0]-1, c[1]] - y[c[0]+1, c[1]]) < 1e-12

def test_wrap_boundary_mass_conservation():
    total_before = x.sum()
    y, _ = grid_step_softbody(x, cfg_wrap)
    assert abs(y.sum() - total_before) < 1e-5

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
import json, hashlib, unicodedata

OBS_ENCODING_VERSION = "obs-v1"

def canonicalize(obj) -> str:
    # rekurencja: str→NFC, float→round(12), list/dict
    return json.dumps(safe, sort_keys=True, separators=(",",":"), ensure_ascii=False)

def hash_obj(obj) -> str:
    return hashlib.sha256(canonicalize(obj).encode()).hexdigest()

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
def canonical_obs_bytes(obs) -> bytes:
    # ndarray:  b"NDARRAYv1\0" + dtype_le + b"\0" + shape + b"\0" + data_C_le
    # dict:     b"DICTv1\0" + n_keys + sorted(keys) + rekurencja
    # list/tuple: b"LISTv1\0" + n_items + rekurencja
    # str/int/float/None: b"JSONv1\0" + json.dumps(NFC)
    # inne: raise TypeError  # nigdy heurystyki!

def obs_hash_hex(obs) -> str:
    return hashlib.sha256(canonical_obs_bytes(obs)).hexdigest()

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
@dataclass
class TraceStep:
    step_id: int
    observation_hash: str       # SHA-256 kanonicznej obs
    observation_size: int
    memory_hash_before: str
    plan_hash: str
    action: str
    reward: float               # round(x, 12)
    done: bool
    memory_hash_after: str

@dataclass
class TraceHeader:
    schema_version: str         # SemVer "1.0.0"
    run_id: str
    env_name: str
    global_seed: int
    obs_encoding_version: str   # "obs-v1"
    hash_policy: str            # "sha256"
    float_precision: int        # 12
    created_at_logical: int     # 0

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
@dataclass
class DiffReport:
    total_steps: int
    action_mismatch: int
    memory_mismatch: int
    reward_mismatch: int
    first_divergence_step: int | None
    classification: str  # "AGENT_DRIFT"|"ENV_DRIFT"|"MEMORY_DRIFT"|"FLOAT_DRIFT"|"SCHEMA_FAIL"|"OK"

def compare_traces(gold_steps, run_steps, reward_tol=1e-12) -> DiffReport: ...

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
@dataclass
class GateResult:
    gate_id: str  # "G1"–"G5"
    status: str   # "PASS"|"FAIL"|"FAIL_HARD"|"FAIL_NONDETERMINISTIC"|"FAIL_CRITICAL"
    value: float | None
    threshold: float | None

def eval_gates(diff: DiffReport) -> list[GateResult]: ...

def overall_exit_code(gates: list[GateResult]) -> int:
    # 0=PASS, 2=FAIL, 4=SCHEMA_FAIL

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
class SQLiteStore:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA synchronous=FULL")

    def begin(self): self.conn.execute("BEGIN IMMEDIATE;")
    def insert_run_placeholder(self, r: RunRow) -> None: ...
    def finalize_run(self, run_id, trace_hash, classification, first_divergence_step): ...
    def insert_steps(self, run_id, steps: list[dict]): ...  # executemany
    def insert_gates(self, run_id, gates: list[GateResult]): ...
    def insert_metrics(self, run_id, metrics: dict): ...
    def insert_artifact(self, ...): ...

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
store.begin()
→ insert_run_placeholder
→ insert_steps
→ insert_gates
→ insert_metrics
→ insert_artifact (każdy plik)
→ finalize_run
→ conn.commit()
# wyjątek: conn.rollback()

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
def atomic_write_bytes(path: str, data: bytes) -> None:
    # tempfile.mkstemp → write → fsync → os.replace(tmp, path) → fsync(dir_fd)

class ArtifactManager:
    def allocate_run_dir(suite_id, build_fingerprint, run_id) -> str
    def write_artifact_json(run_dir, filename, obj, kind, run_id, artifact_id) -> Artifact
    def write_artifact_text(run_dir, filename, text, ...) -> Artifact

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
class MiniGridAdapter:
    def __init__(self, env_id="MiniGrid-Empty-5x5-v0", max_steps=200):
        self.env = gym.make(env_id, max_steps=max_steps)

    def reset(self, seed: int) -> tuple[Any, dict]:
        obs, info = self.env.reset(seed=seed)
        self.env.action_space.seed(seed)
        return obs, info

    def step(self, action) -> StepResult:
        obs, reward, terminated, truncated, info = self.env.step(action)
        return StepResult(obs, float(reward), bool(terminated or truncated), info)

    def snapshot(self) -> dict: ...
    def close(self) -> None: self.env.close()

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
class TextWorldAdapter:
    def __init__(self, game_file: str):
        self.env = textworld.gym.make(game_file)  # deterministyczność z pliku .tw/.z8

    def reset(self, seed: int) -> tuple[str, dict]:
        obs = self.env.reset()   # seed tylko informacyjny, deterministyczność z game_file
        return obs, {}

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
class DeterministicPolicyAgent:
    def reset(self) -> None: self.mem = {}
    def act(self, obs: Any) -> AgentOut:
        # TextWorld (str obs) → "look"
        # Minigrid (dict/array obs) → "forward"
        # zawsze zwraca json-serializable action str

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
def run_episode(env: EnvAdapter, agent, seed: int, max_steps: int, action_mapper) -> tuple[dict, list[dict], dict]:
    obs, info0 = env.reset(seed=seed)
    agent.reset()
    steps = []
    for t in range(max_steps):
        obs_hash = obs_hash_hex(obs)
        mem_before = copy.deepcopy(agent.mem)
        mem_hash_before = hash_obj(mem_before)
        out = agent.act(obs)
        env_action = action_mapper(out.action)
        sr = env.step(env_action)
        steps.append({
            "step_id": t,
            "observation_hash": obs_hash,
            "memory_hash_before": mem_hash_before,
            "plan_hash": hash_obj(out.plan),
            "action": out.action,
            "reward": round(sr.reward, 12),
            "done": sr.done,
            "memory_hash_after": hash_obj(agent.mem),
        })
        if sr.done: break
    return meta, steps, stats

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
# test_obs_canonical.py
def test_ndarray_stride_invariant():
    a = np.arange(100, dtype=np.uint8).reshape(10, 10)
    b = a[:, :]                      # view (różne strides)
    c = np.asfortranarray(a)         # F-order
    assert obs_hash_hex(a) == obs_hash_hex(b) == obs_hash_hex(c)

def test_endianness_invariant():
    a_le = np.array([1, 2, 3], dtype="<u2")
    a_be = a_le.astype(">u2")
    assert obs_hash_hex(a_le) == obs_hash_hex(a_be)

def test_dict_key_order_invariant():
    d1 = {"b": 1, "a": 2}
    d2 = {"a": 2, "b": 1}
    assert obs_hash_hex(d1) == obs_hash_hex(d2)

def test_unknown_type_raises():
    with pytest.raises(TypeError):
        canonical_obs_bytes(object())

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
@given(st.dictionaries(st.text(), st.integers()))
def test_canonical_dict_permutation_invariant(d):
    keys = list(d.keys())
    # permutacja kluczy → ten sam hash
    for perm in itertools.permutations(keys):
        d2 = {k: d[k] for k in perm}
        assert hash_obj(d) == hash_obj(d2)

# Source: Mini‑grid i TextWorld: małe, deterministyczne harnessy
def normalize_step(ret):
    if len(ret) == 5:   # Gymnasium
        obs, reward, terminated, truncated, info = ret
        return obs, float(reward), bool(terminated or truncated), dict(info)
    if len(ret) == 4:   # Gym legacy
        obs, reward, done, info = ret
        return obs, float(reward), bool(done), dict(info)
    raise ValueError(f"Unexpected step() return length: {len(ret)}")

# Source: New agent‑based simulation updates_04
# Wzorzec: adapter silnik_świata / silnik_decyzji
class WorldEngine:
    def step(self, agent_id, state) -> Event: ...  # deterministyczny

class DecisionEngine:
    def decide(self, agent_id, obs) -> Action: ...  # reguły LUB LLM

class Runner:
    def run(self, scenario, seed, frozen_decisions=None):
        rng = Random(seed)
        for t in range(scenario.t_end):
            for agent in self.agents:
                obs = self.world.observe(agent)
                action = frozen_decisions[t][agent] if frozen_decisions                          else self.decision.decide(agent, obs)
                event = self.world.step(agent, action)
                self.journal.append(event)  # JSONL event-sourcing

# Kryteria akceptacji scenariusza (SCN-0002 wzorzec):
acceptance = {
    "max_schema_error_rate": 0.01,
    "max_sd_delta_over_abs_ate": 2.0,
    "min_success_runs": 0.98
}
# Ablacje obowiązkowe: no_heterogeneity, no_comms, [no_memory dla LLM]

# Source: New economic  and social simulation tools
import hashlib, yaml, json, os
os.environ["PYTHONHASHSEED"] = "0"

def run_id_from_config(cfg_path: str) -> str:
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    canonical = json.dumps(cfg, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]

# Source: New economic  and social simulation tools
@dataclass
class Order:
    order_id: str; side: str  # 'BID'/'ASK'
    price: float; qty: int; timestamp: int

class MarketKernel:
    def __init__(self, rng_seed: int = 42):
        self.bids: list[Order] = []
        self.asks: list[Order] = []
        self.events: list[dict] = []
        self._t = 0; self._rng = random.Random(rng_seed)

    def submit(self, order: Order) -> list[dict]:
        # price-time priority matching; emits FILL/PARTIAL/CANCEL events
        ...

    def to_events_jsonl(self) -> str:
        return "\n".join(json.dumps(e, sort_keys=True) for e in self.events)

# Source: New economic  and social simulation tools
# Eliminuje surowe order_id, normalizuje pola do porównania
def canonical_projection(event: dict) -> dict:
    keys = {"t", "side", "price", "qty", "type", "aggressor"}
    return {k: event[k] for k in keys if k in event}

def first_divergence(stream_a, stream_b):
    for i, (a, b) in enumerate(zip(stream_a, stream_b)):
        if canonical_projection(a) != canonical_projection(b):
            return i, a, b
    return None

# Source: New papers SRE Simulation Formal Methods_04
def evidence_id(ev_wo_id: dict) -> str:
    payload = json.dumps(ev_wo_id, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return "ev_" + hashlib.sha256(payload).hexdigest()

# Source: New simulation research & tools
manifest = {
  "run_id": run_id, "model": model_name, "version": version,
  "seed": seed, "started_utc": ..., "platform": platform.node(),
  "params": params
}
# zapis: runs/<run_id>/manifest.json

# Source: New simulation research & tools
@dataclass(frozen=True)
class Entry:
    t: int; debit_acct: str; credit_acct: str; amount: int; meta: Dict
class Ledger:
    def post(self, e: Entry):
        if e.amount < 0: raise ValueError("amount must be non-negative")
        self.bal[e.debit_acct] += e.amount
        self.bal[e.credit_acct] -= e.amount

# Source: New simulation research & tools
def reset(seed): ...  # manifest epizodu
def observation(agent): ...  # cechy stanu + action_mask
def step(actions): ...  # deterministyczny krok + journal

# Source: Symulacje gier jako laboratoria AI
import hashlib, json, random
from typing import Any

def stable_hash(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

def namespaced_rng(run_seed: int, namespace: str, tick_seq: int) -> random.Random:
    material = f"{run_seed}|{namespace}|{tick_seq}"
    h = hashlib.sha256(material.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big", signed=False)
    return random.Random(seed)

# Source: Symulacje gier jako laboratoria AI
def tick(self, seq: int) -> None:
    self.storage.begin()
    try:
        self.storage.insert_tick(seq)
        events = []
        for rule in self.rules:
            events += rule.apply(self.storage, seq)
        obs = self.storage.get_observation(self.agent_id)
        action = self.agent.step(obs, seq)
        events += self.storage.apply_action(action, seq)
        self.storage.insert_events(events)
        h = self.storage.compute_state_hash()
        self.storage.write_tick_hash(seq, h)
        self.storage.commit()
    except Exception:
        self.storage.rollback()
        raise

# Source: Symulacje gier jako laboratoria AI
def apply_recorded_event(storage, ev_type: str, payload: dict) -> None:
    if ev_type == "rule_change":
        for k, v in payload.items():
            storage.set_meta(str(k), str(v))
    elif ev_type == "state_patch":
        storage.set_entity(int(payload["entity_id"]), **payload["fields"])

# Source: Symulacje gier jako laboratoria AI
cmd = [
    "bwrap", "--unshare-net", "--unshare-pid", "--die-with-parent",
    "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
    "--ro-bind", "/usr", "/usr",
    "--ro-bind", str(venv_root), str(venv_root),
    "--ro-bind", self.project_root, self.project_root,
    "--", str(py), "-m", "qa_sim.runtime.agent_worker", ...
]
# fallback: unshare -n -- ... plain ...

# Source: Symulacje gier jako laboratoria AI
DEFAULT_PRAGMAS = {
    "journal_mode": "WAL",
    "synchronous": "NORMAL",
    "temp_store": "MEMORY",
    "foreign_keys": "ON",
}

# Source: Symulacyjne gospodarki sterowane przez AI
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class InFlight:
    recipe: str
    remaining: int  # ticki do ukończenia

@dataclass
class State:
    t: int
    stock: Dict[str, int]          # int-scale (np. 1 unit = 1000 milli-units)
    buildings: Dict[str, int]      # liczba aktywnych budynków per typ
    inflight: List[InFlight] = field(default_factory=list)
    power_cap: int = 0

# Source: Symulacyjne gospodarki sterowane przez AI
def step(state: State, action: Dict, cfg: Dict) -> Dict:
    """
    action = {
      "build_delta": {"miner": +2, "smelter": -1, ...},
      "starts": {"mine_ore": 3, "smelt_plate": 1, ...}
    }
    Zwraca metrics dict. Mutuje state in place.
    """
    # 1. Zastosuj build deltas (clamp do 0..max_buildings)
    for b, delta in action.get("build_delta", {}).items():
        state.buildings[b] = max(0, state.buildings.get(b, 0) + delta)

    # 2. Oblicz zużycie mocy; ogranicz starts jeśli przekracza power_cap
    power_used = sum(cfg["buildings"][b]["power"] * n
                     for b, n in state.buildings.items())
    starts_denied_power = 0

    # 3. Progress inflight: tick remaining down, apply outputs on completion
    new_inflight = []
    for p in state.inflight:
        p.remaining -= 1
        if p.remaining <= 0:
            recipe = cfg["recipes"][p.recipe]
            for res, qty in recipe["outputs"].items():
                state.stock[res] = state.stock.get(res, 0) + qty
        else:
            new_inflight.append(p)
    state.inflight = new_inflight

    # 4. Start nowych procesów (jeśli power + inputs dostępne)
    for recipe_name, count in action.get("starts", {}).items():
        recipe = cfg["recipes"][recipe_name]
        for _ in range(count):
            if power_used + cfg["buildings"][recipe["building"]]["power"] > state.power_cap:
                starts_denied_power += 1
                continue
            if all(state.stock.get(r, 0) >= qty
                   for r, qty in recipe["inputs"].items()):
                for r, qty in recipe["inputs"].items():
                    state.stock[r] -= qty
                state.inflight.append(InFlight(recipe_name, recipe["cycle_time"]))
                power_used += cfg["buildings"][recipe["building"]]["power"]

    # 5. Zaspokojenie popytu (gear)
    demand = cfg.get("demand", {})
    shortage = {}
    for res, qty in demand.items():
        avail = state.stock.get(res, 0)
        shortage[res] = max(0, qty - avail)
        state.stock[res] = max(0, avail - qty)

    # 6. Clamp do caps (overflow)
    overflow = {}
    for res, cap in {r: d["cap"] for r, d in cfg["resources"].items()}.items():
        excess = max(0, state.stock.get(res, 0) - cap)
        overflow[res] = excess
        state.stock[res] = min(state.stock.get(res, 0), cap)

    state.t += 1
    return {
        "shortage": shortage,
        "overflow": overflow,
        "power_used": power_used,
        "starts_denied_power": starts_denied_power,
    }

# Source: Symulacyjne gospodarki sterowane przez AI
from ortools.sat.python import cp_model

def solve_mpc(state: State, cfg: Dict, H: int, time_limit_s: float,
              x_prev: Dict[str, int]) -> Dict:
    """
    H: horyzont planowania (ticki)
    x_prev: poprzednie allokacje budynków (dla switching cost)
    Zwraca: {"buildings": {...}, "runs": {...}, "status": str, "objective": float}
    """
    model = cp_model.CpModel()
    limits = cfg.get("limits", {})
    weights = cfg.get("weights", {
        "shortage": 1000, "overflow": 10, "holding": 1,
        "build": 5, "maint": 2, "switch": 50
    })

    # Zmienne: liczba aktywnych budynków
    x = {b: model.NewIntVar(0, limits.get("max_buildings", {}).get(b, 100), f"x_{b}")
         for b in cfg["buildings"]}

    # Zmienne: liczba uruchomień receptury w horyzoncie H
    runs = {p: model.NewIntVar(0, limits.get("max_runs", 10_000_000), f"runs_{p}")
            for p in cfg["recipes"]}

    # Ograniczenie mocy
    model.Add(sum(cfg["buildings"][b]["power"] * x[b] for b in x) <= cfg["power_cap"])

    # Ograniczenia receptur: runs_p <= floor(H/cycle) * x[building_p]
    for p, recipe in cfg["recipes"].items():
        max_per_building = H // recipe["cycle_time"]
        model.Add(runs[p] <= max_per_building * x[recipe["building"]])

    # Bilans zasobów + zmienne slack (shortage/overflow)
    shortage_vars, overflow_vars, stock_end_vars = {}, {}, {}
    for res in cfg["resources"]:
        net = sum(cfg["recipes"][p]["outputs"].get(res, 0) * runs[p] for p in runs) \
            - sum(cfg["recipes"][p]["inputs"].get(res, 0) * runs[p] for p in runs)
        demand_h = cfg.get("demand", {}).get(f"{res}_per_tick", 0) * H
        cap = cfg["resources"][res]["cap"]

        short = model.NewIntVar(0, demand_h + 1, f"short_{res}")
        over  = model.NewIntVar(0, cap + 1, f"over_{res}")
        stock_end = model.NewIntVar(0, cap, f"stockend_{res}")
        shortage_vars[res], overflow_vars[res], stock_end_vars[res] = short, over, stock_end

        model.Add(stock_end == state.stock.get(res, 0) + net - demand_h + short - over)

    # Switching cost: |x_b - x_b_prev|
    abs_dx = {}
    for b in x:
        prev = x_prev.get(b, 0)
        d = model.NewIntVar(-200, 200, f"dx_{b}")
        abs_d = model.NewIntVar(0, 200, f"adx_{b}")
        model.Add(d == x[b] - prev)
        model.AddAbsEquality(abs_d, d)
        abs_dx[b] = abs_d

    # Koszty build i maint
    build_cost = sum(cfg["buildings"][b]["build_cost"] * x[b] for b in x)
    maint_cost = sum(cfg["buildings"][b]["maint"] * x[b] * H for b in x)

    # Cel: minimalizuj weighted sum
    model.Minimize(
        sum(weights["shortage"] * shortage_vars[r] for r in shortage_vars) +
        sum(weights["overflow"]  * overflow_vars[r]  for r in overflow_vars) +
        sum(weights["holding"]   * stock_end_vars[r] * cfg["resources"][r]["holding_cost"]
            for r in stock_end_vars) +
        weights["build"] * build_cost +
        weights["maint"]  * maint_cost +
        sum(weights["switch"] * abs_dx[b] for b in abs_dx)
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    solver.parameters.num_search_workers = 1  # determinizm

    status = solver.Solve(model)
    status_name = solver.StatusName(status)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {
            "buildings": {b: solver.Value(x[b]) for b in x},
            "runs":      {p: solver.Value(runs[p]) for p in runs},
            "status":    status_name,
            "objective": solver.ObjectiveValue(),
        }
    # Fallback: zachowaj poprzedni plan
    return {"buildings": x_prev, "runs": {}, "status": status_name, "objective": float("inf")}

# Source: Symulacyjne gospodarki sterowane przez AI
from ortools.graph.python import min_cost_flow

def solve_mcf(supplies: Dict[int, int], arcs: List[tuple]) -> Dict:
    """
    supplies: {node_id: supply}  (positive=supply, negative=demand)
    arcs: [(u, v, capacity, unit_cost), ...]
    """
    mcf = min_cost_flow.SimpleMinCostFlow()
    for (u, v, cap, cost) in arcs:
        mcf.AddArcWithCapacityAndUnitCost(int(u), int(v), int(cap), int(cost))
    for n, s in supplies.items():
        mcf.SetNodeSupply(int(n), int(s))
    status = mcf.Solve()
    if status == mcf.OPTIMAL:
        return {
            "flows": [mcf.Flow(a) for a in range(mcf.NumArcs())],
            "optimal_cost": mcf.OptimalCost(),
        }
    return {"flows": [], "optimal_cost": None, "status": status}

# Source: Symulacyjne gospodarki sterowane przez AI
def project_runs_to_starts(plan_runs: Dict[str, int], H: int, K: int) -> Dict[str, int]:
    """
    Tłumaczy agregowany plan (runs w horyzoncie H) na per-tick starts dla K ticków.
    """
    starts = {}
    for p, rp in plan_runs.items():
        starts[p] = int(round(rp * (K / max(1, H))))
    return starts

# Source: Symulacyjne gospodarki sterowane przez AI
import sqlite3, json, hashlib

def jcanon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def init_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, started_at REAL, seed INTEGER, config_hash TEXT);
        CREATE TABLE IF NOT EXISTS steps(run_id TEXT, t INTEGER, state_hash TEXT, action_json TEXT, reward REAL, metrics_json TEXT, PRIMARY KEY(run_id,t));
        CREATE TABLE IF NOT EXISTS solver_runs(run_id TEXT, t INTEGER, solver TEXT, status INTEGER, objective REAL, solve_ms INTEGER, plan_json TEXT);
    """)
    return conn

def log_step(conn, run_id: str, t: int, state: State, action: Dict, reward: float, metrics: Dict):
    state_hash = sha256(jcanon({"stock": state.stock, "buildings": state.buildings}))
    conn.execute(
        "INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?,?)",
        (run_id, t, state_hash, jcanon(action), reward, jcanon(metrics))
    )
    conn.commit()

# Source: Symulacyjne gospodarki sterowane przez AI
def reward_fn(metrics: Dict, cfg: Dict, state: State) -> float:
    w = cfg.get("reward_weights", {"shortage": 100, "overflow": 5, "oscillation": 2, "cost": 1})
    shortage    = sum(metrics["shortage"].values())
    overflow    = sum(metrics["overflow"].values())
    oscillation = sum(abs(state.stock.get(r, 0) - prev_stock.get(r, 0))
                      for r in state.stock)  # Δstock
    cost        = sum(cfg["buildings"][b]["maint"] * n
                      for b, n in state.buildings.items())
    return -(w["shortage"] * shortage + w["overflow"] * overflow +
             w["oscillation"] * oscillation + w["cost"] * cost)

# Source: Typy algorytmów biologicznych
import sounddevice as sd
import numpy as np
data = sd.rec(int(44100 * 5), samplerate=44100, channels=1, dtype='float32')
sd.wait()
binary = (data[:,0] > 0.01).astype(np.uint8)  # próg amplitudy
binary.tofile("nagranie.bin")
# 8 bitów = 1 znak ASCII → dekodowanie tekstowe
