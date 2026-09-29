# Audioguia Cultural SJC

Plataforma web para disponibilização de conteúdos culturais acessíveis por meio de QR Codes.

O sistema permite que instituições culturais cadastrem exposições e obras, disponibilizando ao visitante conteúdos em **texto, áudio, audiodescrição e Libras**, além de fornecer um painel administrativo com métricas de acesso.

O projeto foi desenvolvido inicialmente como uma atividade extensionista do curso de Ciência da Computação, tendo como contexto de aplicação a **Casa de Cultura Chico Triste, em São José dos Campos - SP**.

## 🎯 Objetivo

Desenvolver uma solução tecnológica que facilite o acesso do público aos conteúdos de exposições culturais, proporcionando uma experiência simples, rápida, responsiva e acessível.

Cada obra possui um QR Code próprio. Ao escaneá-lo com o celular, o visitante é direcionado para uma página pública contendo as informações e os recursos de acessibilidade cadastrados para aquela obra.

## ✨ Funcionalidades

### Visitante

- Acesso às obras por QR Code;
- Página pública responsiva;
- Conteúdo textual sobre a obra;
- Reprodução de áudio;
- Audiodescrição;
- Vídeo com conteúdo em Libras;
- Tratamento de obras ou exposições indisponíveis;
- Acesso sem necessidade de cadastro ou autenticação.

### Administração

- Autenticação de administradores;
- Cadastro e gerenciamento de exposições;
- Cadastro e gerenciamento de obras;
- Ativação e desativação de exposições e obras;
- Upload de áudio, audiodescrição e vídeos em Libras;
- Geração de QR Code individual por obra;
- Download do QR Code;
- Visualização de métricas de acesso;
- Métricas agrupadas por obra.

## 🏗️ Arquitetura

O projeto utiliza uma arquitetura web separando frontend, API, banco de dados e armazenamento de arquivos.

```text
                         ┌──────────────────┐
                         │    Visitante     │
                         │      QR Code     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Next.js      │
                         │      Vercel      │
                         └────────┬─────────┘
                                  │
                              HTTPS / API
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │      Heroku      │
                         └───────┬──┬───────┘
                                 │  │
                       ┌─────────┘  └──────────┐
                       ▼                       ▼
              ┌────────────────┐      ┌────────────────┐
              │   PostgreSQL   │      │ Cloudflare R2  │
              │     Heroku     │      │     Storage    │
              └────────────────┘      └────────────────┘
```

O frontend é responsável pela experiência pública e pelo painel administrativo.

A API concentra as regras de negócio, autenticação, gerenciamento das exposições e obras, geração dos QR Codes, métricas e integração com o armazenamento de mídias.

O PostgreSQL armazena os dados estruturados da aplicação, enquanto arquivos de áudio, audiodescrição e Libras são mantidos em object storage no Cloudflare R2.

## 🛠️ Stack

### Backend

- Python;
- FastAPI;
- SQLAlchemy;
- Pydantic;
- PostgreSQL;
- Asyncpg;
- Alembic;
- Pytest.

### Frontend

- Next.js;
- React;
- TypeScript;
- Tailwind CSS.

### Storage

- Cloudflare R2;
- API compatível com S3.

### Infraestrutura

- Vercel — frontend;
- Heroku — API;
- Heroku Postgres — banco de dados;
- Cloudflare R2 — armazenamento de mídias;
- Docker — ambiente de desenvolvimento;
- GitHub Actions — integração contínua.

## 🔐 Segurança

O MVP implementa diferentes camadas de proteção para o painel administrativo e para a API.

Entre elas:

- Senhas armazenadas utilizando hash seguro;
- Autenticação baseada em JWT;
- Tokens com tempo de expiração;
- Cookies `HttpOnly`, `Secure` e `SameSite`;
- Separação entre rotas públicas e administrativas;
- Autorização das rotas administrativas no backend;
- Rate limiting no endpoint de login;
- CORS configurado por ambiente;
- HTTPS;
- HSTS;
- Security Headers;
- Validação de tipo e tamanho dos arquivos enviados;
- Segredos e credenciais mantidos em variáveis de ambiente.

O login administrativo possui limitação de requisições na camada de borda, reduzindo tentativas automatizadas de autenticação.

