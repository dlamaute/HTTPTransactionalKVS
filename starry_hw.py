import http.server
import json
    
class HTTPTransactionalRequestHandler(http.server.BaseHTTPRequestHandler):

    commit_queue = []
    kvs = {}

    #creates kvs file if it doesn't already exist
    kvs_file = open("kvs.json", "w")
    kvs_file.close()
    
    #GET
    def do_GET(self):
        #GET self.path
        self.kvs_file = open("kvs.json", "r")
        try:
           self.kvs = json.load(self.kvs_file)
        except json.decoder.JSONDecodeError:
           self.kvs = {}
        try:
            result = self.kvs[self.path[1:]]
        except KeyError:
            result = None
        
        #if key in there, return key value pair, code 200
        if result is not None: 
            self.send_response(200)
            write_out = "{\"" + self.path[1:] + "\" : \"" + result + "\"}"
            self.wfile.write(write_out.encode())
            
        #key is not in there, return a 404
        else:
            self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.kvs_file.close()
        return

    
        
    #POST /set
    #because of how POST /commit is implemented, should prevent the user from entering "NONE" as a value in a key-val pair
    def do_post_set(self):
        post_len = int(self.headers["Content-Length"])
        post_data_str = self.rfile.read(post_len)
        try:
            post_data = json.loads(post_data_str)
        except json.decoder.JSONDecodeError:
            print("no valid json provided to POST")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            return
        
        if len(post_data) != 1:
            #cannot set more than 1 key-val pair at a time, also cannot set empty json
            print("post data not of length 1, exiting")
            return
        else:
            self.kvs_file = open("kvs.json", "r")
            try:
               self.kvs = json.load(self.kvs_file)
            except json.decoder.JSONDecodeError:
               self.kvs = {}
            
            #this only works because post_data is guaranteed to be a dictionary of length 1
            try:
                result = self.kvs[next(iter(post_data))]
            except KeyError:
                result = None
                
            #if the given dictionary's key is there, will send a 200
            if result is not None:
                self.send_response(200)
                
            #if not there, will send a 201
            else:
                self.send_response(201)
                
        self.commit_queue.append(post_data)
        self.wfile.write(json.dumps(post_data).encode())
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        return


    #POST /commit
    #currently not as ACID following as i'd like to account for theoretical multiple users
    def do_post_commit(self):
        self.kvs_file = open("kvs.json", "r")
        try:
           self.kvs = json.load(self.kvs_file)
        except json.decoder.JSONDecodeError:
           self.kvs = {}
        #post every kv pair in commit queue to the db
        for key_val_pair in self.commit_queue:
            #this only works because key_val_pair is *assumed* to be a dictionary of length 1
            key = next(iter(key_val_pair))
            val = key_val_pair[key]
            #obviously this doesnt work out for if the key's value is actually "NONE" but actually using None won't work
            if (val is "NONE") and (key in self.kvs):
                del self.kvs[key]
            else:
                self.kvs[key] = val

        #empty commit queue
        self.commit_queue = []

        #now take the local kvs and overwrite the previous stored one
        self.kvs_file = open("kvs.json", "w")
        json.dump(self.kvs, self.kvs_file)
            
        #return a 204
        self.send_response(204)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.kvs_file.close()
        return



    #POST
    def do_POST(self):
        if self.path == "/set":
            self.do_post_set()
        elif self.path == "/commit":
            self.do_post_commit()
        else:
            #not a valid POST call, throw error/notify user ideally
            print("not a valid POST call, either call POST /set or POST /commit")
        return



    #DELETE /set
    def do_DELETE(self):
        #get key to delete from kvs
        key_len = int(self.headers["Content-Length"])
        key_str = self.rfile.read(key_len).decode("utf-8", "ignore")

        self.commit_queue.append({key_str : "NONE"})

        self.send_response(200)
        self.end_headers()
        return
