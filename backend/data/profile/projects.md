# Notable Projects

## PDFPal
https://github.com/aaranguha/PDFPal

**Description**  
PDFPal is a web application that enables users to query dense PDF documents using a Retrieval-Augmented Generation (RAG) workflow. It combines semantic retrieval with LLM-based responses to make document exploration faster and more interactive.

**Key Contributions**
- Built a React-based chat interface for asking questions about PDF content.
- Implemented a Python backend using LangChain / transformer tooling for retrieval + generation.
- Designed the ingestion flow for PDF parsing, chunking, embedding, and context retrieval.

**Tech Stack:** React, TypeScript, Python, LangChain, Transformers, Vector search  
**Outcome:** Natural-language Q&A over long PDFs, reducing time spent manually searching and skimming.

---

## NBA_Chipotle_Getter_6000 (Chipotle_Getter_6000)
https://github.com/aaranguha/Chipotle_Getter_6000

**Description**  
An automation tool built during the 2023 NBA Finals that monitored @ChipotleTweets (via TweetDeck), extracted promo codes in real time, and automatically sent the code to a designated number via iMessage.

**Key Contributions**
- Automated monitoring of dynamic Twitter content using Selenium.
- Extracted promo codes from posts as soon as they appeared.
- Automatically forwarded codes via iMessage to minimize delay.

**Tech Stack:** Python, Selenium  
**Outcome:** End-to-end automated code detection and delivery in real time.

---

## Touchdown.Life
https://github.com/aaranguha/Touchdown.Life  
Live site: https://touchdown.life/

**Description**  
Touchdown.Life is a Wordle-like game for football fans powered by scraped NFL roster history (1996–present). Users guess players using structured roster data and game logic.

**Key Contributions**
- Webscraped and normalized NFL roster data across seasons.
- Built puzzle/game logic around real-world player data.
- Implemented a lightweight frontend for interactive gameplay.

**Tech Stack:** Python, HTML, JavaScript  
**Outcome:** A data-driven sports game combining web scraping, structured data, and game mechanics.

---

## UCSC-Dining-Hall-Texts
https://github.com/aaranguha/UCSC-Dining-Hall-Texts

**Description**  
A Python automation script that scrapes UC Santa Cruz dining hall menus and sends formatted meal information via SMS using Twilio. The script parses meal sections (Breakfast, Lunch, Dinner, Late Night), groups items by category, and sends messages to a contact list.

**Key Contributions**
- Scraped menu HTML using `requests` + BeautifulSoup and extracted meal/category/recipe structure from table rows.
- Organized scraped content into a nested dictionary format: `menu[meal][category] -> [recipes]`.
- Built message formatters (e.g., `lunch()`, `dinner()`) to generate readable SMS bodies.
- Integrated Twilio `Client` to send texts to multiple recipients.
- Extended the approach to support a second campus dining source with similar parsing and SMS delivery logic.

**Tech Stack:** Python, requests, BeautifulSoup, Twilio API  
**Outcome:** Automated menu delivery to friends via SMS without needing to check dining hall websites.

---

## Covid-Cases-Tracker
https://github.com/aaranguha/Covid-Cases-Tracker

**Description**  
A scheduled Python script that scrapes California’s COVID dashboard and sends a daily SMS summary of new cases and vaccination numbers.

**Key Contributions**
- Scraped the state dashboard HTML and extracted key metrics using BeautifulSoup selectors.
- Used `schedule` to run the job automatically every day at 10:00 AM.
- Sent formatted daily SMS updates using Twilio messaging.

**Tech Stack:** Python, requests, BeautifulSoup, schedule, Twilio API  
**Outcome:** Daily automated public health updates delivered via SMS.

---

## CologneGetter3000
https://github.com/aaranguha/CologneGetter3000

**Description**  
A Python email automation script that reads a company/email list from a file and sends a personalized “tester request” email to each recipient using Gmail SMTP.

**Key Contributions**
- Parsed `company_email_list.txt` into structured `(company, email)` pairs.
- Generated a templated email message with company-level personalization.
- Used `smtplib` with TLS to authenticate and send emails in bulk.

**Tech Stack:** Python, smtplib  
**Outcome:** Automated a repetitive outreach workflow into a single run script.

---

## Spotify-Playlist-Converter
https://github.com/aaranguha/Spotify-Playlist-Converter

**Description**  
A Python tool that exports a playlist from Apple Music and recreates it on Spotify using the Spotify API. The script extracts track data from Apple Music via AppleScript, reformats it, creates a Spotify playlist (if needed), then searches and adds songs programmatically.

**Key Contributions**
- Exported Apple Music playlist track metadata using AppleScript executed via `osascript`.
- Cleaned and reformatted song strings (e.g., `"Song - Artist"`) for reliable Spotify search.
- Used Spotipy (Spotify OAuth) to create playlists and add tracks via the Spotify API.
- Implemented progress tracking and rate-limit friendly delays while adding tracks.

**Tech Stack:** Python, AppleScript (osascript), Spotipy / Spotify API  
**Outcome:** Automated cross-platform playlist migration (Apple Music → Spotify).

---

## Technology Summary

- **Languages:** Python, TypeScript, JavaScript, HTML/CSS
- **Automation & Scraping:** requests, BeautifulSoup, Selenium, schedule
- **APIs & Integrations:** Twilio, Spotify API (Spotipy), SMTP (Gmail)
- **LLM / RAG:** LangChain, Transformers, vector search
