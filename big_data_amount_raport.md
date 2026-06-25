Usign seen.py script I have loaded massive amount of data into my app. Most poluted are threads and thread messages, with 10^5 threads 10^6 messages (around 10 messages per thread in average).

I implemented paging for threads, and (private) skills page. I didn't implement paging for messages in threads, as I suppose that type of logic would be unnatural for a thread,and I wanted user to easily scroll through the messages. Page size is common for all paging systems and dependent on the one global variable page_size in the app.py.

I calculate the time it takes for the each view function to run, using @app.before_request and @app.after_request. On the threads url it takes around  2.51 s each time, and arounf 5 s in worst case. '''Using CREATE INDEX idx_thread_messages ON messages (thread_id);''' I sped up response time from /threads to just
