from datetime import datetime, date, timedelta

FORMATO_BR = "%d/%m/%Y"
FORMATO_HORA_BRASILEIRA = "%d/%m/%Y %H:%M:%S"
FORMATO_ISO = "%Y-%m-%d"
FORMATO_HORA_ISO = "%Y-%m-%d %H:%M:%S"

#conversões básicas 
def agora():
    return datetime.now()

def hoje():
    return date.today()

def datetime_para_str(dt: datetime, formato=FORMATO_HORA_BRASILEIRA) -> str:
    return dt.strftime(formato)
    if not dt:
        return ""
    return dt.strftime(formato)


def str_para_datetime(data_str: str, formato=FORMATO_HORA_BRASILEIRA) -> datetime:
    return datetime.strptime(data_str, formato)


#utilidades de tempo

def minutos_entre(inicio: datetime, fim: datetime) -> int:
    delta = fim - inicio
    return int(delta.total_seconds() // 60)

def horas_entre(inicio: datetime, fim: datetime) -> float:
    delta = fim - inicio
    return delta.total_seconds() / 3600

def adicionar_minutos(dt: datetime, minutos: int) -> datetime:
    return dt + timedelta(minutes=minutos)

#pomodoro #produtividade

def formatar_duracao (minutos:int) -> str:
    horas = minutos // 60 
    resto = minutos % 60

    if horas > 0:
        return f"{horas}h {resto}min"
    else:
        return f"{resto}min"
    
    def nivel_produtividade (horas_concluidas: float, horas_objetivo: float) -> str:
        if horas_objetivo == 0:
            return "Nenhum objetivo definido."

        percentual = (horas_concluidas / horas_objetivo) * 100

        if percentual == 0:
            return "Nenhum progresso."
        elif percentual < 30:
            return "Baixo progresso, mas está indo"
        elif percentual <50:
            return "Progresso moderado, continue assim!"
        elif percentual < 80:
            return "Bom progresso, quase lá!"
        elif percentual <90:
            return "Ótimo progresso, falta pouco!"
        else:
            return "EXCELENTE PROGRESSO! Parabéns!"
        

    