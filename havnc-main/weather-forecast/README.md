# Weather Forecast Add-on

Aquest add-on exposa la predicció del temps de Meteocat per al municipi que defineixis. L'add-on actua com un petit servei HTTP dins de Home Assistant i retorna la informació en JSON perquè la puguis reutilitzar a dashboards, automatitzacions o sensors REST.

## Descripció

- **Font oficial**: consumeix les dades del Servei Meteorològic de Catalunya (Meteocat).
- **Configuració flexible**: pots indicar el municipi pel nom o pel codi oficial.
- **Integració senzilla**: ofereix un endpoint `/forecast` amb la resposta completa de Meteocat.

## Instal·lació

1. Copia la carpeta `weather-forecast` dins del directori `addons/` del teu Home Assistant (o del repositori local d'add-ons).
2. A Home Assistant, ves a **Settings → Add-ons → Add-on Store**.
3. Fes clic a **Refresh** per carregar el nou add-on.
4. Cerca **Weather Forecast** i prem **Install**.

## Configuració

1. A la pantalla de l'add-on, obre la pestanya **Configuration**.
2. Introdueix el nom del municipi o el seu codi i la clau d'API de Meteocat.
3. Desa els canvis i prem **Start** per iniciar l'add-on.

## Configuració

Opcions disponibles a `config.yaml`:

- `municipality`: nom de la població (p. ex. `Barcelona`).
- `municipality_code`: codi del municipi si ja el coneixes (opcional).
- `api_key`: clau d'API de Meteocat (obligatòria).
- `base_url`: URL base de l'API de Meteocat (`https://api.meteo.cat/recursos/v1` per defecte).

## Endpoint

- `GET /forecast`: retorna la predicció en format JSON.
- `GET /health`: retorna `{ "status": "ok" }`.

## Exemple de sensor REST a Home Assistant

```yaml
sensor:
  - platform: rest
    name: "Prediccio Temps"
    resource: http://<IP_DEL_SUPERVISOR>:8099/forecast
    value_template: "{{ value_json.forecast.prediccio[0].variables[0].valors[0].valor }}"
    json_attributes:
      - forecast
      - municipality
    scan_interval: 1800
```
