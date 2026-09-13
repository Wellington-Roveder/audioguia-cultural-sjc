# Modelo Relacional — Audioguia Cultural SJC

## 1. Objetivo

Este documento descreve o modelo relacional inicial do MVP do Audioguia
Cultural SJC.

O modelo foi derivado do domínio definido para o projeto e contempla as
entidades:

- `exhibitions`
- `works`
- `access_events`

O objetivo é estabelecer tipos, relacionamentos, constraints e índices antes
da implementação dos modelos SQLAlchemy e das migrations do banco de dados.

---

## 2. Política de identificadores

As entidades do domínio utilizarão UUID como chave primária.

Entidades:

- `exhibitions.id`
- `works.id`
- `access_events.id`

Os UUIDs serão gerados pela aplicação.

As chaves estrangeiras utilizarão o mesmo tipo UUID.

---

## 3. Política de data e hora

Datas que representam apenas um dia, sem horário, utilizarão `DATE`.

Exemplos:

- `start_date`
- `end_date`

Eventos temporais utilizarão `TIMESTAMPTZ`.

Exemplos:

- `created_at`
- `updated_at`
- `accessed_at`

A aplicação utilizará UTC como referência para persistência e comunicação
entre backend e banco de dados.

Os valores apresentados ao usuário poderão ser convertidos para o fuso:

`America/Sao_Paulo`

O backend deverá trabalhar com objetos `datetime` timezone-aware, evitando
datas e horários sem informação de timezone.

---

## 4. Tabela `exhibitions`

Representa uma exposição cultural.

| Campo | Tipo | Regras |
|---|---|---|
| `id` | UUID | PRIMARY KEY |
| `title` | VARCHAR(150) | NOT NULL |
| `description` | TEXT | NOT NULL |
| `start_date` | DATE | NULL |
| `end_date` | DATE | NULL |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

### Constraints

O título não pode ser vazio ou composto somente por espaços:

    CHECK (length(trim(title)) > 0)

A descrição não pode ser vazia ou composta somente por espaços:

    CHECK (length(trim(description)) > 0)

Quando as duas datas forem informadas, a data final não poderá ser anterior
à data inicial:

    CHECK (
        end_date IS NULL
        OR start_date IS NULL
        OR end_date >= start_date
    )

O título não possui constraint `UNIQUE`, pois exposições diferentes poderão
utilizar o mesmo título em períodos distintos.

### Índices

- índice da chave primária `id`;
- índice em `is_active`.

---

## 5. Tabela `works`

Representa uma obra ou item cultural pertencente a uma exposição.

| Campo | Tipo | Regras |
|---|---|---|
| `id` | UUID | PRIMARY KEY |
| `exhibition_id` | UUID | NOT NULL, FOREIGN KEY |
| `title` | VARCHAR(150) | NOT NULL |
| `artist` | VARCHAR(150) | NULL |
| `description` | TEXT | NOT NULL |
| `audio_url` | TEXT | NULL |
| `audio_description_url` | TEXT | NULL |
| `libras_video_url` | TEXT | NULL |
| `public_slug` | VARCHAR(180) | NOT NULL, UNIQUE |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

### Relacionamento

    works.exhibition_id -> exhibitions.id

Uma exposição pode possuir várias obras.

A remoção de uma exposição que ainda possua obras associadas deverá ser
impedida.

Estratégia:

    ON DELETE RESTRICT

A desativação de conteúdo deverá ser preferida à exclusão quando for
necessário preservar histórico.

### Constraints

    CHECK (length(trim(title)) > 0)

    CHECK (length(trim(description)) > 0)

    CHECK (length(trim(public_slug)) > 0)

O campo `artist` é opcional.

Os campos de mídia também são opcionais:

- `audio_url`
- `audio_description_url`
- `libras_video_url`

O `public_slug` deverá ser único no sistema.

### Índices

- índice da chave primária `id`;
- índice da foreign key `exhibition_id`;
- índice em `is_active`;
- índice criado pela constraint `UNIQUE` de `public_slug`.

---

## 6. Tabela `access_events`

Representa um acesso contabilizado a uma obra.

| Campo | Tipo | Regras |
|---|---|---|
| `id` | UUID | PRIMARY KEY |
| `work_id` | UUID | NOT NULL, FOREIGN KEY |
| `accessed_at` | TIMESTAMPTZ | NOT NULL |

### Relacionamento

    access_events.work_id -> works.id

Uma obra pode possuir vários registros de acesso.

A remoção de uma obra que possua métricas associadas deverá ser impedida.

Estratégia:

    ON DELETE RESTRICT

### Privacidade

A tabela não deverá armazenar:

- endereço IP;
- user-agent;
- identificador de dispositivo;
- fingerprint;
- localização;
- dados pessoais do visitante.

A deduplicação dos acessos será realizada localmente no navegador, conforme
definido no modelo de domínio.

Consequentemente, a tabela não possui constraint de unicidade relacionada
ao visitante.

### Índices

Índice composto:

    INDEX (work_id, accessed_at)

Esse índice atende consultas de acessos de determinada obra ao longo de um
período.

Índice adicional:

    INDEX (accessed_at)

Esse índice atende consultas e agregações globais por período.

---

## 7. Relacionamentos

O modelo relacional principal é:

    exhibitions
        |
        | 1:N
        v
      works
        |
        | 1:N
        v
    access_events

As relações utilizam foreign keys e `ON DELETE RESTRICT` para evitar exclusões
acidentais de dados relacionados.

---

## 8. Decisões de escopo

O modelo não inclui, neste momento:

- tabela de artistas;
- tabela de visitantes;
- sessões de visitantes;
- identificação de dispositivos;
- geolocalização;
- tabela de métricas agregadas;
- recursos de inteligência artificial.

As métricas serão calculadas a partir dos registros de `access_events`.

Novas estruturas somente deverão ser adicionadas quando existir requisito
que justifique sua inclusão.