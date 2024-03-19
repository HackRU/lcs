from src.util import coll

def get_all_points(event, context):
    
    # get house collection
    houses = coll('houses')

    data = houses.find({})

    results = {
        "status": 200, 
        "houses": {}
    }

    for doc in data:
        results['houses'][doc['name']] = doc['points']

    return results