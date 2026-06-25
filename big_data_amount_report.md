Using seen.py script I have loaded massive amount of data into my app. Most populated are threads and thread messages, with 10^5 threads 10^6 messages (around 10 messages per thread in average).

I implemented paging for threads, and (private) skills page. I didn't implement paging for messages in threads, as I suppose that type of logic would be unnatural for a thread,and I wanted user to easily scroll through the messages. Page size is common for all paging systems and dependent on the one global variable page_size in the app.py.

I calculate the time it takes for the each view function to run, using @app.before_request and @app.after_request. On the threads url it takes around  2.51 s each time, and around 5 s in worst case. '''Using CREATE INDEX idx_thread_messages ON messages (thread_id);''' I sped up response time from /threads to be just around 0.05 - 0.1s. The sql command added to the schema.sql.
Even when I changed seed.py parameters to 10^6 for threads and 10^7 for messages, resulting in 1000000 threads, the response time from /threads is around 0.07.
