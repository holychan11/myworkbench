"""命令执行沙箱：默认拒绝，白名单放行，危险操作升级为二次确认。"""
import re
import shlex
import subprocess
from dataclasses import dataclass

from ..config import settings

RISK_SAFE = "safe"
RISK_RISKY = "risky"
RISK_FORBIDDEN = "forbidden"


@dataclass
class ExecResult:
    ok: bool
    stdout: str
    stderr: str
    risk: str


# 危险命令特征（用于"升级为二次确认"，不作放行依据）
DANGEROUS_PATTERNS = [
    re.compile(r"\brm\s+(-[a-z]*r[a-z]*f?|[a-z]*f[a-z]*r?)\b", re.I),
    re.compile(r"\b(del|erase)\b", re.I),
    re.compile(r"\brmdir\b", re.I),
    re.compile(r"\bformat\s+[a-zA-Z]:", re.I),
    re.compile(r"\b(shutdown|reboot)\b", re.I),
    re.compile(r"\bmkfs|diskpart|fdisk\b", re.I),
    re.compile(r"\breg\s+delete\b", re.I),
    re.compile(r"\bsc\s+delete\b", re.I),
    re.compile(r"(curl|wget|iwr|invoke-webrequest).*(\||;|\s-outfile)", re.I),
    re.compile(r"-encodedcommand|iex\b|invoke-expression|start-process", re.I),
]

# 只读/低危命令白名单，命中且不含危险特征则免确认
SAFE_COMMANDS = {
    "dir", "ls", "pwd", "type", "cat", "where", "which", "echo",
    "get-childitem", "get-location", "get-content", "tasklist", "ps",
}


def assess(cmd: str) -> str:
    if not cmd or not cmd.strip():
        return RISK_FORBIDDEN
    try:
        head = shlex.split(cmd)[0].lower()
    except ValueError:
        head = cmd.split()[0].lower() if cmd.split() else ""
    if any(p.search(cmd) for p in DANGEROUS_PATTERNS):
        return RISK_RISKY
    if head in SAFE_COMMANDS:
        return RISK_SAFE
    return RISK_RISKY  # 非白名单命令默认视为需确认（默认拒绝原则）


def execute(cmd: str, workdir: str | None = None,
            timeout: float | None = None, max_output: int | None = None) -> ExecResult:
    workdir = workdir or settings.EXEC_WORKDIR
    timeout = timeout or settings.EXEC_TIMEOUT
    max_output = max_output or settings.EXEC_MAX_OUTPUT
    try:
        proc = subprocess.run(
            ["cmd", "/c", cmd], cwd=workdir, timeout=timeout,
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        return ExecResult(
            ok=proc.returncode == 0,
            stdout=proc.stdout[:max_output],
            stderr=proc.stderr[:max_output],
            risk=assess(cmd))
    except subprocess.TimeoutExpired:
        return ExecResult(ok=False, stdout="", stderr=f"执行超时（>{timeout}s）已终止", risk=assess(cmd))
    except FileNotFoundError:
        return ExecResult(ok=False, stdout="", stderr="shell 不可用", risk=assess(cmd))
