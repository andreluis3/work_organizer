from __future__ import annotations

TEMPLATE_ESTUDO = """# Titulo

## Objetivo
Descreva o que voce quer aprender.

## Pontos principais
- Conceito 1
- Conceito 2
- Conceito 3

## Proximos passos
- Revisar
- Praticar
"""

TEMPLATE_CODIGO = """# Titulo

## Problema
Descreva aqui

## Codigo
```python
# codigo
```

## Observacoes
- O que funcionou
- O que precisa melhorar
"""

TEMPLATE_RESUMO = """# Titulo

## Resumo
Escreva um resumo curto do assunto.

## Insights
- Insight 1
- Insight 2

## Acoes
- Acao 1
- Acao 2
"""

NOTE_TEMPLATES = {
    "estudo": TEMPLATE_ESTUDO,
    "codigo": TEMPLATE_CODIGO,
    "resumo": TEMPLATE_RESUMO,
}


def get_template(name: str) -> str:
    return NOTE_TEMPLATES.get(name, "")


def get_template_names() -> list[str]:
    return list(NOTE_TEMPLATES.keys())
