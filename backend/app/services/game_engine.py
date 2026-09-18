"""Run the existing, trusted game rules in an isolated, bounded JS context.

Only committed repository scripts are executable. Requests supply JSON commands;
they never supply code, player state, rewards, timestamps, or random outcomes.
"""

from functools import lru_cache
import hmac
import json
from pathlib import Path
from typing import Any

import quickjs

GAME_SOURCE = Path(__file__).resolve().parents[3] / "src"
if not GAME_SOURCE.is_dir():
    GAME_SOURCE = Path("/app/game-src")
SCRIPT_NAMES = (
    "data/skills.js",
    "state/game-state.js",
    "utils/icon-utils.js",
    "data/boss-factories.js",
    "data/bosses.js",
    "rules/abyss-fragment-rules.js",
    "rules/boss-display-rules.js",
    "rules/boss-drop-rules.js",
    "data/boss-bootstrap.js",
    "data/zones.js",
    "systems/stat-system.js",
    "ui/render-ui.js",
    "systems/action-result-system.js",
    "systems/item-system.js",
    "systems/combat-system.js",
    "app/main.js",
    "api/master-data-adapter.js",
    "api/master-data-runtime-switch.js",
)
PRELUDE = """
var window = globalThis;
var console = {log(){},warn(){},error(){}};
var document = {hidden:true,getElementById(){return null},querySelector(){return null},querySelectorAll(){return []},addEventListener(){}};
var localStorage = {getItem(){return null},setItem(){throw Error('server_storage_only')},removeItem(){throw Error('server_storage_only')}};
var location = {search:'',hostname:'server'};
var addEventListener=()=>{}, setInterval=()=>1,clearInterval=()=>{},setTimeout=()=>1,clearTimeout=()=>{};
"""


@lru_cache(maxsize=1)
def _scripts() -> tuple[str, ...]:
    return tuple((GAME_SOURCE / name).read_text(encoding="utf-8") for name in SCRIPT_NAMES)


@lru_cache(maxsize=1)
def _runtime_script() -> str:
    return Path(__file__).with_name("game_engine_runtime.js").read_text(encoding="utf-8")


def simulate(
    snapshot: dict,
    runtime: dict,
    master: dict,
    *,
    now_ms: int,
    seed: str,
    rng_cursor: int,
    command: dict | None = None,
) -> dict[str, Any]:
    """Call in a worker thread; a context is created and destroyed in that thread."""
    count = 32768
    key = bytes.fromhex(seed)
    randoms = [
        int.from_bytes(hmac.digest(key, i.to_bytes(8, "big"), "sha256")[:8], "big") >> 11
        for i in range(rng_cursor, rng_cursor + count)
    ]
    ctx = quickjs.Context()
    ctx.set_memory_limit(128 * 1024 * 1024)
    ctx.set_max_stack_size(2 * 1024 * 1024)
    ctx.set_time_limit(8)
    ctx.eval(PRELUDE)
    for source in _scripts():
        ctx.eval(source)
    ctx.eval(_runtime_script())
    invoke = ctx.get("runServerGame")
    output = json.loads(
        invoke(
            json.dumps(
                {
                    "snapshot": snapshot,
                    "runtime": runtime,
                    "master": master,
                    "now": now_ms,
                    "randoms": randoms,
                    "command": command,
                },
                ensure_ascii=False,
                allow_nan=False,
            )
        )
    )
    output["rngCursor"] = rng_cursor + output.pop("randomCount")
    return output
