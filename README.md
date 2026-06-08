# 99Dev

Plataforma web que conecta clientes a desenvolvedores freelancers. O cliente publica uma demanda técnica e o dev pode visualizá-la e registrar tarefas. O projeto é o trabalho interdisciplinar do 1º período do curso de Bacharelado em Engenharia de Software do IFPB — Campus João Pessoa, integrando as disciplinas de Programação Web I, Introdução à Programação e Introdução à Engenharia de Software.

---

## Integrantes

| Nome 
|------|
| Lucas Francelino de Pontes
| Theo Nogueira Virginio
| João Tigre
| Felipe Flor 

---

## Tecnologias utilizadas

- Python 3.13
- Flask + Flask-WTF + Flask-Mail
- SQLAlchemy (SQLite)
- Jinja2 (templates)
- HTML5 + CSS3
- CSV (persistência de demandas)
- bcrypt (hash de senhas)
- Git e GitHub

---

## Funcionalidades implementadas

**Visitante**
- Visualizar página inicial
- Criar conta (cliente ou dev)

**Cliente**
- Gerenciar perfil (e-mail, senha, foto, descrição)
- Publicar demandas (título, tecnologia, descrição, orçamento)
- Visualizar histórico de demandas com filtro por status (Aberta / Pendente / Fechada)
- Buscar demandas por texto

**Desenvolvedor**
- Gerenciar perfil dev (nome, título, skills, valor/hora, GitHub, LinkedIn, resumo)
- Visualizar demandas disponíveis

---

## Estrutura do projeto

```
99dev/
├── main.py                  # Rotas e formulários Flask
├── requirements.txt
├── .gitignore
├── app/
│   ├── __init__.py          # Configuração da app (Flask, Mail, DB)
│   ├── models.py            # Models: Usuario, PerfilDev
│   ├── functions.py         # Lógica de negócio (cadastro, autenticação, CSV...)
│   └── decorators.py        # login_required
├── templates/
│   ├── home.html
│   ├── cadastro.html
│   ├── login.html
│   ├── recuperar-senha.html
│   ├── nova-senha.html
│   ├── perfil.html          # Perfil do dev
│   ├── perfil-editar.html   # Edição de perfil do cliente
│   ├── dashboardCliente.html
│   ├── MeusProjetos.html
│   └── 403.html
├── static/
│   ├── css/
│   ├── img/
│   └── uploads/perfil/      # Fotos de perfil (geradas em runtime)
└── data/
    └── demandas.csv         # Persistência das demandas
```

---

## Como executar o projeto

### Pré-requisitos

- Python 3.10 ou superior
- pip

### Passo a passo

**1. Clone o repositório**

```bash
git clone https://github.com/<seu-usuario>/99dev.git
cd 99dev
```

**2. Crie e ative o ambiente virtual**

