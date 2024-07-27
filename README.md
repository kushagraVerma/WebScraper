<h1>Webscraper v4</h1>
Webscraping application made in Python to process online marketplace data for different products on various platforms<br>
Uses Selenium and Chrome driver to open webpages in a headless (invisible) browser and access their contents<br>
Currently scrapable: Amazon India, Flipkart, BigBasket<br>
<h3>USAGE</h3>
<h4>Setup</h4>
Required on your system:<br>
<ul>
  <li>Python (added to PATH): Install from https://www.python.org/downloads/ and add to PATH variable</li>
  <li>Chrome: Install from https://www.google.com/intl/en_us/chrome/</li>
  <li>Chrome Driver: Download (same version as Chrome!) from https://chromedriver.chromium.org/downloads (versions <= 114) or https://googlechromelabs.github.io/chrome-for-testing (versions >= 115)</li>
  <li>Python modules (selenium and tqdm): Run command <code>pip install -r path/to/WebScraper/requirements.txt</code> (see also: Updating)</li>
</ul>
Edit chrome_driver_path in consts.txt according to your system<br>
<h4>Running</h4>
Windows users can quickly run by clicking on RUN.bat<br>
Otherwise, run commands <code>cd path/to/WebScraper</code> and <code>python main.py</code><br>
<h4>Updating</h4>
If cloned with Git, Windows users can use UPDATE.bat to pull the latest version while preserving consts.txt<br>
Otherwise, run commands <code>cd path/to/WebScraper</code> and <code>python updater.py</code><br>
This will ask you if you would like to update Python packages as well (note that this is a time-taking process)
<h4>Notes</h4>
Selenium handshake failure errors can mostly be ignored<br><br>
