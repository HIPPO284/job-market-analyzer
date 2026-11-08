# Job Market Analyzer

Find jobs and internships through your skills, with optional filters, ranked results, employer application links, and market statistics.

## How to Use

1. Enter a skill in English, wait for suggestions, and click one to select it. At least one selected skill is required; typing alone does not count.
2. Optionally click the map and wait a few seconds, then select a returned location.
3. Add optional filters: minimum annual salary and currency, workplace type, education level, and employment type.
4. Submit the form and view up to 100 ranked results. The application links will lead to employer websites.
5. Open Job Market Insights to explore periodically refreshed statistics.

## Technology

- Application: Python, Flask, Jinja, MySQL, HTML, CSS, JavaScript, Leaflet.
- Data processing: Requests, Beautiful Soup, Matplotlib, Ollama (runs a local AI model to extract job information), Pydantic (defines and validates structured data).
- Deployment: Azure, Ubuntu, Gunicorn, Nginx, systemd, Certbot.
- Windows: pywebview, PyInstaller, NSIS.
- Version control: Git and GitHub.

AI assists with data preparation; search ranking uses SQL-based rules.

## Project Links

[Web application](https://job-market-analyzer-web-hippo.swedencentral.cloudapp.azure.com/)

[Windows download](https://wukuncheng.itch.io/job-market-analyzer)

## Project Status

An early prototype currently in its first round of user testing. Skill and employer coverage is limited, some listings or links may be outdated, and the search experience is being improved.

## License

Project code is licensed under the MIT terms in [LICENSE](LICENSE).

Hippo artwork and icons are excluded from MIT and covered by the separate [Artwork License](desktop_client/ARTWORK_LICENSE.txt).

Third-party components remain subject to their respective licenses.
