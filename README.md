# National Grid: Live

This repository contains the source code for [National Grid: Live](https://grid.iamkate.com/).

## Development

The development environment uses [Docker](https://www.docker.com/).

Copy `.env.example` to `.env` and edit the values as appropriate. At a minimum, `DATABASE_PASSWORD` must be given a value.

To start the containers:

```
docker compose up --detach
```

Once the containers are running, you can view the site at [http://localhost:9714/](http://localhost:9714/). Port 9714 was chosen due to its slight resemblance to the word ‘grid’.

To run the update script:

```
docker compose exec python-updater python /var/grid/update.py
```

To stop the containers:

```
docker compose down
```

## Production

The production environment does not use Docker, instead running directly on the server. Python 3.12 and a recent version MariaDB or MySQL are required.

### Files

Copy `.env.example` to `.env` and edit the values as appropriate. At a minimum, `DATABASE_PASSWORD` must be given a value. `DATABASE_HOSTNAME` should be changed to `localhost` if the database is running on the same server.

Upload `.env`, `update.py`, and the `grid` directory to the server.

### Database

Create a database and a user with `SELECT`, `INSERT`, `UPDATE`, and `DELETE` privileges, and import `grid.sql` into the database.

### Web server

Configure the server to host the frontend and route API requests to the Python API service.

### Cron

Set up a cron job to execute `update.py` (using Python) every five minutes.

The script outputs details of the update process to standard output, and details of errors to standard error. An error with an individual data source does not abort the rest of the update process.

### Fonts

The CSS refers to `proza-light.woff2` and `proza-regular.woff2`. These are commercial fonts, so are not included in this repository. Licences for [Proza](http://bureauroffa.com/about-proza) can be purchased from [Bureau Roffa](http://bureauroffa.com/). Alternatively, the simplified free version [Proza Libre](http://bureauroffa.com/about-proza-libre) can be used instead.

### Cloudflare

National Grid: Live uses [Cloudflare](https://www.cloudflare.com/)’s content delivery network. Visit counts will be retrieved from Cloudflare if the `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ZONE_ID` environment variables are set to non-empty strings. The Cloudflare API token must be configured to provide Analytics Read access for the zone.

## Codebase structure

Python modules can be found in the `grid` directory. The [database module](grid/database.py) is responsible for all database access. The other modules are divided into three packages:

The [data](grid/data) package contains modules for reading data from the various data sources, as documented further below.

The [state](grid/state) package contains classes representing the data needed to output responses.

The [ui](grid/ui) package contains classes for UI-specific formatting, including favicon generation.

## Data sources

### [Elexon Insights Solution](https://bmrs.elexon.co.uk/)

This API, developed by Elexon, reports power generation connected to the national transmission network, interconnector imports and exports, and pricing.

Data is available in JSON format at 30-minute or 5-minute granularity.

Python modules: [generation](grid/data/generation.py), [pricing](grid/data/pricing.py)

### [National Energy System Operator Data Portal](https://www.neso.energy/data-portal)

This API, developed by the National Energy System Operator, estimates power generation from embedded solar and wind (generation connected to the local distribution network rather than the national transmission network).

Data is available in CSV format at 30-minute granularity. Estimates may be retrospectively updated.

Python module: [demand](grid/data/demand.py)

### [Carbon Intensity API](https://carbonintensity.org.uk/)

This API, developed by the National Energy System Operator and the University Of Oxford Department Of Computer Science, estimates the carbon intensity of electricity generation in grams of carbon dioxide per kilowatt-hour.

Data is available in JSON format at 30-minute granularity. Estimates may be retrospectively updated.

Python module: [emissions](grid/data/emissions.py)

## Future plans

Battery storage data isn’t yet shown. The Elexon Insights Solution only reports on discharging of battery storage systems. Without charging being reported, this would lead to double-counting of generation.

I’m not currently planning any other major changes. I believe it’s better for a project like this to have a limited scope and a concise interface serving the general public than to attempt to offer specialised analysis for energy industry experts.
