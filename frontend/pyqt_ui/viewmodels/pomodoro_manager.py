from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PomodoroPhase(Enum):
    FOCUS = "focus"
    BREAK = "break"


@dataclass
class PomodoroConfig:
    focus_minutes: int = 25
    break_minutes: int = 5
    total_cycles: int = 4


@dataclass
class PomodoroSnapshot:
    """Snapshot pronto para a Page exibir, sem ela precisar conhecer a máquina de estados."""

    enabled: bool
    phase: PomodoroPhase
    current_cycle: int
    total_cycles: int
    config: PomodoroConfig

    @property
    def is_focus_phase(self) -> bool:
        return self.phase is PomodoroPhase.FOCUS

    @property
    def session_minutes_for_phase(self) -> int:
        return self.config.focus_minutes if self.is_focus_phase else self.config.break_minutes

    @property
    def phase_label(self) -> str:
        if not self.enabled:
            return ""
        rotulo = "Foco" if self.is_focus_phase else "Pausa"
        return f"{rotulo} · Ciclo {self.current_cycle}/{self.total_cycles}"


class PomodoroManager:
    """Controla a alternância foco/pausa e a contagem de ciclos.

    Não dirige o QTimer nem toca som — só decide, dado que uma sessão
    terminou, qual é a próxima fase e por quantos minutos ela deve rodar.
    Quem chama `advance()` no momento certo é a FocusViewModel.
    """

    def __init__(self, config: PomodoroConfig | None = None) -> None:
        self._config = config or PomodoroConfig()
        self._enabled = False
        self._phase = PomodoroPhase.FOCUS
        self._current_cycle = 1

    @property
    def enabled(self) -> bool:
        return self._enabled

    # ---- ativação ----

    def enable(self) -> None:
        self._enabled = True
        self._phase = PomodoroPhase.FOCUS
        self._current_cycle = 1

    def disable(self) -> None:
        self._enabled = False
        self._phase = PomodoroPhase.FOCUS
        self._current_cycle = 1

    def update_config(self, focus_minutes: int, break_minutes: int, total_cycles: int) -> None:
        self._config = PomodoroConfig(
            focus_minutes=self._sanitize(focus_minutes, self._config.focus_minutes),
            break_minutes=self._sanitize(break_minutes, self._config.break_minutes),
            total_cycles=self._sanitize(total_cycles, self._config.total_cycles),
        )

    # ---- transições ----

    def advance(self) -> bool:
        """Chamado quando a sessão atual (foco OU pausa) termina.

        Retorna True quando o Pomodoro inteiro (todos os ciclos) terminou.
        """
        if not self._enabled:
            return False

        if self._phase is PomodoroPhase.FOCUS:
            self._phase = PomodoroPhase.BREAK
            return False

        # estava em pausa: fecha o ciclo atual
        if self._current_cycle >= self._config.total_cycles:
            self._phase = PomodoroPhase.FOCUS
            self._current_cycle = 1
            return True  # pomodoro completo

        self._current_cycle += 1
        self._phase = PomodoroPhase.FOCUS
        return False

    def reset(self) -> None:
        self._phase = PomodoroPhase.FOCUS
        self._current_cycle = 1

    # ---- snapshot ----

    def get_snapshot(self) -> PomodoroSnapshot:
        return PomodoroSnapshot(
            enabled=self._enabled,
            phase=self._phase,
            current_cycle=self._current_cycle,
            total_cycles=self._config.total_cycles,
            config=self._config,
        )

    @staticmethod
    def _sanitize(value: int | None, fallback: int) -> int:
        if value is None or value <= 0:
            return fallback
        return value