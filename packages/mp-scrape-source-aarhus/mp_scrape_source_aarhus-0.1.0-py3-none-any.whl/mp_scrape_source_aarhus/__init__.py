# SPDX-FileCopyrightText: 2025 Free Software Foundation Europe e.V. <mp-scrape@fsfe.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mp_scrape_core import DataSource, ModuleDescription, ModuleArgument, ModuleDefinition, ModuleMaintainer
from playwright.async_api import async_playwright
import pandas as pd

import subprocess
import logging

class AarhusSource(DataSource):
    def __init__(self, display_browser: bool = False, url: str = "https://aarhus.dk/demokrati/politik/byraadet/byraadets-medlemmer?tags="):
        """
        Retrieve the information of members from the Aarhus City Council.

        :param bool display_browser: (Display browser) When enabled, a browser window is opened displaying the actions being performed.
        :param str url: (URL) URL from where the data is extracted.
        """
        self.display_browser = display_browser
        self.url = url

    @staticmethod
    def metadata() -> ModuleDefinition:
        return ModuleDefinition({
            "name": "Aarhus",
            "identifier": "aarhus",
            "description": ModuleDescription.from_init(AarhusSource.__init__),
            "arguments": ModuleArgument.list_from_init(AarhusSource.__init__),
            "maintainers": [
                ModuleMaintainer({
                    "name": "Free Software Foundation Europe",
                    "email": "mp-scrape@fsfe.org"
                }),
                ModuleMaintainer({
                    "name": "Sofía Aritz",
                    "email": "sofiaritz@fsfe.org"
                }),
            ],
        })
    
    async def fetch_data(self, logger: logging.Logger) -> pd.DataFrame:
        logger.warn("installing playwright browsers, if this fails try to run 'playwright install firefox --with-deps'")
        subprocess.run(["playwright", "install", "firefox"])

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=self.display_browser is False)

            page = await browser.new_page()
            await page.goto(self.url)
            councillors = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll(".card__person")).map(function (card) {
                    let email = Array.from(card.querySelectorAll("a")).filter(function (link) { return link.href.startsWith("mailto:") })[0].href.replace("mailto:", "")
                    let name  = card.querySelector("h3").innerText
                    let title = card.querySelector("p.subtitle").innerText
                    let party = card.querySelector("div.tag > span").innerText
                    return { "Email": email, "Full Name": name, "Title": title, "Party": party }
                })
            }""")

        return pd.DataFrame.from_dict(councillors)