# Audioguia Cultural SJC

Guia digital interativo e acessível para exposições culturais.

O Audioguia Cultural SJC é uma plataforma web para disponibilizar conteúdos de obras e exposições por meio de QR Codes. O sistema permite cadastrar exposições e obras e oferecer ao visitante conteúdo em **texto, áudio, audiodescrição e vídeo em Libras**, quando houver material apropriado e autorizado, além de um painel administrativo com métricas básicas de acesso.

O projeto é uma atividade acadêmico-extensionista do curso de Bacharelado em Ciência da Computação (Projeto de Extensão II), desenvolvida por Wellington Danilo Roveder.

## Aviso sobre o estágio do projeto

O MVP (versão mínima viável) está publicado **apenas para demonstração técnica**.

- A publicação não equivale à implantação em nenhuma instituição cultural, nem representa aprovação institucional, parceria formal ou autorização de uso de acervo.
- Todo o conteúdo da demonstração (exposição, obra, artista, textos e mídias) é **fictício**, criado para teste, e não representa acervo real de qualquer instituição.
- Cadastro de acervo real, publicação de materiais de terceiros e qualquer piloto dependem de análise, autorização e alinhamento prévio com a instituição envolvida.
- Este repositório não constitui parecer jurídico nem afirma conformidade legal integral.

## Demonstração

- Página pública de exemplo (obra demonstrativa fictícia): https://audioguia-cultural-sjc.vercel.app/obra/fb5232ca217d4d99afef967c0d204638
- Painel administrativo (tela de login): https://audioguia-cultural-sjc.vercel.app/admin/login — o acesso ao painel é liberado mediante solicitação.

## Objetivo

Desenvolver uma plataforma web complementar para acesso a informações de exposições e obras culturais por QR Code, oferecendo formatos textuais e recursos de mídia acessíveis, com gestão administrativa simples, sem substituir a curadoria, a mediação cultural ou os profissionais de uma instituição.

Cada obra possui um QR Code próprio. Ao escaneá-lo com o celular, o visitante é direcionado a uma página pública com as informações e os recursos de acessibilidade cadastrados para aquela obra.

## Escopo do MVP

### Incluído

#### Visitante

- Acesso às obras por QR Code ou endereço público;
- Página pública responsiva, sem necessidade de cadastro ou autenticação;
- Conteúdo textual sobre a obra;
- Reprodução de áudio;
- Audiodescrição;
- Vídeo com conteúdo em Libras;
- Tratamento de obras ou exposições indisponíveis.

#### Administração

- Autenticação de administradores;
- Cadastro e gerenciamento de exposições e obras;
- Ativação e desativação de exposições e obras;
- Upload de áudio, audiodescrição e vídeos em Libras;
- Geração e download de QR Code individual por obra;
- Visualização de métricas básicas de acesso por obra e exposição.

### Fora do escopo atual

- Substituição da mediação cultural, da curadoria, da sinalização física ou dos profissionais da instituição;
- Tradução automática para Libras (a plataforma apenas apresenta mídia fornecida e autorizada);
- Reconhecimento de obras por inteligência artificial, aplicativo nativo, sistema de venda ou plataforma comercial;
- Cadastro de acervo real ou publicação de imagens e materiais de instituições sem autorização;
- Garantia de acessibilidade integral sem auditoria específica com usuários e especialistas.

## Arquitetura

O projeto utiliza uma arquitetura web que separa frontend, API, banco de dados e armazenamento de arquivos.

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

A API concentra as regras de negócio, a autenticação, o gerenciamento das exposições e obras, a geração dos QR Codes, as métricas e a integração com o armazenamento de mídias.

O PostgreSQL armazena os dados estruturados da aplicação, enquanto os arquivos de áudio, audiodescrição e Libras são mantidos em armazenamento de objetos no Cloudflare R2.

## Stack

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

### Armazenamento

- Cloudflare R2;
- API compatível com S3.

### Infraestrutura

- Vercel — frontend;
- Heroku — API;
- Heroku Postgres — banco de dados;
- Cloudflare R2 — armazenamento de mídias;
- Docker — ambiente de desenvolvimento;
- GitHub Actions — integração contínua.

## Segurança

O MVP implementa camadas de proteção para o painel administrativo e para a API, entre elas:

