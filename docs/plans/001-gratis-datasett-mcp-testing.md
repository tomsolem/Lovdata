# Plan: Gratis Lovdata-datasett for MCP-testing

**Created:** 2026-04-29

## Overview

Målet er å bruke de gratis Lovdata-datasettene (lover, sentrale forskrifter og Lovtidend) til deterministisk testing av MCP-serveren uten autentisering. Planen følger prosjektets Copilot-instrukser for struktur, Go-praksis og MCP-konvensjoner.

## Steps

- [ ] Step 1 - Opprett feature-branch for arbeidet, og referer denne planen i PR-beskrivelsen.
- [ ] Step 2 - Etabler datasett-inntak under testdata/ med nedlastingsscript, utpakking og checksum for snapshot-versjonering.
- [ ] Step 3 - Implementer typed klientmetoder i internal/lovdata/client.go for gratis endepunkter, med context.Context i alle I/O-kall.
- [ ] Step 4 - Implementer robust HTTP-feilhåndtering med eksponentiell backoff ved 429, timeout-håndtering og eksplisitt error-return.
- [ ] Step 5 - Implementer/utvid MCP-tools som egne filer under internal/tools/, med navn lovdata_<action> og korte engelske beskrivelser.
- [ ] Step 6 - Registrer alle nye MCP-tools i cmd/server/main.go.
- [ ] Step 7 - Definer flate request/response-schema med encoding/json-tags og stabile feltnavn for kontraktstesting.
- [ ] Step 8 - Legg til tabell-drevne enhetstester for parsing, validering, mapping og feilscenarier.
- [ ] Step 9 - Legg til integrasjonstester mot lokale snapshots slik at CI kan kjøre uten ekstern nettavhengighet.
- [ ] Step 10 - Legg til E2E-røyktest som starter serveren og verifiserer minst én komplett MCP-flyt mot gratis data.
- [ ] Step 11 - Legg inn sikkerhetskontroller i tester/kode for å sikre at LOVDATA_API_TOKEN aldri logges eller eksponeres.
- [ ] Step 12 - Dokumenter datasettkilder, NLOD 2.0-lisens og rutine for oppdatering av snapshots.

## Status (2026-04-29)

- Ferdig nå:
	- Opprettet testdatastruktur under testdata/lovdata med laws/, regulations/ og lovtidend/.
	- Lagt inn representativt lovutvalg i laws/ basert på nedlastede filer i unzipped/nl.
	- Lagt til .gitignore for unzipped/.
	- Dokumentert utvalg og forslag i testdata/lovdata/SELECTION.md.
- Delvis ferdig:
	- Step 2: Struktur, utpakking og eksempeldata er på plass; checksum/snapshot-rutine gjenstår.
	- Step 12: Datakilde-URL og lisensreferanse er dokumentert i planen; konkret, operasjonell oppdateringsrutine gjenstår.
- Neste anbefalte handling:
	- Legg til checksums.txt for utvalgsfilene og marker Step 2 som fullført.

## Detailed Scope

### Datasett som skal brukes

- Norsk Lovtidend avd. 1 (Data.norge.no), lisensiert under NLOD 2.0.
- Gjeldende lover via gratis Lovdata-endepunkt.
- Sentrale forskrifter via gratis Lovdata-endepunkt.
- Kilde for gratis data: https://api.lovdata.no/publicData

### Prinsipper for bruk av data

- Gratis datasett er baseline for funksjonell testing i utvikling og CI.
- Token-baserte kall holdes separat, slik at baseline ikke blokkeres av autentisering.
- Snapshot-baserte tester skal være deterministiske og reproduserbare.

### Norsk Lovtidend, Avdeling I dataserie

- Dataserien inneholder kunngjøringer fra Norsk Lovtidend, Avdeling I.
- Dette utgjør offisielle kunngjøringer av grunnlovsbestemmelser, lover, landsdekkende forskrifter, ikrafttredelses- og delegeringsvedtak, skatte-, avgifts- og tollvedtak m.m.
- Dataserien er komplett fra 1. januar 2001 til dags dato og består av to datasett:
	- Komplett samling fra 1. januar 2001 til inneværende år.
	- Komplett samling fra 1. januar inneværende år til dags dato, oppdatert daglig.
- Norsk Lovtidend utgis av Lovdata på vegne av Justis- og beredskapsdepartementet.
- Avdeling I dekker regelverk for hele landet, mens Avdeling II dekker regionale og lokale forskrifter.

### Autoritativitet og tolkning

- Norge har ikke offisielle ajourførte versjoner av regelverk.
- Den juridisk autoritative kilden er Norsk Lovtidend (kunngjort original + endringsvedtak).
- Lovdatas konsoliderte versjoner er praktisk nyttige, men er ikke offisiell versjon av loven.
- Dette skal reflekteres i MCP-svar ved at kildegrunnlag og status (offisiell vs. konsolidert) fremgår tydelig.