```bash
# Criar
python -m venv venv

# Ativar — Linux/macOS
source venv/bin/activate

# Ativar — Windows (PowerShell)
venv\Scripts\activate

# Ativar — Windows (Git Bash)
source venv/Scripts/activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Execute a aplicação**

```bash
python main.py
```

**5. Acesse no navegador**

```
http://127.0.0.1:3001
```

---

## Arquitetura do sistema

```
Sprint 2
```

---

## Diagrama de Casos de Uso

> _![Diagrama de casos de uso 99Dev](https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&target=self&highlight=0000ff&edit=_blank&layers=1&nav=1&title=Diagrama%20de%20uso%20v2.png&dark=0#R%3Cmxfile%3E%3Cdiagram%20name%3D%22P%C3%A1gina-1%22%20id%3D%22xjuuxhfehlK_iUozR-dd%22%3E7V1bd6M4Ev41Pmf3IeeYu%2F3odpLe3ensZiezvWfnTQbZ1jZGDMi59K8fySDbCGwuRgJyeElsoQhQfV9VqaqkTIzl7v1rBMLtE%2FagP9Gn3vvEuJ%2FoumboBv3FWj6SlpnlJA2bCHlpp1PDC%2FoJ08Zp2rpHHowzHQnGPkFhttHFQQBdkmkDUYTfst3W2M%2FeNQQbmGt4cYGfb%2F0v8sg2fQvdObX%2FDaLNlt9Zs%2BfJlR3gndM3ibfAw29nTcbDxFhGGJPk0%2B59CX02eXxekr97vHD1%2BGARDEiVP%2Fi38cfvAVnpS%2Fi%2Fn29P39zfn%2F4F7jQzP0w6ckw%2B%2BCTQRw%2FZx%2F3OX7gERxPjyyuMCKLT9A2soP%2BMY0QQDmiXFSYE7846LHy0YRcIDmnrlux8%2BkWjH%2FGe%2BCiAy6PgprTRZ8N9Ae6PTYT3gbfEPrvbfYADeLyKIw9GwhUC38kLn2A20Br5Pu8z0Q0PwNnape0xifAPeHbFdmdwtaZXNhHwEJ2Es2sOBDZkoyUz8gr8fTojE932CbsNprN2Plf2H3vML9zFBzgvaIdZ%2BH4Yhl%2Bmnzbs93dEZw4EBPIBqfySMZPr6Y3pXML3M%2BmkEv4K8Q6S6IN22Z6B0E4R93YCrJE2pYNY6deUlGb6FaRk2RzHPeGJfkghVQdeVjIw9HIsu4Y3GHgLxt2TfM9wcwAG9ErkfE2alzFAb%2FyI2CveX5B62dTziY2gDwh6zb70mTysKzOe3uEZowO2UpHNsyJz5tkBYryPXJj%2BzbkWEIbRjOvjEBBtIMmNc5D%2B8Z1vAIRdSf6%2BT%2FU7k%2FvbFhH4EgKXXXmjJiaLhZt56VzgpRshENHr%2Bx1IjAthvwPMxkQxgay5PcJaecI6WcJqZlZsliWLsc7I2GaMpe8PPs46hIxD8WVCa1pWpDPBfJd017Lmnn5IHqCS9pgJL9NUexy%2Fq1Ifs2Goj1cU74GPfh50SDhZGpOFtkEB0yEoQC4Cfrfq4wim9vXHvIqEPoFDacGZZxapppm%2BMmy7WKHNHW%2FqODIdyqXPbgn%2F8p94n8AuQsxoucAD9Enp%2B%2Fy1U0%2FTkOZq8mVW31XDI%2FgJmVb4hqlC6FYLGKL2bk8YmmovgtPxGukuU3XAXoQuyNQucSOE%2FjzQUrW%2FZt%2FgdvCHq%2B93iPZLHEiy35FAYFDKhVpDtdpFV6ddjFG7KNIu2lXtoor9RslAstlvjnhrhrecKPUL5qo2JvSuMaE8svlZMKHawzGnfdBZprjilo3PgQRav0L6fG4SbH2GEQV9x2uiuTSvRXlkddQYDTXGrBONYRY%2FhSqNwRVW3zXG837lI%2FegMO7hDgRex6kY8xp%2Bb9IYxhhFGYjGsMw%2BaAxLDK7K1hgDiYp8P8%2FGbFFMWGT8ixEhl4XGPcjGhtErOgTMHUxxMnXxjv6k9KBgjztO9UrL1RhjHGUg%2BsXuZg1jFj%2BFMv0yxl0a4rM07pJzLpvGXZR7qdYwbM6CWpAQBNuDzfG68FMNUVLSaoYMe%2BRpSzw1tZZ4apYRXjZPnUoQ6Jynv0U4WUvuYBCDDf1x9P7wYYX5qpa1Zo61pizWzkbWtsRaqy3WWl2ztlL1VvesXYQRfmW0fbyHMeBfuokHWcoYy93xkbE3M9Zui7F2x4w1q0Ggc8b%2BCo8RmGewAdTaEqyWp7Y6nuojT1viqdMWT52ueWoMg6cLOiZKjali19dRR9BKux67F8aS7TsiB2nE%2BxBH7W4TbBCKdq4Q%2BDaJjOU0DVWm8lB0LwqAbcXlXuZAymkqpLpC7n51nNeypdUHm5V2iQ1%2FD9J67Xr6rEhPec58NZ0Wa7f1GlhTqZvaqefQn%2F1H4rZJWaCzxmKNgVgwR%2BuDBXMUF4Ra%2BjAs2MJDLtW6idMLfE9xlCBnpaTVg1qqqy%2BO5uKaUbhsSoarMI5r%2FY%2BMyC%2BmuEWm1uuu1aoFE59NLOGqnJcX9%2BkprgXja%2FURzZ8azaX9ub28aAadq%2F0VsUV8CkNXzBbV4Y5Pw5bSlKkmFqk1zb1qqjExkBBD1zt2zJktyElWXZM1kBqWTNAnrTVTHNyxHJE80oSiumzl06jOuo6GWNiglRwVcSwPLu5fYtpzd2uqx3OPoVqPz2sA9PBOFVTQiOTr5RxTKyNzXVQ%2F1cGTHUgTl%2F%2BSwWPX2SRaBh4eqjoHDx33Jf2KI7LFGxwA%2F%2BHUKiDo1OcbZrHuA8j%2BDwn5SI%2FqBXuCsxBsHXQC2otgmEjl2lTYFfFaiM3WjRiXTN89Cxi8Jo5eGOEQx0R1aZ3oVcx1WQIZSEVAADfY7VIk4npfXpGGPZYEtGUeDS1r1RpXURl6yUCSzSMHYzvm0R7NI5%2BKeb%2FMo6JQSByC4BZt%2FCvcIJbVjpI5hmu27J6yAvSCLV%2FJzZTaS53HlFqXkFMneVVKxPlIRD6ver%2BIqGg%2FyK1EfOB%2BKqMefdIIbtinNQqA3ytG5hIN7TGyjrtUxkgOw5GRd47ZK0ZyyfSdkZkT0JMdWsnxGoefBqYvHzCSZttUUtMWj6aWR802gzocjyM175x%2BBXUcRTGE271WF64OxwSHBTuxFDBP3OghkXkDWUicdt24yfn9agUyE4%2F5lSeQOsmRnuY8zvVS%2BPDjIwT77%2F9YLn%2F55%2FrB%2BeWH8fe7qmqpH1k%2BsUC6JMsnHlBQt79RUlBkih5zrXK6fLl3w0hX7rHlJYIKMaS6mvxGngwJ8bqIsBIE5w62r9nfqQPg3MOJqrgygIvLBFXhV9Ey5dZ8ytPeO5jdNSanDVIdFDXlMNZG2XmhYMYz%2FxqqmfIz1ZpSNXemmryKlUJIDCT3ybkK73ZANT8NZfwcs55t8dNoi5%2B5k%2FQU83MghcGcnzEMtoqrEkx%2BVKh0eo6H%2BLdFT1PLyqwxPU29ZCDJ9BzI%2FyTl9PRg7EboUuBdyYFpqsiqOtj0eclqtUVWq2Oy8vhQ39n6G%2FZUH9AhrkFbOXi%2BWAjjWQmyFqG5%2FwHRdBEq8Z9JFGNiIBGjZwoGIUPTwfpTIjfHAJGsBWhjbooLUOXcHEiEaLGivFPszYpLT4nMHENDstaejZkprj2VM3MgsaFH6LKDzLpdaEqk5hgWkrXSbExNcaWpnJqfoNSlJ5jIZdq4k3pzpk0cSHZWvM7%2BpRETtbI7TTGRy%2B6oxsTASn16jIlcSoF%2FvzmlIA4kGxP6iAlJ%2FkRjPZGLXKvWEw3PFSkezMiD5%2FPvIiieillFvLa%2Bi%2BCqZPpesp45dGoDgm0mXdHB%2Fp1WjpwqFok5LG3cpf6tXX4uSrHskKnZ1f5l5eHi6ZaND5kSH0NxGlNXVHRwq5Z4AW5%2FFEQbp8cU19QObFk3JAWhCTs6rLIDZsW9TNPr%2FXOV1zX716ru18REjlj60nl1P%2F0aYUbhU3eqLbZP2IOsx58%3D%3C%2Fdiagram%3E%3C%2Fmxfile%3E)

---
