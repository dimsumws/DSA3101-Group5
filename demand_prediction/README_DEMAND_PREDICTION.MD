# Demand Prediction regarding Average Daily Wait Time at Universal Studios Singapore

## Overview:
As part of Business Question 6, we would like to explore the possibility of building a demand prediction model using historical data and external factors 
such as Weather Data and Events to predict the average daily wait time for attractions at Universal Studios Singapore (USS). Taking into account the 
exploration of external factors effect on USS Attendance and the guest experience as a whole, we would like to channel this newfound knowledge to explore 
using the effects of factors into building a demand prediction model. From work done under [External Factors Analysis](external_factors_analysis/README.md), it was found that elements such as Rain Forecast, Rainfal do play a role in contributing influencing wait times.

Additionally, Events may not necessarily influence wait times whereas nationwide Holidays such as Public Holidays or School Holidays can have a more 
significant impact on influencing general waiting time. We thus would like to investigate demand predicition modelling and then branching a similar 
methodology to demand prediction for general attendance counts at USS on a daily basis, as well as that for individual rides.

## Data
Before beginning with building demand prediction modelling for wait times, data would have to be collected.

### Weather:
Weather data was primarily collected from reliable government sources such as [[1] data.gov.sg](https://data.gov.sg/) and [[2]Meteorological Service Singapore](https://www.weather.gov.sg/home/). Data was broad and was filtered down to included the weather readings specific to Sentosa Island where USS is situated at. Weather data is particularly interesting to explore on how it could affect Demand and Wait Times in USS as on top of the work and thorough analysis in[[3] External Factors Analysis](external_factors_analysis/README.md), weather conditions can affect how people perceive on the worthiness of visting theme parks or going for rides, and hence affecting wait times in Theme Parks  

Data pulling through [[1] data.gov.sg](https://data.gov.sg/) was mostly done through downloading tabular data stored in CSV files or making API calls. 
Generally, the output of making API calls comes in a large JSON file which contains readings for multiple weather stations in Singapore. In the case of 
Sentosa, it had a Station ID of **S60**. Since each API call only calls a specific day only, and prcoessing has to be done to extract the wanted value 
nested within the JSON Output, as such, python code was done to iterate through a date range, extract necessary values, process them if necessary and store 
them in Tabular CSV form for later modelling use. The [Python Scripts can be found here](data/Meteorological/code_solutions). The data is then stored in 
[final_data](data/Meteorological/datasets/final_data)

For data generated from [[2] Meteorological Service Singapore](https://www.weather.gov.sg/home/), monthly data for Sentosa Island can be downloaded a s a CSV file manually from the aforementioned website. 2016 to 2025 February data was downloaded from the website and the individual months CSV files is stored 
[here](data/Meteorological/datasets/raw_data/daily_data_sentosa/sentosa_data.zip). The python code to merge the more than 70 CSV files and cleaning can be 
found [here](data/Meteorological/code_solutions/merge_sentosa_data.py)  

### Events
Next, external factors were also included into the demand prediction modelling quest, more specifically exploring Events in Singapore, Public Holidays, and 
School Holidays
### Events
Events data was then represented and prepared in a tabular data form so that it can be used for modelling. From 2016 and 2025 February, every single date 
was included as a row and a **'is_event'** flag is included. The values under this variable is **1** if that day has an Event and **0** if otherwise. The 
definition of an Event to be included and classify the **is_event** variable to be 1 had to be laid out as there are multiple events in general in 
Singapore, be it big or small. 

As such, metrics can be used to deem whether an Event should be utilised. For Example, Events had to be siginificant and grand enough to possibly impact
attendance counts to USS. As such, the most convenient measure of how big an event would be is the event's attendance. A threshold of **50,000** (50,000
cumulated from all the dates of the Events )was set to filter off events that are big enough to possibily affect the USS Attendance. Such events could
include **Formula 1 Singapore Grand Prix** which saw an attendance of *269,072* people across the Race Weekend[[4] (Singapore Grand Prix, 2024)](https:/singaporegp.sg/en/news/2024/15th-edition-of-the-formula-1/). Other siginifcant events in Singapore that occured in 2024 were **Coldplay's Adventure of a Lifetime Singapore Tour** and **Taylor Swift's Eras Tour** which saw a total attendance of over **200,000** and over **300,000** respectively across each Artists' 
tour dates in Singapore. [[5] (Straits Times, 2024)](https://www.straitstimes.com/singapore/consumer/top-tier-concerts-helped-draw-over-a-million-visitors-to-sports-hub-in-first-3-months-of-2024)

These events alone can influence attendance at Universal Studios Singapore as being high-profile, and "once-in-a-lifetime" events, 
people may opt out a day of Universal Studios Singapore in favour of these events. Additionally, not only could these events decrease attendance, it also 
could increase attendance to Universal Studios. Events of such a big scale can bring in tourists and foreigners from neighbouring countries and during 
their stay in Singapore, USS may possibily be a part of their itineraries when coming to Singapore alongside the Events they attend. For example, around 
half of the Taylor Swift concertgoers possibily came from overseas. [[6] Source](https://www.channelnewsasia.com/singapore/taylor-swift-coldplay-concerts-singapore-economy-mas-4292951)

When processing the data, Events were found and filtered from multiple online sources such as [[7] Wikipedia](https://en.wikipedia.org/wiki/Main_Page), [[8] Visit Singapore](https://www.visitsingapore.com/whats-happening/all-happenings/) and [[9] The Straits Times](https://www.straitstimes.com/singapore/strong-slate-of-mice-events-around-singapore-grand-prix-period-despite-expected-fall-in-race-attendance?utm_source=chatgpt.com) to attain attendance figures and dates ranges of events.

### School & Public Holidays
School Holidays and Public Holiday data was also attained and stored in a similar fashion to the procedure with that of Event Data.
These days are external factors that can influence USS attendance and wait times as during these days, more people have the opportunity to visit USS and
enjoy the theme park in all its glory as these days allow Workers, Students and Families alike to take the day off from work or school.

Data was taken from [[10] MOE](https://www.moe.gov.sg/news/press-releases/20221019-school-terms-and-holidays-for-2023) and [[11] data.gov.sg](https://data.gov.sg/datasets?query=public+holiday&page=1&resultId=691), since websites provide data on a yearly basis, the data had to be retrieved from each years respective range to cover a total date range from **2016 to 2025**. Python Code to merge the data and scrape data can be found in [Holidays](data/Events/Holidays/code_solutions), the data is then processed and merged, and the final data is stored in [Holidays/datasets](data/Events/Holidays/datasets).

More specification can be found [here](data/Events/Holidays/README_HOLIDAYS.md)



