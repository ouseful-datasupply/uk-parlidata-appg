# uk-parlidata-appg
Scrape UK Parliament APPG (All Party Parliamentary Group) Details

You can query the latest copy of the db (Oct 2021) here: [https://ouseful-datasupply.github.io/uk-parlidata-appg/](https://ouseful-datasupply.github.io/uk-parlidata-appg/)

```
Usage:

appg

```

Downloads data to `appg_data.db` SQLIte3 database by default.

If you have it installed, you can then view the database using [`datasette`](https://github.com/simonw/datasette): `datasette serve appg_data.db`

Example: [https://appg.herokuapp.com/](https://appg.herokuapp.com/)