## 🧪 Testes e qualidade

O projeto possui uma suíte automatizada com **126 testes**, cobrindo componentes importantes do backend e suas regras de negócio.

Também foram realizados testes manuais e smoke tests no ambiente de produção, incluindo:

- Autenticação administrativa;
- Persistência da sessão;
- Cadastro de exposições;
- Cadastro de obras;
- Upload e reprodução de mídias;
- Armazenamento no Cloudflare R2;
- Geração e leitura de QR Codes;
- Acesso público por dispositivos móveis;
- Registro de métricas;
- Exposições e obras inativas;
- Recursos inexistentes;
- Health check da API;
- Rate limiting do login.

O fluxo completo também foi validado utilizando um dispositivo móvel real através do QR Code gerado pela aplicação.

## 🔄 Fluxo principal

```text
Administrador
      │
      ├── cria exposição
      │
      ├── cadastra obra
      │
      ├── adiciona recursos de acessibilidade
      │
      └── gera QR Code
                │
                ▼
            Visitante
                │
          escaneia QR Code
                │
                ▼
          Página da obra
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
      Áudio   Audiodesc. Libras
                │
                ▼
         Registro de acesso
                │
                ▼
       Métricas administrativas
```

## 📂 Estrutura do projeto

```text
audioguia-cultural-sjc/
│
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/
│   ├── app/
│   ├── public/
│   └── package.json
│
└── README.md
```

## ⚙️ Configuração

A aplicação utiliza variáveis de ambiente para configurações e credenciais.

O repositório contém arquivos de exemplo para documentar as variáveis necessárias sem versionar informações sensíveis.

Entre as configurações utilizadas estão:

```text
DATABASE_URL
SECRET_KEY
PUBLIC_FRONTEND_URL
CORS_ORIGINS

STORAGE_ENDPOINT_URL
STORAGE_ACCESS_KEY_ID
STORAGE_SECRET_ACCESS_KEY
STORAGE_BUCKET_NAME
```

Credenciais reais não devem ser adicionadas ao repositório.

## 🚀 Deploy

O MVP encontra-se implantado em ambiente de produção.

### Frontend

Vercel

### Backend

Heroku

### Banco de dados

Heroku Postgres

### Armazenamento

Cloudflare R2

As migrations do banco de dados são controladas através do Alembic.

## 📈 Métricas

Cada acesso público a uma obra pode ser registrado pela aplicação.

O painel administrativo permite acompanhar:

- Total de acessos da exposição;
- Número de acessos por obra.

Essas informações permitem avaliar a utilização dos conteúdos pelos visitantes.

## ♿ Acessibilidade

A acessibilidade é parte central da proposta.

Uma obra pode disponibilizar diferentes formas de consumo do conteúdo:

- Texto;
- Áudio;
- Audiodescrição;
- Libras.

Os recursos são independentes, permitindo que a página continue disponível mesmo quando determinada mídia não estiver cadastrada.

## 📚 Contexto extensionista

O projeto surgiu como uma atividade extensionista do curso de **Ciência da Computação**, utilizando a metodologia **PDCA (Plan, Do, Check, Act)** durante seu desenvolvimento.

A proposta busca aproximar tecnologia, cultura e comunidade através de uma solução que possa ser utilizada em espaços culturais para ampliar as formas de acesso às informações das exposições.

## 📌 Status

**MVP concluído e implantado.**

A versão atual passou por testes automatizados, testes de integração, validação em ambiente de produção e testes reais de acesso por dispositivo móvel.

Novas funcionalidades serão avaliadas a partir de feedback e de necessidades identificadas durante a utilização da solução.

## 🗺️ Possíveis evoluções

- Domínio próprio;
- Ampliação das métricas;
- Melhorias de observabilidade;
- Validação mais profunda do conteúdo dos arquivos enviados;
- Evolução dos recursos administrativos;
- Melhorias baseadas no feedback das instituições culturais.

## 👨‍💻 Autor

**Wellington Danilo Roveder**

Projeto desenvolvido como parte da formação em Ciência da Computação e como aplicação prática de desenvolvimento backend, APIs REST, aplicações web, bancos de dados, testes, segurança e deploy em ambiente de produção.