### Dokumentstruktur og teknisk format

- Hvert dokument er delt i hode og kropp, med strukturkoder med id-ene hode og dokument.
- Hodet inneholder metadata, kroppen inneholder dokumenttekst.
- Dokumentene er strukturert som XML, men skal kunne tolkes som HTML.
- Strukturkoder bor valideres mot Lovdata XML-dokumentasjon i parser- og mapping-lag.

### Klassifisering og heuristikk

- Lover kan skilles fra forskrifter og andre dokumenter via filnavn: prefiks nl indikerer lover.
- Kunngjøringer skiller ikke alltid eksplisitt mellom nytt regelverk og senere endringer.
- Endringsdokumenter kan ofte utledes heuristisk fra tittelmønster, for eksempel:
	- Lov om endring i lov om ...
	- Forskrift om endring i lov om ...
	- Forskrift om endring i flere forskrifter ...

### Testimplikasjoner fra Lovtidend-beskrivelsen

- Lag testsett som eksplisitt dekker:
	- Nye kunngjøringer.
	- Endringskunngjøringer.
	- Tvetydige titler der heuristikk kan feile.
- Verifiser at parseren leser hode og dokument korrekt og robust ved manglende felt.
- Verifiser klassifisering basert på filnavnsprefiks nl.
- Dokumenter i testresultater hva som er offisiell kilde (Lovtidend) og hva som er konsolidert visning.

## Test Strategy

### Testnivåer

- Enhetstester:
	- Parsing, mapping og validering av metadata/innhold.
	- Feilhåndtering ved manglende felter, tomme svar og ugyldig format.
- Integrasjonstester:
	- Kjøring mot lokale snapshots av gratis datasett.
	- Verifisering av at MCP-tools returnerer gyldig JSON med stabile felt.
- Kontraktstester:
	- Stabil input/output for hvert MCP-tool.
	- Varsling ved breaking changes i dataformat eller feltstruktur.
- E2E-tester:
	- Oppstart av server og verifisering av minst én komplett MCP-flyt.

### Scenarier som må dekkes

- Normalflyt:
	- Hente dokument med gyldig ID.
	- Søke/liste dokumenter fra kjent snapshot.
- Edge cases:
	- Ugyldig ID.
	- Dokument uten forventede felter.
	- Tomt resultatsett.
- Robusthet:
	- HTTP 429 med eksponentiell backoff og begrenset antall forsøk.
	- Nettverksfeil/timeouts med tydelige, eksplisitte feil.
- Ytelse:
	- Sekvensielle oppslag over utvalgte dokumentsett.
	- Måling av responstid per tool og total svartid.

## Implementation Details

### Fase 1 - Datasettinntak

- Etabler struktur under testdata/lovdata:
	- laws/
	- regulations/
	- lovtidend/
- Bruk nedlastingsscript for henting og utpakking.
- Lag checksum-fil for versjonering av snapshots brukt i tester.

### Fase 2 - Klientstøtte

- Utvid internal/lovdata/client.go med typed metoder for gratis endepunkter.
- Bruk context.Context konsekvent i alle I/O-kall.
- Returner feil eksplisitt, uten panic i bibliotekkode.
- Implementer retry/backoff ved 429 med jitter.

### Fase 3 - MCP-tools

- Ett tool per fil under internal/tools/.
- Toolnavn følger lovdata_<action>.
- Korte engelske beskrivelser for AI-assistenter.
- Flate request/response-schema med encoding/json-tags.
- Registrering av alle nye tools i cmd/server/main.go.

### Fase 4 - Testautomatisering

- Tabell-drevne enhetstester med standard testing-pakke.
- Integrasjonstester mot lokale snapshots som standard i CI.
- E2E-røyktest for hel MCP-flyt.
- Baseline-pipeline med go test ./... og valgfri separat jobb for tyngre E2E.

## Recommended Test Matrix

- Valid input gir forventet struktur og obligatoriske felter.
- Invalid input gir tydelig valideringsfeil.
- Ikke-eksisterende ressurs gir kontrollert feilrespons.
- Midlertidige feil (429/5xx) håndteres med retry der relevant.
- Svar kan serialiseres/deserialiseres stabilt.

## Data Governance And License

- Dokumenter alle datakilder og URL-er i repo-dokumentasjon.
- Referer eksplisitt til NLOD 2.0 der datasettene beskrives.
- Unngå store råfiler i repo når mulig:
	- Bruk komprimerte snapshots.
	- Bruk delmengde for raske CI-kjøringer.
	- Kjør full datasettvalidering periodisk eller manuelt.

## Definition Of Done

- Baseline-tester passerer uten API-token.
- MCP-tools for gratis data returnerer stabilt schema.
- 429/timeout håndteres kontrollert og testet.
- CI kjører deterministisk testpakke på snapshot-data.
- Dokumentasjon beskriver oppdateringsrutine for snapshots.
