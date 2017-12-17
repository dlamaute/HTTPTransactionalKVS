Transactional HTTP Key-Value Store

The request handler (in starry_hw.py) is a subclass of Python's standard BaseHTTPRequestHandler. While there are libraries out there that have more concise ways to implement an HTTP Key-Value Store, I'd never learned how to originally do it in Python, and thus I decided to learn it by only using the Python standard classes available.

The request handler has a few properties:
1. kvs, a python dictionary that keeps a temporary copy of the key-value store.
2. kvs_file, the actual file where the real key-value store is kept.
3. commit_queue, the python list of key-value pairs to be committed.

The actual request handler has 5 methods--
1. do_GET:
	Responds to GET calls. It opens the kvs_file, loads the data to the kvs dictionary, and checks if the item to GET (parsed from the url) is already in the key-value store. If so, it sends a 200 and sends the user a string of the key_value pair as well. Else, it sends a 404.

2. do_post_set:
	All lowercase to differentiate from valid BaseHTTPRequestHandler functions, this function is just internal. It reads the data being posted, and checks if it is valid JSON and exactly one key-value pair.If not, it simply returns since there are no currently allotted errors for these issues. However, it does print a short summary of the problem as a placeholder for throwing an error. Otherwise, if the JSON is valid, it checks the KVS (by loading the kvs_file contents into the dictionary kvs) for the key provided in the data to see if the KVS has a valid entry for it. If so, it sends a 200, else, it sends a 201. It then adds the value to commit_queue, and sends the submitted key_value_pair to the user as confirmation.

3. do_post_commit:
	All lowercase to differentiate from valid BaseHTTPRequestHandler functions, this function is just internal. This first loads the kvs_file contents into the kvs dictionary to make sure it's up to date. It then goes through every key-value pair in commit_queue. If the key is in the KVS and its value is "NONE", that means the key was set to be deleted, and it gets deleted from the dictionary kvs. Any other key-value pair is simply added to kvs. After all the pairs are added from the commit_queue, it is emptied, and the dictionary kvs is used to overwrite kvs_file's contents. It then sends a 204.

4. do_POST:
	Calls either do_post_set or do_post_commit depending on the url from the POST call. If the user does not specify "/set" or "/commit", the function prints out the error (as a placeholder for throwing an error)and returns.

5. do_DELETE:
	Reads the key to delete and associates it with the value "NONE", which I used as the indicator for a key's deletion. (None as an actual keyword fails to work because it automatically deletes the key, thus defeating the purpose if this key-value pair is to be added to a commit_queue.) Sends a 200.

Notes for improvement:
1. abort functions would improve this db, as a practical matter, since there's currently no way to undo a commit
2. asserting keys are valid strings or something and needing to sanitize inputs is generally good
3. There are some parts of the code that work because a dictionary is assumed or forced to have length 1, but there are better ways to design that (and given more time, I would have changed more specific things like this.)
4. For a system more constrained on memory, i wouldn't actually store many of these variables that I made mostly for readability purposes.
5. Should switch from print statements for certain errors to throwing real errors (empty/invalid JSON, trying to POST too many keys at once...)
6. Ideally as a system design parameter itself, it should handle sending headers internally rather than relying on the user, since this is a json-only system, which is why I included it in my functions.
7. Not sure how atomic POST /commit is in its current implementation/documentation. Each commit should probably be individual rather than running a batch all with one HTTP return code.