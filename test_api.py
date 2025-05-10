import requests
import textwrap

# Tente 3 vezes
for _ in range(3):
    try:
        response = requests.post('http://127.0.0.1:5001/ask', 
                                 json={'question': 'faça uma lista de substratos com proporção recomendada para shiitake'})
        
        # Processamento mais robusto
        resposta_original = response.json()['answer']
        
        # Substituir quebras de linha e remover espaços extras
        resposta_formatada = resposta_original.replace('\\n', '\n').strip()
        
        # Formatar parágrafos
        paragrafos = resposta_formatada.split('\n\n')
        paragrafos_formatados = [textwrap.fill(p, width=100) for p in paragrafos]
        
        # Imprimir com separação entre parágrafos
        print('\n\n'.join(paragrafos_formatados))
        break
    except requests.exceptions.ConnectionError:
        print("Servidor não disponível. Tentando novamente...")