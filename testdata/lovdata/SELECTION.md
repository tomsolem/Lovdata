# Lovdata test selection

Dette er et anbefalt minimumsutvalg fra nedlastet `unzipped/nl` for gode MCP-tester.

## Inkludert i repo

- `laws/nl-2025-04-25-12.xml`
  - Komplett lovstruktur med mange kapitler/paragrafer.
  - Egnet for parsing av hode/dokument, innholdslister og lenker.
- `laws/nl-2026-03-06-7.xml`
  - Kort endringslov med tydelige dokumentendringer.
  - Egnet for tester av endringsmønstre.
- `laws/nl-2023-12-20-107.xml`
  - Endringslov med flere deler (I-IV) og ikrafttredelsesnoter.
  - Egnet for tester av fotnoter og fler-delte dokumenter.

## Foreslått neste utvidelse (ikke kopiert ennå)

- Flere `nl-*` fra ulike år for å dekke variasjon i metadata og struktur.
- Et `-nn` dokument for språkvariant-testing.
- Eget utvalg for "endring i lov om ..." titler for heuristikk.

## Kilde

- https://api.lovdata.no/publicData
