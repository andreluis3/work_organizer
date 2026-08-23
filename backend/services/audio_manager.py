from __future__ import annotations

from pathlib import Path

import pygame


class AudioManager:
    """Toca os efeitos sonoros do Focus Time.

    Usa pygame.mixer (mesma engine que já era usada no protótipo antigo).
    Os caminhos dos arquivos são resolvidos com pathlib.Path a partir da
    localização deste próprio módulo — não de os.getcwd() — então funciona
    igual seja qual for o diretório de onde `main_pyqt6.py` for executado.

    Responsabilidade única: carregar e reproduzir sons de evento.
    Nenhuma lógica de estado do timer, nenhum PyQt aqui.
    """

    # Este arquivo está em backend/services/audio_manager.py.
    # backend/services -> backend -> raiz do projeto -> assets/audio
    # Se você mover este arquivo para backend/audio_manager.py (um nível
    # acima), troque para: .parent.parent / "assets" / "audio"
    _AUDIO_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "audio"

    _FILES: dict[str, str] = {
        "start": "pianonote.mp3",
        "pause": "pause_sond.mp3",
        "resume": "pianonote.mp3",
        "finish": "pianostop.mp3",
        "reset": "pianostop.mp3",
    }

    def __init__(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._load_all()

    # ---- carregamento ----

    def _load_all(self) -> None:
        for key, filename in self._FILES.items():
            self._sounds[key] = self._load(filename)

    def _load(self, filename: str) -> pygame.mixer.Sound | None:
        path = self._AUDIO_DIR / filename
        if not path.exists():
            print(f"[AudioManager] Arquivo de áudio não encontrado: {path}")
            return None
        try:
            return pygame.mixer.Sound(str(path))
        except pygame.error as exc:
            print(f"[AudioManager] Erro ao carregar '{path.name}': {exc}")
            return None

    def _play(self, key: str) -> None:
        sound = self._sounds.get(key)
        if sound is None:
            return
        try:
            sound.play()
        except pygame.error as exc:
            print(f"[AudioManager] Erro ao reproduzir som '{key}': {exc}")

    def stop_all(self) -> None:
        """Para qualquer som em reprodução no mixer."""
        try:
            pygame.mixer.stop()
        except pygame.error:
            pass

    # ---- eventos públicos ----

    def play_start_sound(self) -> None:
        self._play("start")

    def play_pause_sound(self) -> None:
        self._play("pause")

    def play_resume_sound(self) -> None:
        self._play("resume")

    def play_finish_sound(self) -> None:
        self._play("finish")

    def play_reset_sound(self) -> None:
        self._play("reset")