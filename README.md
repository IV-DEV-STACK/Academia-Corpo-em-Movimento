# Academia Corpo em Movimento

Sistema web em Django para a proprietária manter modalidades e turmas e publicar
essas informações diretamente do banco de dados para os alunos.

## O que o sistema faz

- Painel administrativo protegido pelo Django em `/admin/`.
- Cadastro, edição, consulta e exclusão de modalidades; modalidades associadas
  a turmas não podem ser excluídas.
- Filtro de modalidades por ativa/inativa e busca por nome no painel.
- Cadastro, edição, consulta e exclusão de turmas.
- Filtros de turmas por modalidade e dia da semana e busca por nome do instrutor
  no painel.
- Página inicial (`/`) com modalidades ativas e suas descrições.
- Grade pública (`/turmas/`) em tabela, ordenada por dia da semana e horário,
  com modalidade, dia, horário, instrutor e vagas.
- Menu para navegar entre as duas páginas públicas.
- Dados iniciais de modalidades e turmas aplicados pelas migrações.

## Regras implementadas

- Uma modalidade tem nome único, sem distinção entre maiúsculas e minúsculas.
- Cada turma pertence a exatamente uma modalidade.
- O painel oferece dias fixos de segunda-feira a sábado.
- Horários usam o formato de hora `HH:MM`.
- Vagas são inteiras não negativas, com padrão de 10.
- Modalidades inativas continuam no painel, mas não aparecem na página inicial.
- Modalidades com turmas associadas não podem ser excluídas.

## Tecnologias

- Python 3.12 ou superior
- Django
- SQLite

## Executar no Windows

No PowerShell, a partir da pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abra `http://127.0.0.1:8000/` para as modalidades, `http://127.0.0.1:8000/turmas/`
para a grade e `http://127.0.0.1:8000/admin/` para o painel. As migrações
carregam as modalidades e turmas iniciais do levantamento.

O endereço e o telefone exibidos são fictícios para a demonstração em sala:
Rua Exemplo, 100 - Centro, Caruaru - PE e (81) 90000-0000. Substitua-os pelos
dados reais usando as variáveis de ambiente `ACADEMY_ADDRESS` e
`ACADEMY_PHONE` antes de publicar o site.

## Testes

```powershell
python manage.py test
```

## Fora do escopo desta versão

Matrícula de alunos, pagamentos, login de aluno, aplicativo para celular e fotos.

## Decisões

- O instrutor é armazenado como texto da turma, conforme o modelo de dados
  fornecido; não há cadastro separado de instrutores.
- Para preservar a regra de não excluir modalidades usadas por turmas, o
  relacionamento usa proteção contra exclusão em vez de apagar turmas em cascata.
- A grade pública lista as turmas cadastradas, inclusive as de modalidades
  inativas; a regra recebida restringe explicitamente a modalidade inativa da
  página inicial, não a página da grade.