- Senhas armazenadas com hash seguro;
- Autenticação baseada em JWT, com tokens de tempo de expiração;
- Cookies `HttpOnly`, `Secure` e `SameSite`;
- Separação entre rotas públicas e administrativas, com autorização das rotas administrativas no backend;
- Limitação de tentativas (rate limiting) no login administrativo;
- CORS configurado por ambiente;
- HTTPS, HSTS e cabeçalhos de segurança;
- Validação de tipo e tamanho dos arquivos enviados;
- Segredos e credenciais mantidos em variáveis de ambiente.

## Privacidade e uso responsável

- As páginas públicas não exigem cadastro de visitantes.
- As métricas foram concebidas para contagem agregada de acessos, não para identificar pessoas. O desenho do domínio de métricas não prevê armazenar IP, user-agent, fingerprint, geolocalização ou login do visitante.
- A configuração exata da hospedagem, os logs operacionais e a retenção de dados deverão ser revisados antes de qualquer uso institucional.
- O tratamento de dados eventualmente inseridos por administradores, os responsáveis, os prazos de retenção e os procedimentos de correção ou exclusão deverão ser alinhados com a instituição antes de qualquer piloto.
- Áudios, imagens e vídeos somente devem ser publicados quando houver direito ou autorização para o seu uso.

## Testes e qualidade

O projeto possui uma suíte automatizada com **126 testes**, cobrindo componentes importantes do backend e suas regras de negócio. Esse número é um indicador de verificação técnica do software; não representa avaliação de usabilidade com visitantes nem evidência de impacto cultural.

Também foram realizados testes manuais e smoke tests no ambiente publicado, incluindo:

- Autenticação administrativa e persistência da sessão;
- Cadastro de exposições e obras;
- Upload e reprodução de mídias, com armazenamento no Cloudflare R2;
- Geração e leitura de QR Codes;
- Acesso público por dispositivos móveis, inclusive em um dispositivo móvel real, a partir do QR Code gerado pela aplicação;
- Registro de métricas;
- Exposições e obras inativas e recursos inexistentes;
- Health check da API;
- Rate limiting do login.

## Fluxo principal

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

## Estrutura do projeto

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
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Configuração

A aplicação utiliza variáveis de ambiente para configurações e credenciais. O repositório contém um arquivo de exemplo (`.env.example`) que documenta as variáveis necessárias sem versionar informações sensíveis.

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

## Publicação para demonstração

O MVP está publicado em ambiente web para demonstração técnica:

- Frontend: Vercel;
- Backend: Heroku;
- Banco de dados: Heroku Postgres;
- Armazenamento de mídias: Cloudflare R2.

As migrations do banco de dados são controladas pelo Alembic.

## Métricas

Cada acesso público a uma obra pode ser registrado pela aplicação, para fins de contagem agregada. O painel administrativo permite acompanhar:

- Total de acessos por exposição;
- Número de acessos por obra.

## Acessibilidade

A acessibilidade é parte central da proposta. Uma obra pode disponibilizar diferentes formas de consumo do conteúdo: texto, áudio, audiodescrição e Libras.

Os recursos são independentes, de modo que a página continua disponível mesmo quando determinada mídia não está cadastrada.

A existência desses recursos, isoladamente, não comprova acessibilidade plena nem impacto: são necessárias validação e avaliação com os públicos envolvidos.

## Contexto extensionista

O projeto é desenvolvido no âmbito do Projeto de Extensão II do curso de Bacharelado em Ciência da Computação, com base na metodologia **PDCA (Plan, Do, Check, Act)**.

- **Plan e Do:** planejamento, desenvolvimento do MVP e testes técnicos, concluídos.
- **Check e Act:** a verificação junto a uma instituição e a avaliação com usuários dependem de autorização, agendamento e feedback documentado. Nenhum resultado de uso real, impacto social mensurado ou aprovação institucional é afirmado neste repositório.

## Status

**MVP funcional, publicado para demonstração técnica.**

Eventuais próximos passos (análise institucional, definição de piloto, seleção de conteúdos autorizados e avaliação de acessibilidade, privacidade e direitos de uso) dependem de diálogo e autorização da instituição envolvida.

## Possíveis evoluções

- Domínio próprio;
- Ampliação das métricas;
- Melhorias de observabilidade;
- Validação mais profunda do conteúdo dos arquivos enviados;
- Evolução dos recursos administrativos;
- Melhorias baseadas em feedback, se e quando houver avaliação autorizada.

## Autor

**Wellington Danilo Roveder**
Bacharelado em Ciência da Computação — Centro Universitário Anhanguera Pitágoras Ampli
Projeto de Extensão II — Programa de Ação e Difusão Cultural
