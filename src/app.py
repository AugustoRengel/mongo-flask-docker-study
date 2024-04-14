import json
from flask import Flask, jsonify, request
from pymongo import MongoClient 
from bson import ObjectId, json_util

app = Flask(__name__) 

client = MongoClient(
    host='host_mongodb', 
    port=27017, 
    username='root', 
    password='pass', 
    authSource="admin"
    ) 
db = client.my_mongo_db 
collection = db.my_collection 

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/') 
def ping_api(): 
    return "API online"

@app.get('/v1/items')
def get_items():
    items_list = []
    items = collection.find({})
    for item in items:
        items_list.append(parse_json(item))
    return {
        "data": items_list
    }, 200

@app.post('/v1/item') 
def post_item(): 
    item_data = request.json
    result = collection.insert_one(item_data) 

    if result.inserted_id:
        return jsonify({'message': 'Post success'}), 201
    else:
        return jsonify({'error': 'Failet to post'}), 500
    
@app.get("/v1/item/<item_id>/")
def get_item(item_id):
    query={
        "_id": ObjectId(item_id)
    }
    item = collection.find_one(query)

    if not item:
        return {
            "message":"Item not found"
        }, 404

    return {
        "data":parse_json(item)
    }, 200

@app.delete("/v1/item/<item_id>/")
def delete_item(item_id):
    query={
        "_id": ObjectId(item_id)
    }
    result = collection.delete_one(query)
    
    if not result.deleted_count:
        return {
            "message":"Failed to delete"
        }, 500
    
    return {"message":"Delete success"}, 200

@app.put("/v1/item/<item_id>/")
def update_item(item_id):
    query={
        "_id": ObjectId(item_id)
    }
    content={ "$set": dict(request.json) }
    result = collection.update_one(query, content)

    if not result.matched_count:
        return {
            "message":"Failed to update. Record not found"
        }, 404
    
    if not result.modified_count:
        return {
            "message":"No changes applied"
        }, 500
    
    return {"message":"Update success"}, 200
  
if __name__ == '__main__': 
    app.run(host='0.0.0.0', debug=True) 