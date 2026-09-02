# Modelo de Domínio — Audioguia Cultural SJC

## 1. Objetivo

Este documento descreve o modelo de domínio inicial do MVP do Audioguia
Cultural SJC.

O projeto tem como objetivo apoiar a experiência de visitantes em exposições
culturais por meio de páginas digitais acessadas por QR Code, disponibilizando
conteúdo textual e recursos multimídia e de acessibilidade relacionados às
obras.

O modelo descrito neste documento representa o escopo atualmente definido
para o MVP e poderá evoluir conforme as etapas de validação do projeto.

---

## 2. Entidades do domínio

O domínio inicial é composto pelas seguintes entidades:

- Exhibition
- Work
- AccessEvent

Relacionamento principal:

    Exhibition
        |
        | 1:N
        v
       Work
        |
        | 1:N
        v
    AccessEvent

Uma exposição pode possuir várias obras.

Cada obra pertence a uma exposição e possui sua própria página pública,
acessível por meio de um QR Code individual.

Uma obra pode possuir vários registros de acesso.

---

## 3. Exhibition

Representa uma exposição cultural cadastrada no sistema.

### Campos

- `id`
- `title`
- `description`
- `start_date`
- `end_date`
- `is_active`
- `created_at`
- `updated_at`

### Responsabilidades

A entidade é responsável por representar e organizar uma exposição dentro
da plataforma.

As obras cadastradas são associadas a uma exposição.

---

## 4. Work

Representa uma obra ou item cultural pertencente a uma exposição.

### Campos

- `id`
- `exhibition_id`
- `title`
- `artist` (opcional)
- `description`
- `audio_url` (opcional)
- `audio_description_url` (opcional)
- `libras_video_url` (opcional)
- `public_slug`
- `is_active`
- `created_at`
- `updated_at`

### Responsabilidades

Cada obra possui uma página pública própria.

O campo `public_slug` identifica a URL pública da obra e permite que o QR Code
continue apontando para o mesmo endereço mesmo quando outros dados da obra
forem alterados.

O campo `artist` é opcional para permitir diferentes formatos de exposição,
incluindo exposições coletivas e exposições dedicadas a um único artista.

Os recursos de áudio, audiodescrição e vídeo em Libras são opcionais no modelo
e podem ser associados à obra conforme o conteúdo disponível.

O sistema disponibiliza o conteúdo em Libras associado à obra, mas não realiza
automaticamente tradução ou geração de conteúdo em Libras.

---

## 5. AccessEvent

Representa um acesso contabilizado a uma obra.

### Campos

- `id`
- `work_id`
- `accessed_at`

### Responsabilidades

Permitir a geração de métricas de acesso por obra e, por agregação, por
exposição e período.

O registro não armazena identificadores do visitante.

Não fazem parte da entidade:

- endereço IP;
- user-agent;
- identificador de dispositivo;
- fingerprint;
- localização;
- dados pessoais do visitante.

---

## 6. Contabilização de acessos

Para o MVP, um acesso representa o primeiro acesso estimado de um
navegador/dispositivo a uma determinada obra.

A deduplicação será realizada localmente no navegador.

Após um primeiro acesso contabilizado, o navegador armazenará localmente a
informação de que aquela obra já foi acessada e evitará o envio de novos
registros para a mesma obra.

O backend receberá somente a informação necessária para registrar o acesso
à obra.

Essa estratégia evita a criação de mecanismos de identificação ou
fingerprinting de visitantes apenas para geração de métricas.

### Limitações

A métrica não representa visitantes únicos absolutos.

Um mesmo visitante poderá ser contabilizado novamente caso, por exemplo:

- utilize outro dispositivo;
- utilize outro navegador;
- limpe os dados armazenados localmente;
- utilize mecanismos que não preservem o armazenamento local.

Por esse motivo, os resultados deverão ser apresentados como
**acessos únicos estimados por navegador/dispositivo**, e não como quantidade
exata de visitantes.

---

## 7. QR Code e acesso público

Cada obra possuirá um QR Code individual associado à sua URL pública.

O QR Code poderá ser utilizado em diferentes meios, incluindo:

- material impresso;
- espaço expositivo;
- telas digitais;
- materiais de divulgação.

O acesso ao conteúdo público de uma obra não exigirá autenticação do visitante.

O QR Code funciona como meio de acesso ao conteúdo da obra e não depende de
estar fisicamente posicionado ao lado dela.

---

## 8. Fora do escopo atual

Não fazem parte do modelo de domínio do MVP neste momento:

- cadastro independente de artistas;
- contas de visitantes;
- identificação ou rastreamento individual de visitantes;
- geolocalização;
- reconhecimento de obras por inteligência artificial;
- geração automática de Libras;
- sistema geral de divulgação de eventos;
- funcionalidades comerciais ou de SaaS.

Esses elementos somente deverão ser considerados futuramente caso exista uma
necessidade validada que justifique sua inclusão.