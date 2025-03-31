"""
Module containing prompts for GPT interactions
"""

REVIEW_PROMPT = '''
Проведи code review для следующих изменений.
В первую очередь напиши об ошибках если они есть.
Ответ дай в виде HTML.
Ответ дай на языке: {language}.

Изменения в коде:
{changes}
'''
