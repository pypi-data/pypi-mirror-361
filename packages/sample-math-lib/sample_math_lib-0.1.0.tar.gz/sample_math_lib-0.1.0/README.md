# Sample Math Lib

Esta é uma biblioteca Python simples de exemplo que fornece funções matemáticas básicas. O objetivo deste projeto é demonstrar o passo a passo da criação de uma biblioteca Python, desde a estrutura do projeto até a publicação no GitHub.

## Instalação

Você pode instalar a biblioteca diretamente do GitHub usando `pip`:

```bash
pip install git+https://github.com/adonitech-solutions/sample-python-lib.git
```

Alternativamente, você pode baixar os arquivos `.whl` ou `.tar.gz` da seção de [Releases](https://github.com/adonitech-solutions/sample-python-lib/releases) e instalar localmente com `pip`:

```bash
# Exemplo para o arquivo .whl
pip install /caminho/para/o/arquivo/sample_math_lib-0.0.1-py3-none-any.whl
```

## Como Usar

Aqui estão alguns exemplos de como usar as funções da biblioteca:

```python
from adonitech.sample_math_lib.operations import add, subtract, multiply, divide

# Operações básicas
soma = add(10, 5)
subtracao = subtract(10, 5)
multiplicacao = multiply(10, 5)
divisao = divide(10, 5)

print(f"Soma: {soma}")
print(f"Subtração: {subtracao}")
print(f"Multiplicação: {multiplicacao}")
print(f"Divisão: {divisao}")

# Exemplo de tratamento de erro para divisão por zero
try:
    divide(10, 0)
except ValueError as e:
    print(f"Erro: {e}")
```

## Executando os Testes

Para contribuir com o desenvolvimento ou validar a integridade do código, você pode executar os testes. O projeto utiliza `pytest` e gerencia as dependências de desenvolvimento através do `pyproject.toml`.

Primeiro, clone o repositório:

```bash
git clone https://github.com/adonitech-solutions/sample-python-lib.git
cd sample-python-lib
```

Em seguida, instale a biblioteca em modo de desenvolvimento:

```bash
pip install -e ".[test]"
```

Agora você pode executar os testes a partir do diretório raiz do projeto:

```bash
pytest
```

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.