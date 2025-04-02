## EventData Subfolder
*EventsData* subfolder under *Events* contains TWO different csv files. One is **supplementary_event_data_2016_2025.csv** which is a CSV file that contains every single individual day from Start of 2016 to February 2025. Under each day, there is a variable flag named *is_event* where if there is an event on that day that can affect USS attendance, it has a flag of **1** and *0* if there is no event on that day. There are also other variables included to further categorize the type of event it is (e.g. Concert Event, Social Event and etc.)

Events that are selected and chosen to be included are those that have **>50000** Attendance in total attendance, be it a single day or multi-day event. Such events can include the **Singapore Airlines Formula 1 Singapore Grand Prix** , and **National Day Parade**, other metrics to classify events include the impact these events can have on drawing tourists into visting Singapore, just for these events. For example, **Coldplay and Taylor Swift concerts** in 2024 not only draws attendance from Singaporeans, but from those in neighbouring countries as well.

Other events could include events that happen in Sentosa Island itself, with people perhaps visting **Universal Studios Singapore** before, during or after the event. Some of these events can include **Zoukout**

**2025_remainder_supplementary_event.csv** includes the data likewise in the structure of **supplementary_event_data_2016_2025.csv**, but rather for the remaining days of 2025 that were not included in **supplementary_event_data_2016_2025.csv**.

Sources